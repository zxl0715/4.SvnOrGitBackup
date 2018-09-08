from datetime import datetime
import os

import logging
from temp import ziphandle

logger = logging.getLogger(__name__)

logger.setLevel(level=logging.WARN)
# Log

logger.debug('Debugging')

logger.critical('Critical Something')

logger.error('Error Occurred')

logger.warning('Warning exists')

logger.info('Finished')



def dir_entries(dir_name, subdir, *args):
    '''
    Return a list of file names found in directory 'dir_name'
    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional arguments, if any, are file extensions to match filenames. Matched
        file names are added to the list.
    If there are no additional arguments, all files found in the directory are
        added to the list.
    Example usage: fileList = dir_entries(r'H:\TEMP', False, 'txt', 'py')
        Only files with 'txt' and 'py' extensions will be added to the list.
    Example usage: fileList = dir_entries(r'H:\TEMP', True)
        All files and all the files in subdirectories under H:\TEMP will be added
        to the list.
    '''
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if not args:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
        # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            #print "Accessing directory:", dirfile
            fileList.extend(dir_entries(dirfile, subdir, *args))
    return fileList

if __name__=='__main__':
    REPO_NAME = r'repo_name'
    now = datetime.now()
    date = '%d.%02d.%02d-%02d.%02d.%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    zipf = 'svn-%s-backup-%s.zip' % (REPO_NAME, date)
    dst = r'D:\360Downloads'
    if os.path.exists(dst):
       print('路径不存在')
    result = ziphandle.make_archive(dir_entries(dst, True), zipf)