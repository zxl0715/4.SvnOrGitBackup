# -*- coding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    A brief description goes here.

    :copyright: (c) YEAR by zxl0715.
    :license: LICENSE_NAME, see LICENSE_FILE for more details.
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
import main


class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SvnOrGitBackupService"  # 服务名
    _svc_display_name_ = "SvnOrGitBackupService"  # job在windows services上显示的名字
    _svc_description_ = "备份SVN和GIT项目的程序"  # job的描述

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        self.T = time.time()
        self.run = True

    def SvcDoRun(self):
        loggingHandler.logger.info("service is run....")
        try:
            # while self.run:
            loggingHandler.logger.info('---Begin---')

            main()

            loggingHandler.logger.info('---End---')
            time.sleep(10)

        except Exception as e:
            loggingHandler.logger.info(e)
            time.sleep(60)

    def SvcStop(self):
        loggingHandler.logger.info("service is stop....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


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
