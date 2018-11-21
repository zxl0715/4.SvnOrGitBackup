import collections
import os
import shutil
import socket
import time

import svn
from svn.common import CommonClient

import SvnHandler
import configHandler
import loggingHandler

_prject_info = collections.namedtuple(
    '_prject_info', [
        'dep_code',
        'path',
    ])


class FileHandler:
    """
    文件操作类
    """

    def getBackupRepository(self):
        """
        获取需要备份的工程项目，返回备份的工程项目路径
        :return:
        """
        paths = configHandler.get_svn_or_git_path()
        file_name = configHandler.get_backup_conf_file()
        backup_rep = []
        for path in paths:
            if path['path'].strip() == '':
                continue
            # 备份文件
            backup_file_path = os.path.join(path['path'], file_name)
            # 不存在备份文件的跳过（需要备份的库通过备份文件控制）
            if not os.path.isfile(backup_file_path):
                continue

            try:
                # 读取备份控制项目的备份文件清单
                with open(backup_file_path, 'r', encoding="UTF-8-sig")as f:
                    # loggingHandler.logger.info('文件编码为：{}！'.format(f.encoding))
                    for line in f.readlines():
                        if len(line.strip()) == 0:
                            continue
                        str_line = line.split(':')

                        project_info = self.get_project_info(paths, os.path.join(
                            os.path.dirname(path['path']), str_line[0]))
                        if project_info is not object:
                            _dep_code = project_info.dep_code
                            _path = project_info.path
                        else:
                            _dep_code = path['depCode']
                            _path = path['path']
                        BackupRepository = None
                        if path['type'] == 'svn':
                            BackupRepository = os.path.join('{}{}'.format(path['path'], '_mapping'), str_line[0])
                        else:
                            BackupRepository = os.path.join(os.path.dirname(path['path']), str_line[0])

                        # 软研中心工程名称格式：sp - 工程名称, 硬研中心工程名称格式：hp - 工程名称, 其他中心待定。
                        backup_rep.append({'depCode': _dep_code, 'RepositoryPath': _path,
                                           'BackupFilePath': backup_file_path, 'RepositoryName': str_line[0],
                                           'BackupRepository': BackupRepository})

            except Exception as e:
                loggingHandler.logger.exception('读取“项目备份保存清单”文件失败，路径为：{}'.format(backup_file_path))

        return backup_rep

    def get_project_info(self, svn_git_info, projcet_name):
        """
        获取项目信息，归属于那个部门
        :param svn_git_info:
        :param projcet_name:
        :return:
        """
        project_info = object
        for info in svn_git_info:
            if info['path'].lower() == projcet_name.lower():
                project_info = _prject_info(dep_code=info['depCode'], path=info['path'])
                break

        return project_info

    def jedgeProjectStandard(self, path, projectStandardlist):
        for fileOrFloder in projectStandardlist:
            if not os.path.exists('{}\{}'.format(path, fileOrFloder)):
                loggingHandler.logger.warning('违反【源文件存放规范】在{} 目录下 {} 文件或目录不存在，请检查！'.format(path, fileOrFloder))

    # backupPath=<class 'list'>: [['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '产销差系统', 'D:\\testSVN\\产销差系统'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '智慧水务赋能管控平台', 'D:\\testSVN\\智慧水务赋能管控平台'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '一个项目工程', 'D:\\testSVN\\一个项目工程']]
    def backupRepository(self, backup_path=[]):
        '''从源svn或git代码库复制到svn备份库的'''
        # svn备份仓库地址
        backup_server_path = configHandler.get_backup_path()
        # 目录校验
        project_standard = configHandler.get_project_standard()
        file_name = '项目备份保存清单.txt'
        inventory_file = '{}\{}'.format(backup_server_path, file_name)
        if os.path.exists(backup_server_path) is False:
            os.makedirs(backup_server_path)
            # loggingHandler.logger.warning('备份服务器svn路径不存在{}，请检查！', backup_server_path)

        # 清理svn备份仓库的项目备份保存清单文件
        if os.path.exists(inventory_file):
            os.remove(inventory_file)
        dirs = os.listdir(backup_server_path)
        for path in dirs:
            _path = os.path.join(backup_server_path, path)
            try:
                if os.path.isdir(_path):
                    # 排除隐藏文件夹。因为隐藏文件夹过多
                    if path[0] == '.':
                        pass
                    else:
                        # 添加非隐藏文件夹
                        shutil.rmtree(_path)  # 递归删除一个目录以及目录内的所有内容
                elif os.path.isfile(_path):
                    # 添加文件
                    os.remove(_path)
            except Exception as e:
                loggingHandler.logger.exception('清理svn备份仓库的项目备份保存清单文件失败！')

        for path in backup_path:

            if path['BackupFilePath'].strip() == '':
                continue
            file_path = path['BackupFilePath']
            # 检查根目录下是否有 项目备份保存清单.txt 文件
            if not os.path.isfile(file_path):
                loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！'.format(path['RepositoryPath'], file_path))
                continue
            # 判断待备份工程是否存在，存在进行规范校验
            if os.path.exists(path['BackupRepository']):
                try:
                    # 检查工程项目或单个项目 是否违反【源文件存放规范】
                    _rmFile = os.path.join(path['BackupRepository'], '目录说明.txt')
                    if os.path.exists(_rmFile) and path['BackupRepository'].find('_mapping') == -1:
                        with open(_rmFile, encoding="UTF-8-sig") as f:
                            for line in f.readlines():
                                str_line = line.split(':')
                                # 目录为工程项目
                                if line.find(':') > 0 & os.path.exists(
                                        '{}\{}'.format(path['BackupRepository'], str_line[0])):
                                    self.jedgeProjectStandard(os.path.join(path['BackupRepository'], str_line[0]),
                                                              project_standard)
                                else:  # 为单个项目
                                    self.jedgeProjectStandard(path['BackupRepository'], project_standard)
                except Exception as e:
                    loggingHandler.logger.exception(
                        '检查工程项目或单个项目 是否违法【源文件存放规范】，路径为：{0}'.format(path['BackupRepository']))
            try:
                # 从 项目备份保存清单文件里，读取需要备份的工程项目信息，并写入到 备份目录
                with open(file_path, encoding="UTF-8-sig") as f:
                    for line in f.readlines():
                        # print(line)
                        str_line = line.split(':')
                        if str_line[0] == path['RepositoryName']:
                            with open(inventory_file, mode='a+', encoding="UTF-8-sig") as f_child:
                                # f.writelines('{}-{}'.format(path['depCode'], line))
                                f_child.writelines(
                                    '{}-{}{}'.format(path['depCode'], line.strip('\n').strip('\n').strip('\r'), '\n'))

                            break

            except Exception as e:
                loggingHandler.logger.exception('从 项目备份保存清单文件里，读取需要备份的工程项目信息，路径为：{0}'.format(file_path))
            # 项目备份来源位置
            source_path = path['BackupRepository']
            # 项目备份目标位置（备份到目标文件夹）
            tager_path = '{}\{}-{}'.format(backup_server_path, path['depCode'],
                                           os.path.basename(path['BackupRepository']))

            if not os.path.exists(source_path):
                loggingHandler.logger.info('工程项目文件：{}不存在！'.format(source_path))
                continue
            # 文件移动的方案
            enable_plan = 1
            if enable_plan == 2:
                # 方案一
                # todo
                try:
                    if os.path.exists(tager_path):
                        shutil.rmtree(tager_path)  # 递归删除一个目录以及目录内的所有内容
                except Exception as e:
                    loggingHandler.logger.exception('删除文件失败，路径为：{0}'.format(tager_path))

                try:
                    # 进行复制（忽略.svn和.git文件夹）
                    shutil.copytree(source_path, tager_path,
                                    ignore=shutil.ignore_patterns('.svn', '.git', '.gitignore'))
                except Exception as e:
                    loggingHandler.logger.exception('从{} 复制到 {}失败！'.format(source_path, tager_path))
            else:

                # 方案二
                self.copyFiles(source_path, tager_path)

            # shutil.copytree(path[4], '{}\{}'.format(backup_server_path, os.path.basename(path[4])), symlinks=False,
            #                 ignore=shutil.ignore_patterns(".svn"), copy_function=shutil.copy2,
            #                 ignore_dangling_symlinks=True)

            # shutil.move(source_path, tager_path)

            loggingHandler.logger.info('移动备份工程项目文件{}至本地备份服务器{}！'.format(source_path, tager_path))

    def copyFiles(self, sourceDir, targetDir):
        '''从源svn或git目录，备份文件到备份的svn目录下'''
        if sourceDir.find(".svn") > 0 or sourceDir.find(".git") > 0 or sourceDir.find(".gitignore") > 0:
            return
        for file in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, file)
            targetFile = os.path.join(targetDir, file)
            if len(sourceFile) > 200:
                continue
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if os.path.isfile(sourceFile):
                if not os.path.exists(targetFile) or (
                        os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                    open(targetFile, "wb").write(open(sourceFile, "rb").read())
            if os.path.isdir(sourceFile):
                First_Directory = False
                self.copyFiles(sourceFile, targetFile)

    def svn_commit(self, backupPath=[]):
        '''备份的文件通过svn提交操作'''
        backup_server_path = configHandler.get_backup_path()
        if not os.path.exists(backup_server_path):
            loggingHandler.logger.warning('备份服务器svn路径不存在{0}，请检查！', backup_server_path)
        bb = 0
        try:
            loggingHandler.logger.debug('提交备份文件至备份服务器{0}'.format(backup_server_path))

            repo = svn.local.LocalClient(backup_server_path)
            un_file_paths = []
            rel_file_paths = []
            # 清除锁定
            loggingHandler.logger.debug('提交备份文件至备份服务器，动作 {0}'.format('清除锁定'))
            repo.cleanup()
            # 先进行更新
            loggingHandler.logger.debug('提交备份文件至备份服务器，动作 {0}'.format('进行更新'))
            repo.update()

            repo.add(' * --no-ignore --force ')
            repo.add('. --no-ignore --force ')
            loggingHandler.logger.debug('提交备份文件至备份服务器，动作 {0}'.format('检查文件状态'))
            chang_file = repo.status_new()
            for file in chang_file:
                rel_file_paths.append(file.name)
                # 未进行管控的文件
                if file.type_raw_name == 'unversioned':
                    repo.add(file.name)
                    # un_file_paths.append(file.name)

                # 修改（过时）的文件
                if file.type_raw_name == 'missing':
                    # 在包文件local.py 添加 删除方法
                    #
                    repo.delete(file.name)
                    # un_file_paths.append(file.name)

                # with open('logs/log.txt', 'a+', encoding='utf-8') as f1:
                #     f1.writelines('fileStatus：{} :{}！\n'.format(file.type_raw_name, file.name))
                # loggingHandler.logger.debug('fileStatus：{} :{}！\n'.format(file.type_raw_name, file.name))
            # if len(un_file_paths) > 0:
            #     # 添加未管控的文件
            #     repo.add(un_file_paths)
            file_count = len(rel_file_paths)
            if file_count > 0:
                pass
            else:
                loggingHandler.logger.warning('***未有代码变化')

            # 获取本机电脑名
            myname = socket.getfqdn(socket.gethostname())
            # 获取本机ip
            myaddr = socket.gethostbyname(myname)

            # 添加到需要提交的列表
            message = '备份系统自动提交，日期为:{} {}备份服务器计算机名称：{}ip地址为：{} 共计'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), os.linesep, myname, myaddr, file_count)
            # repo.commit(message, rel_file_paths)
            # 提交所有文件
            # repo.commit(message, ['*/**/*'])
            loggingHandler.logger.debug('提交备份文件至备份服务器，动作 {}'.format('进行提交'))
            repo.commit(message, [''])
            loggingHandler.logger.info(
                '***提交文件至备份svn服务成功!路径为： {},合计提交{}个文件或文件夹'.format(backup_server_path, str(file_count)))

        except Exception as e:
            loggingHandler.logger.exception('***提交文件至备份svn服务出错（请检查备份svn可用性） {} '.format(backup_server_path))


if __name__ == '__main__':
    fileHandler = FileHandler()
    backupRep = fileHandler.getBackupRepository()
    fileHandler.backupRepository(backupRep)
    fileHandler.svn_commit(backupRep)
