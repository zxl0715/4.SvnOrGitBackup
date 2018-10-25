import multiprocessing
import os
import shutil
import time
from datetime import datetime

import svn.local

import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

import GitHandler
import SvnHandler
import configHandler
import loggingHandler

from APSchedulerHandler import JobManager

# 拉取代码
import FileHandler

#
from zipObj import ZipObj


def backup_svn_git():
    '''使用多进程，拉取代码'''
    # 获取svn和git本地仓库路径
    paths = configHandler.getSvnOrGitPath()
    # 获取本机cpu数量
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores)
    for map in paths:
        '''使用多进程执行'''
        # pool = multiprocessing.Process(target=pull_code, args=(svnOrGit,path,))
        pool.apply_async(pull_code, args=(map['type'], map['path'], map['MappingFilePath']))
        loggingHandler.logger.info('启动多进程拉取代码 {0} 库任务，路径{1}！'.format(map['type'], map['path']))
    pool.close()
    pool.join()
    loggingHandler.logger.info('多进程任务执行代码库同步至本地库完成,共计 {} 个任务!'.format(len(paths)))


def pull_code(svnOrGit='svn', path='', MappingFilePath=None):
    '''拉取代码'''
    status = False
    if os.path.exists(path) == False:
        loggingHandler.logger.warning('{0} 路径{1}不存在。'.format(svnOrGit, path))
        return status
    try:
        # todo
        if svnOrGit == 'svn':
            # todo
            status = SvnHandler.pull(path)
        else:
            # todo
            status = GitHandler.pullAndMapping(path, MappingFilePath)
    except Exception as e:
        loggingHandler.logger.exception('错误代码{0}：{1}拉取路径为：{2}代码库出错，错误信息{3}'.format(1001, svnOrGit, path, e))

    if status:
        loggingHandler.logger.info('{0} 库拉取代码成功，路径{1}！'.format(svnOrGit, path))
    else:
        loggingHandler.logger.info('{0} 库拉取代码失败，路径{1}！'.format(svnOrGit, path))
    return status


def getDetpName(code):
    '''获取部门名称'''
    deptInfo = configHandler.getDdepartment()
    for dept in deptInfo:
        if code == dept[0]:
            return dept[1]
    return None


def make_compressed_file():
    '''执行文件压缩'''
    startswith = '研发成果'
    pwd = configHandler.getZipPwd()
    dst = configHandler.getBackupPath()
    target = configHandler.getTargetPath()
    parent_path = os.path.dirname(dst)
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    zipPath = r'{}\{}-{}'.format(target, startswith, date)

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

    if os.path.exists(zipPath) is False:
        os.makedirs(zipPath)
    _dir = ''
    _dep_code = ''
    _dep_name = ''
    _index = 0
    _zip_path = ''
    # 按部门、工程项目打包压缩
    for dir in os.listdir(dst):
        _index = dir.find("-")
        if os.path.isdir('{}\{}'.format(dst, dir)) == False:
            continue
        if dir.find(".svn") >= 0:
            continue

        if _index > 0:
            _dep_code = dir[:_index]
            _dep_name = getDetpName(_dep_code)
        # 压缩到 的目标文件路径
        _dir = r'{}\{}'.format(zipPath, _dep_name)
        if os.path.exists(_dir) is False:
            os.makedirs(_dir)
        # 对各部门工程项目进行工程说明
        with open('{}\{}'.format(dst, '项目备份保存清单.txt'), encoding="utf-8") as f:
            line = f.readline()
            while line:
                if line.startswith(dir):
                    # str = line.split(':')
                    f = open('{}\工程说明.txt'.format(_dir), 'a+', encoding="utf-8")
                    _index = line.find("-")
                    if _index > 0 and (_index + 1) <= len(line):
                        line = line[_index + 1:]
                    f.write(line)
                    f.close()
                    break
                else:
                    line = f.readline()
        # _dir = r'{}\{}'.format(_dir, os.path.basename(dir))
        # 移除部门简称前缀
        _zip_path = r'{}\{}'.format(dst, dir)
        if _index > 0 and (_index + 1) <= len(dir):
            filename = dir[_index + 1:]
        # 进行打包加密压缩
        zipo = ZipObj(_zip_path, pwd)
        zipo.enCrypt(targetPath=_dir, fileName=filename, deleteSource=False)
        loggingHandler.logger.info('打包工程文件：{} 项目归属部门 {} 成功！'.format(filename.rjust(20), _dep_name.rjust(10)))


