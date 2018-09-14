import multiprocessing
import os
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


def pull_code(svnOrGit='svn', path=''):
    status=False
    if os.path.exists(path) == False:
        loggingHandler.logger.warning('{0} 路径{1}不存在。'.format(svnOrGit, path))
    try:
        if svnOrGit == 'svn':
            status = SvnHandler.pull(path)
        else:
            status = GitHandler.pull(path)
    except Exception as e:
        loggingHandler.logger.exception('错误代码{0}：{1}拉取路径为：{2}代码库出错，错误信息{3}'.format(1001, svnOrGit, path, e))

    if status:
        loggingHandler.logger.info('{0} 库更新代码成功，路径{1}！'.format(svnOrGit, path))
    else:
        loggingHandler.logger.info('{0} 库更新代码失败，路径{1}！'.format(svnOrGit, path))
    return status


#
def backup_svn_git():
    '''拉取代码'''
    # 获取svn和git本地仓库路径
    paths = configHandler.getSvnOrGitPath()
    # 获取本机cpu数量
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores)
    for map in paths:
        '''使用多进程执行'''
        # pool = multiprocessing.Process(target=pull_code, args=(svnOrGit,path,))
        pool.apply_async(pull_code, args=(map[0], map[2],))
        print('process start {}{}'.format(map[0], map[2]))

    pool.close()
    pool.join()
    print('All processes done!')


def my_job(job_id):
    print('Job ' + str(job_id) + ' begin!' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # 每60秒查看下网络连接情况
    # os.system("netstat -an")

    time.sleep(3)
    print('Job ' + str(job_id) + ' End!' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def job():
    '''使用定时任务执行'''
    # timeNow= (datetime.datetime.now() + datetime.timedelta(=1)
    # hour = int(time.strftime('%H', time.localtime(time.time())))
    # minute = int(time.strftime('%M', time.localtime(time.time())))
    # second = int(time.strftime('%S', time.localtime(time.time())))
    #
    # i = datetime.datetime.now()+datetime.timedelta(second=10)
    # i.hour
    sched = JobManager()
    for i in range(1, 4):
        sched.add_job(my_job, str(i), 14, 26, 20 + i * 2)

    loggingHandler.logger.info('启动定时任务成功！')
    sched.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit) as e:
        loggingHandler.logger.exception('结束程序运行2！')
    finally:
        sched.scheduler.shutdown()
        loggingHandler.logger.info('结束程序运行！')


if __name__ == '__main__':
    loggingHandler.logger.info(r'\n————————————————————————————————————————————————\n')
    loggingHandler.logger.info('启动程序运行！')

    '''设置启动运行'''
    firstStartup = configHandler.getFirstStartup()
    # firstStartup = False
    if firstStartup:
        loggingHandler.logger.info('启动首次运行！')
        backup_svn_git()

        fileHandler = FileHandler()
        backupRep = fileHandler.getBackupRepository()
        fileHandler.backupRepository(backupRep)
        fileHandler.svn_commit(backupRep)

        loggingHandler.logger.info('结束首次运行！')

    loggingHandler.logger.info('开始启动定时任务……')

    # job()
