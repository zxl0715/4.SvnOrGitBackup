from temp import logging1

logger = logging1.getLogger('main.core')

def run():

    logger.info('Core Info')

    logger.debug('Core Debug')

    logger.error('Core Error')