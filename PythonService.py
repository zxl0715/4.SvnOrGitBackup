# -*- coding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    A brief description goes here.

    :copyright: (c) YEAR by zxl0715.
    :license: LICENSE_NAME, see LICENSE_FILE for moree details.
"""

import win32timezone
from logging.handlers import TimedRotatingFileHandler
import win32serviceutil
import win32service
import win32event
import winerror

import os
import logging
import inspect
import time
import shutil
import sys
import servicemanager
import win32timezone
import loggingHandler
# from main import *
from MyTickScheduler import MyTickScheduler
from mainBackup import Worker


class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SvnOrGitBackupService"  # 服务名
    _svc_display_name_ = "SvnOrGitBackupService"  # job在windows services上显示的名字
    _svc_description_ = "备份SVN和GIT项目的程序"  # job的描述

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.job = MyTickScheduler()

        self.run = True

    def _getLogger(self):
        '''日志记录'''
        logger = logging.getLogger('[PythonService]')
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        if os.path.isdir('%s\\logs' % dirpath):  # 创建log文件夹
            pass
        else:
            os.mkdir('%s\\logs' % dirpath)
        dir = '%s\\logs' % dirpath

        handler = TimedRotatingFileHandler(os.path.join(dir, "Clearjob.log"), when="midnight", interval=1,
                                           backupCount=20)
        formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        return logger

    def SvcDoRun(self):
        self.logger.info("service is run....")
        try:
            # import loggingHandler
            # # loggingHandler.logger.info('启动程序运行！')
            # this_file = inspect.getfile(inspect.currentframe())
            # dirpath = os.path.abspath(os.path.dirname(this_file))
            # self.logger.info('this_file:{}'.format(this_file))
            # self.logger.info('dirpath:{}'.format(dirpath))
            # dir = '%s\\log' % dirpath
            # self.logger.info('2:{}'.format(os.path.join(dir, "Clearjob.log")))
            # self.logger.info('1111---Begin---')
            # self.logger.info('22---end---')
            # from main import main_job
            # main_job()
            # self.logger.info('22---end---')
            woker = Worker()
            woker.first_run()
            self.job.run()  # 开始任务
        except Exception as e:
            self.logger.exception('错误代码:{}：'.format(e))

        while self.run:
            time.sleep(4)

    def SvcStop(self):
        self.logger.info("服务器准备停止....")
        self.run = False
        self.job.stop()  # 停止任务
        self.logger.info("正在停止中....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        """
        以下代码解决 
        提示：错误1053 服务没有及时相应启动或控制请求
        """
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(PythonService)  # 如果修改过名字，名字要统一
            servicemanager.Initialize('PythonService', evtsrc_dll)  # 如果修改过名字，名字要统一
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(PythonService)  # 如果修改过名字，名字要统一

'''
安装服务　　　　python PythonService.py install
自动启动　　　　python PythonService.py –startup auto install # 如果需要设置开机自启动，则须要使用命令
启动服务　　　　python PythonService.py start
重启服务　　　　python PythonService.py restart
停止服务　　　　python PythonService.py stop
删除\卸载服务　 python PythonService.py remove
'''
