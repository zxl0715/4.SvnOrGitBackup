import os
import shutil
import time

import svn
from svn.common import CommonClient

import SvnHandler
import configHandler
import loggingHandler


class FileHandler:
    def getBackupRepository(self):
        '''获取需要备份的工程项目，返回备份的工程项目路径'''
        paths = configHandler.getSvnOrGitPath()
        # paths = configHandler.getSvnPath().split(';')
        # paths.extend(configHandler.getGitPath().split(';'))

        # pathsNew = list(set(paths))  # 去除重复
        fileName = '项目备份保存清单.txt'
        backupRep = []
        for path in paths:
            if path[2].strip() == '':
                continue
            filePath = '{}\{}'.format(path[2], fileName)
            if os.path.isfile(filePath) == False:
                loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！'.format(path[2], fileName))
                continue
            with open(filePath) as f:
                line = f.readline()
                while line:
                    # print(line)
                    str = line.split(':')
                    # 软研中心工程名称格式：sp - 工程名称, 硬研中心工程名称格式：hp - 工程名称, 其他中心待定。
                    backupRep.append([path[1], path[2], filePath, str[0], '{}\{}'.format(path[2], str[0])])

                    line = f.readline()
        return backupRep

    def backupRepository(self, backupPath=[]):
        '''执行需要备份的svn或git代码库'''
        backupServerPath = configHandler.getBackupPath()
        fileName = '项目备份保存清单.txt'
        fileProject='{}\{}'.format(backupServerPath, fileName)
        if os.path.exists(backupServerPath) == False:
            loggingHandler.logger.warning('备份服务器svn路径不存在{}，请检查！', backupServerPath)

        if os.path.exists(fileProject)==True:
            os.remove(fileProject)
        for path in backupPath:

            if path[2].strip() == '':
                continue
            filePath = path[2]
            if os.path.isfile(filePath) == False:
                loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！'.format(filePath))
                continue
            with open(filePath) as f:
                line = f.readline()
                while line:
                    # print(line)
                    str = line.split(':')
                    if str[0] == path[3]:
                        f = open(fileProject, 'a+')
                        f.write('{}-{}'.format(path[0],line))
                        f.close()
                        break
                    else:
                        line = f.readline()

            # 拷贝文件 “项目备份保存清单.txt”
            # shutil.copy2(path[2], '{}\{}'.format(backupServerPath, os.path.basename(path[2])))

            # shutil.copytree(path[4], '{}\{}-{}'.format(backupServerPath, path[0], os.path.basename(path[4])))
            self.copyFiles(path[4], '{}\{}-{}'.format(backupServerPath, path[0], os.path.basename(path[4])))
            # shutil.copytree(path[4], '{}\{}'.format(backupServerPath, os.path.basename(path[4])), symlinks=False,
            #                 ignore=shutil.ignore_patterns(".svn"), copy_function=shutil.copy2,
            #                 ignore_dangling_symlinks=True)
            # shutil.move(path[4], '{}\{}'.format(backupServerPath, os.path.basename(path[4])))

    def copyFiles(self, sourceDir, targetDir):
        '''从源svn或git目录，备份文件到备份的svn目录下'''
        if sourceDir.find(".svn") > 0:
            return
        for file in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, file)
            targetFile = os.path.join(targetDir, file)
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if os.path.isfile(sourceFile):
                if not os.path.exists(targetFile) or (
                        os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                    open(targetFile, "wb").write(open(sourceFile, "rb").read())
            if os.path.isdir(sourceFile):
                First_Directory = False
                self.copyFiles(sourceFile, targetFile)

    def svn_commit(self, backupPath=[]):
        '''备份的文件通过svn提交操作'''
        backupServerPath = configHandler.getBackupPath()
        if os.path.exists(backupServerPath) == False:
            loggingHandler.logger.warning('备份服务器svn路径不存在{0}，请检查！', backupServerPath)

        try:
            repo = svn.local.LocalClient(backupServerPath)
            changeFiel = repo.status()
            un_filepaths = []
            rel_filepaths = []
            aa = 1
            for file in changeFiel:
                if aa == 1:
                    rel_filepaths.append(file.name)
                    if file.type_raw_name == 'unversioned':
                        aa += 1
                        un_filepaths.append(file.name)

                print(file)
            if len(un_filepaths) > 0:
                repo.add(un_filepaths)  # 添加未管控的文件
            if len(rel_filepaths) > 0:
                message = '备份系统自动提交，日期为:{0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                repo.cleanup()
                repo.commit(message, rel_filepaths)
            # SvnHandler.commit(tempPath)
        except Exception as e:
            loggingHandler.logger.exception('提交文件至备份svn服务出错 {0}'.format(backupServerPath))


if __name__ == '__main__':
    fileHandler = FileHandler()
    backupRep = fileHandler.getBackupRepository()
    fileHandler.backupRepository(backupRep)
    fileHandler.svn_commit(backupRep)
