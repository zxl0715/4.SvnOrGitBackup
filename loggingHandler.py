import inspect
import logging
import logging.handlers
import os
import configHandler

this_file = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(this_file))
logDir = os.path.join(dirpath,'logs')
if os.path.exists(logDir) is False:
    os.mkdir(logDir)

logger = logging.getLogger(__name__)

loging_level = configHandler.get_logging_level()
if loging_level.upper() == 'DEBUG':
    logger.setLevel(logging.DEBUG)
elif loging_level.upper() == 'INFO':
    logger.setLevel(logging.INFO)
elif loging_level.upper() == 'WARNING':
    logger.setLevel(logging.WARNING)
elif loging_level.upper() == 'ERROR':
    logger.setLevel(logging.ERROR)
elif loging_level.upper() == 'CRITICAL':
    logger.setLevel(logging.CRITICAL)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# 写入文件，如果文件超过100个Bytes，仅保留5个文件。
handler = logging.handlers.RotatingFileHandler(
    logDir + '/app.log', maxBytes=2 * 1024 * 1024, backupCount=5, encoding='utf-8')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

'''日志输出到屏幕控制台'''
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

if __name__ == '__main__':

    logger.critical('Critical Something')
    logger.error('Error Occurred')
    logger.warning('Warning exists')
    logger.info('Finished')
    logger.debug('Debugging')

    while True:
        logger.info("sleep     sleepsleepsleepsleepsleepsleepsleepsleepsleepsleepsleeptest")
        logger.critical('test critical')
