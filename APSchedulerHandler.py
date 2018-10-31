import loggingHandler
import os
import time

import apscheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import *
from apscheduler.triggers.cron import CronTrigger

# EVENT_JOB_ADDED = 128
# EVENT_JOB_REMOVED = 256
# EVENT_JOB_MODIFIED = 512
# EVENT_JOB_EXECUTED = 1024
# EVENT_JOB_ERROR = 2048
# EVENT_JOB_MISSED = 4096#
LISTENER_JOB = (EVENT_JOB_ADDED |
                EVENT_JOB_REMOVED |
                EVENT_JOB_MODIFIED |
                EVENT_JOB_EXECUTED |
                EVENT_JOB_ERROR |
                EVENT_JOB_MISSED)

JOB_DEFAULTS = {
    'misfire_grace_time': 1,
    'coalesce': False,
    'max_instances': 100
}

EXECUTORS = {
    'default': ThreadPoolExecutor(2),
    'processpool': ProcessPoolExecutor(4)
}


class JobManager(object):

    def __init__(self):
        self.scheduler = BlockingScheduler(executors=EXECUTORS, job_defaults=JOB_DEFAULTS, timezone='Asia/Shanghai')
        self.jobs = {}
        # self.scheduler.add_listener(err_listener,apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED)
        self.scheduler.add_listener(err_listener, LISTENER_JOB)

    def start(self):
        self.scheduler.start()

    def add_job(self, method, jobid, hour, minute, second, *trigger_args):
        trigger_dict = dict(hour=hour, minute=minute, second=second)
        trigger = CronTrigger(**trigger_dict)

        # job = self.scheduler.add_job(method, 'cron', hour=17, minute=33, second=20)
        job = self.scheduler.add_job(method, trigger, id=jobid, args=trigger_args)
        # job = self.scheduler.add_job(method, trigger)
        print("add job %s successful!" % jobid + "; next_run_time: + str(job.next_run_time)")


def my_job(job_id):
    print('Job ' + str(job_id) + ' begin!' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # 每60秒查看下网络连接情况
    # os.system("netstat -an")

    time.sleep(3)
    print('Job ' + str(job_id) + ' End!' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 4.异常处理
#         当job抛出异常时，APScheduler会默默的把他吞掉，不提供任何提示，这不是一种好的实践，我们必须知晓程序的任何差错。
# APScheduler提供注册listener，可以监听一些事件，包括：job抛出异常、job没有来得及执行等。
def err_listener(events):
    if events.code == EVENT_JOB_MISSED:
        loggingHandler.logger.info('%s miss', str(events.job))
        print("Job %s has missed." % str(events.job_id))

    # if events.exception:
    #     loggingHandler.logger.exception('%s error.', str(events.job))
    #     print('%s error.', str(events.job))
    # else:
    #     loggingHandler.logger.info('%s miss', str(events.job))
    #     print('%s miss', str(events.job))


if __name__ == '__main__':
    sched = JobManager()
    for i in range(1, 3):
        sched.add_job(my_job, str(i), 11, 54, 20 + i * 2)
    sched.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        sched.scheduler.shutdown()
    # sched = BlockingScheduler()
    # # sched.add_job(my_job, 'interval', seconds=5)
    # # 定时每天 12:15:07秒执行任务
    # sched.add_job(my_job, 'cron', hour=17, minute=33, second=20)
    # sched.add_listener(err_listener, apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED)
    #
    # sched.start()

# 每分钟执行一次，可以写成， */1 * * * * cmd
# 每天上午8点执行一次， 可以写成，0 8 */1 * * cmd
# Python已经提供了这个模块，croniter，我们使用 pip install croniter即可安装croniter模块。
#