def job():
    '''使用定时任务执行'''
    sched = JobManager()

    timeTaskList = configHandler.getTimedTask()
    try:
        for timeTask in timeTaskList:
            if timeTask[0] == 1:
                # 备份源代码和归档
                sched.add_job(backupCode, '', timeTask[1], timeTask[2], timeTask[3], True)
                loggingHandler.logger.info(
                    '添加定时任务成功！类型为：备份源代码和归档，每天执行时间点为：{}:{}:{}'.format(timeTask[1], timeTask[2], timeTask[3]))
            else:
                # 备份源代码
                sched.add_job(backupCode, '', timeTask[1], timeTask[2], timeTask[3], False)
                loggingHandler.logger.info(
                    '添加定时任务成功！类型为：备份源代码，每天执行时间点为：{}:{}:{}'.format(timeTask[1], timeTask[2], timeTask[3]))

    except Exception as e:
        loggingHandler.logger.exception('添加定时任务失败！')
        return None
    try:
        loggingHandler.logger.info('启动定时任务成功！')
        sched.start()
    except (KeyboardInterrupt, SystemExit) as e:
        loggingHandler.logger.exception('结束程序运行2！')
    finally:
        sched.scheduler.shutdown()
        loggingHandler.logger.info('结束程序运行！')


def backup_file_svn():
    '''备份文件到svn（备份的svn）'''
    fileHandler = FileHandler.FileHandler()
    backupRep = fileHandler.getBackupRepository()
    if len(backupRep) > 0:
        try:
            fileHandler.backupRepository(backupRep)
            loggingHandler.logger.info('移动备份工程项目文件至本地备份服务器！')
            fileHandler.svn_commit(backupRep)
        except (KeyboardInterrupt, SystemExit) as e:
            loggingHandler.logger.exception('备份文件到svn出现异常！')


# def backup_svn_git_zip():
#     '''拉取文件及归档备份'''
#     backup_svn_git()
#     # 压缩


def backupCode(isZip=False):
    loggingHandler.logger.info('启动任务{}'.format(os.linesep))
    try:
        # 拉取代码
        loggingHandler.logger.debug('backup_svn_git 1')
        # todo
        backup_svn_git()
        loggingHandler.logger.debug('backup_svn_git 2')
        loggingHandler.logger.debug('backup_file_svn 1')
        # 备份文件至svn备份服务器
        # todo
        backup_file_svn()
        loggingHandler.logger.debug('backup_file_svn 2')

        # 是否启用打包归档
        if isZip:
            # 按工程进行打包归档
            loggingHandler.logger.debug('make_compressed_file 1')
            make_compressed_file()
            loggingHandler.logger.debug('make_compressed_file 2')

    except Exception as e:
        loggingHandler.logger.exception('备份任务出现异常')
    loggingHandler.logger.info('结束任务{}'.format(os.linesep))


def main():
    multiprocessing.freeze_support()  # 解决pyinstaller多进程打包问题
    loggingHandler.logger.info('{}————————————————————————————————————————————————{}'.format(os.linesep, os.linesep))
    loggingHandler.logger.info('启动程序运行！')

    '''设置启动运行'''
    firstStartup = configHandler.getFirstStartup()
    # firstStartup = False
    if firstStartup:
        loggingHandler.logger.info('程序启动一次运行开始！')
        backupCode(True)
        loggingHandler.logger.info('程序启动一次运行结束！{}'.format(os.linesep))

    loggingHandler.logger.info('开始启动定时任务……')
    # 执行定时任务
    job()
    loggingHandler.logger.info('結束启动定时任务')

    loggingHandler.logger.info('结束程序运行！')


if __name__ == '__main__':
    main()
