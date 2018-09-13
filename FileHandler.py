import os

import configHandler
import loggingHandler


def getBackupRepository():
    paths = configHandler.getSvnPath().split(';')
    paths.extend(configHandler.getGitPath().split(';'))

    pathsNew = list(set(paths))  # 去除重复
    fileName = '项目备份保存清单.txt'
    backupRep = []
    for path in pathsNew:
        filePath = path + '/' + fileName
        if os.path.isfile(filePath) == False:
            loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！', path, fileName)
        with open(filePath) as f:
            line = f.readline()
            while line:
                print(line)
                str = line.split(':')
                backupRep.append([path, filePath, str[0], ])

                line = f.readline()
    return backupRep


if __name__ == '__main__':
    backupRep = getBackupRepository()
