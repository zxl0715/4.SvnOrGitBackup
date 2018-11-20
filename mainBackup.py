import multiprocessing
import os
import shutil
import time
import GitHandler
import SvnHandler
import configHandler
import loggingHandler
from APSchedulerHandler import JobManager
# 拉取代码
import FileHandler
from MyTickScheduler import *

from zipObj import ZipObj


class Worker(object):
    @classmethod
    def backup_svn_git(self):
        '''使用多进程，拉取代码'''
        # 获取svn和git本地仓库路径
        paths = configHandler.get_svn_or_git_path()
        # 获取本机cpu数量
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_cores)
        for args in paths:
            '''使用多进程执行'''
            # pool = multiprocessing.Process(target=pull_code, args=(svnOrGit,path,))
            pool.apply_async(self.pull_code, args=(args['type'], args['path'], args['MappingFilePath']))
            loggingHandler.logger.info('启动多进程拉取代码 {0} 库任务，路径{1}！'.format(args['type'], args['path']))
        pool.close()
        pool.join()
        loggingHandler.logger.info('多进程任务执行代码库同步至本地库完成,共计 {} 个任务!'.format(len(paths)))

    @classmethod
    def pull_code(self, svn_or_git='svn', path='', mapping_file_path=None):
        '''拉取代码'''
        status = False
        if os.path.exists(path) is False:
            loggingHandler.logger.warning('{0} 路径{1}不存在。'.format(svn_or_git, path))
            return status
        try:
            # todo
            if svn_or_git == 'svn':
                # todo
                status = SvnHandler.pullAndMapping(path, mapping_file_path)
            else:
                # todo
                status = GitHandler.pullAndMapping(path, mapping_file_path)
                pass
        except Exception as e:
            loggingHandler.logger.exception('错误代码{0}：{1}拉取路径为：{2}代码库出错，错误信息{3}'.format(1001, svn_or_git, path, e))

        if status:
            loggingHandler.logger.info('{0} 库拉取代码成功，路径{1}！'.format(svn_or_git, path))
        else:
            loggingHandler.logger.info('{0} 库拉取代码失败，路径{1}！'.format(svn_or_git, path))
        return status

    @classmethod
    def backup_file_svn(self):
        '''备份文件到svn（备份的svn）'''
        file_handler = FileHandler.FileHandler()
        backup_rep = file_handler.getBackupRepository()
        if len(backup_rep) > 0:
            try:
                loggingHandler.logger.info('开始移动备份工程项目文件至本地备份服务器！')
                file_handler.backupRepository(backup_rep)
                loggingHandler.logger.info('完成移动备份工程项目文件至本地备份服务器！')

                loggingHandler.logger.info('开始本地SVN备份服务器内容提交！')
                file_handler.svn_commit(backup_rep)
                loggingHandler.logger.info('完成本地SVN备份服务器内容提交！')

            except (KeyboardInterrupt, SystemExit) as e:
                loggingHandler.logger.exception('备份文件到svn出现异常！')

    @classmethod
    def get_detp_name(self, code):
        '''获取部门名称'''
        dept_info = configHandler.get_department()
        for dept in dept_info:
            if code == dept[0]:
                return dept[1]
        return None

    @classmethod
    def make_compressed_file(self):
        '''执行文件压缩'''
        startswith = '研发成果'
        pwd = configHandler.get_zip_pwd()
        dst = configHandler.get_backup_path()
        target = configHandler.get_target_path()
        parent_path = os.path.dirname(dst)
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        zip_path = r'{}\{}-{}'.format(target, startswith, date)
        # 作为临时文件（后面做变更成正式）
        zip_path_temp = zip_path + '_'
        if os.path.exists(dst) is False:
            loggingHandler.logger.warning('代码备份路径{}不存在。'.format(dst))
            return False
        if os.path.exists(target):
            # 归档压缩路径
            try:
                for dir in os.listdir(target):
                    if dir.startswith(startswith):
                        shutil.rmtree('{}\{}'.format(target, dir))
            except Exception as e:
                loggingHandler.logger.exception('5001  删除历史归档文件失败，请检查文件是否被占用或无权限访问！')

        # 创建目标文件(下划线)
        if os.path.exists(zip_path_temp) is False:
            os.makedirs(zip_path_temp)

        _dir = ''
        _dep_code = ''
        _dep_name = ''
        _index = 0
        _zip_path = ''
        # 按部门、工程项目打包压缩
        for dir in os.listdir(dst):
            _index = dir.find("-")
            if not os.path.isdir('{}\{}'.format(dst, dir)):
                continue
            if dir.find(".svn") >= 0:
                continue

            if _index > 0:
                _dep_code = dir[:_index]
                _dep_name = self.get_detp_name(_dep_code)
            # 压缩到 的目标文件路径
            _dir = r'{}\{}'.format(zip_path_temp, _dep_name)
            if os.path.exists(_dir) is False:
                os.makedirs(_dir)
            # 对各部门工程项目进行工程说明
            with open('{}\{}'.format(dst, '项目备份保存清单.txt'), encoding="UTF-8-sig") as f:
                for line in f.readlines():
                    if line.find(dir) == 0:
                        # str = line.split(':')
                        with open('{}\工程说明.txt'.format(_dir), 'a+', encoding="UTF-8-sig") as f_child:
                            _index = line.find("-")
                            if _index > 0 and (_index + 1) <= len(line):
                                line = line[_index + 1:]
                            f_child.writelines(line)

                        break
            # _dir = r'{}\{}'.format(_dir, os.path.basename(dir))
            # 移除部门简称前缀
            _zip_path = r'{}\{}'.format(dst, dir)
            if _index > 0 and (_index + 1) <= len(dir):
                filename = dir[_index + 1:]
            # 进行打包加密压缩
            zipo = ZipObj(_zip_path, pwd)
            zipo.enCrypt(target_path=_dir, file_name=filename, delete_source=False)
            loggingHandler.logger.info('打包工程文件：{} 项目归属部门 {} 成功！'.format(filename.rjust(20), _dep_name.rjust(10)))
        # 重命名目标文件路径（作为用为，文件在生成中尾部为下划线结尾，全部生成完成后去除下划线）
        os.rename(zip_path_temp, zip_path)

    @classmethod
    def backup_code(self, is_zip=False):
        loggingHandler.logger.info('启动任务{}'.format(os.linesep))

        try:
            # 拉取代码
            loggingHandler.logger.debug('步骤{}：{} {}。'.format(1, 'backup_svn_git', '开始'))
            # todo
            self.backup_svn_git()
            loggingHandler.logger.debug('步骤{}：{} {}。{}'.format(1, 'backup_svn_git', '完成', os.linesep))

            # 备份文件至svn备份服务器
            loggingHandler.logger.debug('步骤{}：{} {}。'.format(2, 'backup_file_svn', '开始'))
            # todo
            self.backup_file_svn()
            loggingHandler.logger.debug('步骤{}：{} {}。{}'.format(2, 'backup_file_svn', '完成', os.linesep))

            # 是否启用打包归档
            if is_zip:
                # 按工程进行打包归档
                loggingHandler.logger.debug('步骤{}：{} {}。'.format(3, 'make_compressed_file', '开始'))
                self.make_compressed_file()
                loggingHandler.logger.debug('步骤{}：{} {}。{}'.format(3, 'make_compressed_file', '完成', os.linesep))
        except Exception as e:
            loggingHandler.logger.exception('备份任务出现异常')

        loggingHandler.logger.info('结束任务{}'.format(os.linesep))

    @classmethod
    def first_run(self):
        loggingHandler.logger.info(
            '{}————————————————————————————————————————————————{}'.format(os.linesep, os.linesep))
        loggingHandler.logger.info('启动程序运行！')

        # 初始化备份项目（待备工程清单文件）
        loggingHandler.logger.info('初始化备份项目（待备工程清单文件）！')
        SvnHandler.init_all()
        loggingHandler.logger.info('完成备份项目（待备工程清单文件）！')

        '''设置启动运行'''
        first_startup = configHandler.get_first_startup()
        if first_startup:
            loggingHandler.logger.info('程序启动一次运行开始！')
            self.backup_code(True)
            loggingHandler.logger.info('程序启动一次运行结束！{}'.format(os.linesep))

    @classmethod
    def main_job(self):
        # assert 2 == 1, '2不等于1'
        multiprocessing.freeze_support()  # 解决pyinstaller多进程打包问题
        self.first_run()
        # 执行定时任务
        job = MyTickScheduler()
        try:
            loggingHandler.logger.info('开始启动定时任务……')
            job.run()
        except Exception as e:
            job.stop()
            loggingHandler.logger.info('停止定时任务成功！')
        finally:
            job.stop()
        loggingHandler.logger.info('結束启动定时任务')
        loggingHandler.logger.info('结束程序运行！')


if __name__ == '__main__':
    Worker.main_job()
