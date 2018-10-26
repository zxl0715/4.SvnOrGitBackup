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
            if path['path'].strip() == '':
                continue
            # 备份文件
            backup_file_path = '{}\{}'.format(path['path'], fileName)
            # 不存在备份文件的跳过（需要备份的库通过备份文件控制）
            if os.path.isfile(backup_file_path) == False:
                # loggingHandler.logger.warning(
                #     '在{}目录下 {} 文件不存在，请检查！'.format(path['path'], fileName))
                # backupRep.append(
                #     [path['depCode'], path['path'], '','', '{}\{}'.format(path['path'], '')])
                continue
            else:
                try:

                    with open(backup_file_path, encoding="UTF-8-sig") as f:
                        # loggingHandler.logger.info('文件编码为：{}！'.format(f.encoding))

                        line = f.readline()
                        while line:
                            # print(line)
                            str = line.split(':')
                            # 软研中心工程名称格式：sp - 工程名称, 硬研中心工程名称格式：hp - 工程名称, 其他中心待定。
                            backupRep.append(
                                {'depCode': path['depCode'], 'RepositoryPath': path['path'],
                                 'BackupFilePath': backup_file_path, 'RepositoryName': str[0],
                                 'BackupRepository': '{}\{}'.format(os.path.dirname(path['path']), str[0])})

                            line = f.readline()
                except Exception as e:
                    loggingHandler.logger.exception('读取“项目备份保存清单”文件失败，路径为：{}'.format(backup_file_path))
            loggingHandler.logger.info('准备备份工程项目文件至备份服务器{}！'.format(path['path']))

        return backupRep

    def jedgeProjectStandard(self, path, projectStandardlist):
        for fileOrFloder in projectStandardlist:
            if os.path.exists('{}\{}'.format(path, fileOrFloder)) == False:
                loggingHandler.logger.warning(
                    '违反【源文件存放规范】在{} 目录下 {} 文件或目录不存在，请检查！'.format(path, fileOrFloder))

    # backupPath=<class 'list'>: [['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '产销差系统', 'D:\\testSVN\\产销差系统'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '智慧水务赋能管控平台', 'D:\\testSVN\\智慧水务赋能管控平台'], ['sp', 'D:\\testSVN', 'D:\\testSVN\\项目备份保存清单.txt', '一个项目工程', 'D:\\testSVN\\一个项目工程']]
    def backupRepository(self, backupPath=[]):
        '''从源svn或git代码库复制到svn备份库的'''
        # svn备份仓库地址
        backupServerPath = configHandler.getBackupPath()
        # 目录校验
        projectStandard = configHandler.getProjectStandard()
        fileName = '项目备份保存清单.txt'
        inventory_file = '{}\{}'.format(backupServerPath, fileName)
        if os.path.exists(backupServerPath) == False:
            loggingHandler.logger.warning('备份服务器svn路径不存在{}，请检查！', backupServerPath)
        # 清理svn备份仓库的项目备份保存清单文件
        if os.path.exists(inventory_file) == True:
            os.remove(inventory_file)

        for path in backupPath:

            if path['BackupFilePath'].strip() == '':
                continue
            filePath = path['BackupFilePath']
            # 检查根目录下是否有 项目备份保存清单.txt 文件
            if os.path.isfile(filePath) == False:
                loggingHandler.logger.warning('在{}目录下 {} 文件不存在，请检查！'.format(path['RepositoryPath'], filePath))
                continue

            if os.path.exists(path['BackupRepository']):
                try:
                    # 检查工程项目或单个项目 是否违法【源文件存放规范】
                    _rmFile = '{}\{}'.format(path['BackupRepository'], '目录说明.txt')
                    if os.path.exists(_rmFile) and path['BackupRepository'].find('_mapping') == -1:
                        with open(_rmFile, encoding="UTF-8-sig") as f:
                            line = f.readline()
                            while line:
                                # print(line)
                                str = line.split(':')
                                # 目录为工程项目
                                if line.find(':') > 0 & os.path.exists(
                                        '{}\{}'.format(path['BackupRepository'], str[0])):
                                    self.jedgeProjectStandard('{}\{}'.format(path['BackupRepository'], str[0]),
                                                              projectStandard)
                                else:  # 为单个项目
                                    self.jedgeProjectStandard(path['BackupRepository'], projectStandard)
                                line = f.readline()
                except Exception as e:
                    loggingHandler.logger.exception(
                        '检查工程项目或单个项目 是否违法【源文件存放规范】，路径为：{0}'.format(path['BackupRepository']))
            try:
                # 从 项目备份保存清单文件里，读取需要备份的工程项目信息，并写入到 备份目录
                with open(filePath, encoding="UTF-8-sig") as f:
                    line = f.readline()
                    while line:
                        # print(line)
                        str = line.split(':')
                        if str[0] == path['RepositoryName']:
                            f = open(inventory_file, 'a+', encoding="UTF-8-sig")
                            # f.writelines('{}-{}'.format(path['depCode'], line))
                            f.write('{}-{}{}'.format(path['depCode'], line, '\r\n'))
                            f.close()
                            break
                        else:
                            line = f.readline()
            except Exception as e:
                loggingHandler.logger.exception('从 项目备份保存清单文件里，读取需要备份的工程项目信息，路径为：{0}'.format(filePath))
            # 项目备份来源位置
            sourcepath = path['BackupRepository']
            # 项目备份目标位置（备份到目标文件夹）
            tagerpath = '{}\{}-{}'.format(backupServerPath, path['depCode'], os.path.basename(path['BackupRepository']))

            # 文件移动的方案
            enable_plan = 1
            if enable_plan == 2:
                # 方案一
                # todo
                try:
                    if os.path.exists(tagerpath):
                        shutil.rmtree(tagerpath)  # 递归删除一个目录以及目录内的所有内容
                except Exception as e:
                    loggingHandler.logger.exception('删除文件失败，路径为：{0}'.format(tagerpath))

                try:
                    # 进行复制（忽略.svn和.git文件夹）
                    shutil.copytree(sourcepath, tagerpath, ignore=shutil.ignore_patterns('.svn', '.git', '.gitignore'))
                except Exception as e:
                    loggingHandler.logger.exception('从{} 复制到 {}失败！'.format(sourcepath, tagerpath))
            else:

                # 方案二
                self.copyFiles(sourcepath, tagerpath)

            # shutil.copytree(path[4], '{}\{}'.format(backupServerPath, os.path.basename(path[4])), symlinks=False,
            #                 ignore=shutil.ignore_patterns(".svn"), copy_function=shutil.copy2,
            #                 ignore_dangling_symlinks=True)

            # shutil.move(sourcepath, tagerpath)

            loggingHandler.logger.info('移动备份工程项目文件{}至本地备份服务器{}！'.format(sourcepath, path['RepositoryPath']))

    def copyFiles(self, sourceDir, targetDir):
        '''从源svn或git目录，备份文件到备份的svn目录下'''
        if sourceDir.find(".svn") > 0 or sourceDir.find(".git") > 0 or sourceDir.find(".gitignore") > 0:
            return
        for file in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, file)
            targetFile = os.path.join(targetDir, file)
            if len(sourceFile) > 200:
                continue
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
                message += '{}备份服务器ip地址为：{}'.format(os.linesep, self.get_host_ip())

                repo.cleanup()
                repo.commit(message, rel_filepaths)
                loggingHandler.logger.info('***提交文件至备份svn服务成功!路径为： {0}'.format(backupServerPath))
            else:
                loggingHandler.logger.warning('***未有代码变化')

        except Exception as e:
            loggingHandler.logger.exception('***提交文件至备份svn服务出错（请检查备份svn可用性） {0}'.format(backupServerPath))

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
