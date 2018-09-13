import logging
import logging.handlers
import os

logDir = 'logs'
if os.path.exists(os.getcwd() + '/' + logDir) is False:
    os.mkdir(os.getcwd() + '/' + logDir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# 写入文件，如果文件超过100个Bytes，仅保留5个文件。
handler = logging.handlers.RotatingFileHandler(
    logDir + '/app.log', maxBytes=2 * 1024 * 1024, backupCount=5)
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
