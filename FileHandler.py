import os
import shutil
import socket
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

    # backupPath=<class 'list'>: [['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '产销差系统', 'D:\\testSVN\\产销差系统'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '智慧水务赋能管控平台', 'D:\\testSVN\\智慧水务赋能管控平台'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '一个项目工程', 'D:\\testSVN\\一个项目工程']]
    def backupRepository(self, backupPath=[]):
        '''执行需要备份的svn或git代码库'''
        backupServerPath = configHandler.getBackupPath()
        fileName = '项目备份保存清单.txt'
        fileProject = '{}\{}'.format(backupServerPath, fileName)
        if os.path.exists(backupServerPath) == False:
            loggingHandler.logger.warning('备份服务器svn路径不存在{}，请检查！', backupServerPath)

        if os.path.exists(fileProject) == True:
            os.remove(fileProject)
        for path in backupPath:

            if path[2].strip() == '':
                continue
            filePath = path[2]
            # 检查根目录下是否有 项目备份保存清单.txt 文件
            if os.path.isfile(filePath) == False:
                loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！'.format(filePath))
                continue
            # 从 项目备份保存清单文件里，读取需要备份的工程项目，并写入到 备份目录
            with open(filePath) as f:
                line = f.readline()
                while line:
                    # print(line)
                    str = line.split(':')
                    if str[0] == path[3]:
                        f = open(fileProject, 'a+')
                        f.write('{}-{}'.format(path[0], line))
                        f.close()
                        break
                    else:
                        line = f.readline()
            # 进行源码文本备份（备份到目标文件夹）
            sourcepath = path[4]
            tagerpath = '{}\{}-{}'.format(backupServerPath, path[0], os.path.basename(path[4]))
            # 方案一
            # self.copyFiles(sourcepath,tagerpath)

            # 方案二
            if os.path.exists(tagerpath):
                shutil.rmtree(tagerpath)  # 递归删除一个目录以及目录内的所有内容
            shutil.copytree(sourcepath, tagerpath)

            # shutil.copytree(path[4], '{}\{}'.format(backupServerPath, os.path.basename(path[4])), symlinks=False,
            #                 ignore=shutil.ignore_patterns(".svn"), copy_function=shutil.copy2,
            #                 ignore_dangling_symlinks=True)

            # shutil.move(sourcepath, tagerpath)

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
            changFile = repo.status()
            un_filepaths = []
            rel_filepaths = []
            aa = 1
            for file in changFile:
                rel_filepaths.append(file.name)
                # 未进行管控的文件
                if file.type_raw_name == 'unversioned':
                    aa += 1
                    repo.add(file.name)
                    un_filepaths.append(file.name)
                # 修改（过时）的文件
                if file.type_raw_name == 'missing':
                    aa += 1
                    repo.delete(file.name)
                    un_filepaths.append(file.name)

                print(file)
            # if len(un_filepaths) > 0:
            #     # 添加未管控的文件
            #     repo.add(un_filepaths)

            if len(rel_filepaths) > 0:
                # 添加到需要提交的列表
                message = '备份系统自动提交，日期为:{0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                message += '{}ip地址为{}'.format(os.linesep, self.get_host_ip())

                repo.cleanup()
                repo.commit(message, rel_filepaths)
            # SvnHandler.commit(tempPath)
        except Exception as e:
            loggingHandler.logger.exception('提交文件至备份svn服务出错 {0}'.format(backupServerPath))

    def get_host_ip(self):
        '''获取本机ip'''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


if __name__ == '__main__':
    fileHandler = FileHandler()
    backupRep = fileHandler.getBackupRepository()
    fileHandler.backupRepository(backupRep)
    fileHandler.svn_commit(backupRep)
