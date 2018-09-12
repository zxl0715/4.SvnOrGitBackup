import logging
import os
import time

import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import (EVENT_JOB_EXECUTED, EVENT_JOB_ERROR)
import math

content = dir(math)


def my_job():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


sched = BlockingScheduler()



# 4.异常处理
#         当job抛出异常时，APScheduler会默默的把他吞掉，不提供任何提示，这不是一种好的实践，我们必须知晓程序的任何差错。
# APScheduler提供注册listener，可以监听一些事件，包括：job抛出异常、job没有来得及执行等。
def err_listener(ev):
    err_logger = logging.getLogger('schedErrJob')
    if ev.exception:
        err_logger.exception('%s error.', str(ev.job))
        print('%s error.', str(ev.job))

    else:
        err_logger.info('%s miss', str(ev.job))
        print('%s miss', str(ev.job))



# sched.add_job(my_job, 'interval', seconds=5)
# 定时每天 12:15:07秒执行任务
sched.add_job(my_job, 'cron', hour=17, minute=33, second=20)
sched.add_listener(err_listener, apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED)

sched.start()
# 每60秒查看下网络连接情况
if __name__ == '__main__':


    os.system("netstat -an")

# 每分钟执行一次，可以写成， */1 * * * * cmd
# 每天上午8点执行一次， 可以写成，0 8 */1 * * cmd
#
# 因此，我们可以利用linux的cron 定义计划任务。那如何解析cron的计划呢？很幸运，Python已经提供了这个模块，croniter，我们使用 pip install croniter即可安装croniter模块。
#
# 至此，就可以利用croniter解析Linux cron格式的计划任务了，而我们只需将计划任务写入到文件中，再有Python读取即可。我定义的计划任务格式如下：
