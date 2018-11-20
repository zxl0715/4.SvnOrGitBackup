import configHandler
import loggingHandler
from APSchedulerHandler import JobManager


class MyTickScheduler(object):
    def __init__(self):
        self.__sched = JobManager()

    def __addTash(self):
        timeTaskList = configHandler.get_timed_task()
        try:
            from mainBackup import Worker
            for timeTask in timeTaskList:
                if timeTask[0] == 1:
                    # 备份源代码和归档

                    self.__sched.add_job(Worker.backup_code, '', timeTask[1], timeTask[2], timeTask[3], True)
                    loggingHandler.logger.info(
                        '添加定时任务成功！类型为：备份源代码和归档，每天执行时间点为：{}:{}:{}'.format(timeTask[1], timeTask[2], timeTask[3]))
                else:
                    # 备份源代码
                    self.__sched.add_job(Worker.backup_code, '', timeTask[1], timeTask[2], timeTask[3], False)
                    loggingHandler.logger.info(
                        '添加定时任务成功！类型为：备份源代码，每天执行时间点为：{}:{}:{}'.format(timeTask[1], timeTask[2], timeTask[3]))

        except Exception as e:
            loggingHandler.logger.exception('添加定时任务失败！')
            return False
        return True

    def run(self):
        self.__addTash()
        try:
            self.__sched.start()
        except (KeyboardInterrupt, SystemExit) as e:
            loggingHandler.logger.exception('启动定时任务失败！')
            self.__sched.scheduler.shutdown()

    def stop(self):

        self.__sched.scheduler.shutdown()
