import shutil
import subprocess
import time
import zipfile as zf
import platform as pf
import os
import configHandler
import loggingHandler


class ZipObj():

    def __init__(self, filepathname, passwd):
        self.filepathname = filepathname
        self.passwd = passwd
        '''需使用WinRAR压缩文件处理，该压缩程序支持命令调用及压缩加密'''
        self.zipPath = configHandler.getZipAppPath()

    def enCrypt(self, targetPath='', fileName=None, deleteSource=False):
        """
            压缩加密，并删除原数据
            window系统调用rar程序

            linux等其他系统调用内置命令 zip -P123 tar source
            默认不删除原文件
        """
        target = ''
        if fileName is not None:
            # 自定义压缩文件名称
            target = targetPath + '\\' + fileName + ".zip"
        elif targetPath.strip():
            # 设置源文件目录为压缩文件名称
            target = targetPath + '\\' + os.path.basename(self.filepathname) + ".zip"
        else:
            target = self.filepathname + ".zip"

        source = self.filepathname + '\*.*'
        if pf.system() == "Windows":
            cmd = ['rar', 'a', '-r', '-ibck', '-ad', '-ep1', '-p{0}'.format(self.passwd), target, source]
            p = subprocess.Popen(cmd, executable=self.zipPath, stdout=subprocess.PIPE)
            p.wait()
        else:
            cmd = ['zip', '-P %s' % self.passwd, target, source]
            p = subprocess.Popen(cmd)
            p.wait()
        #            os.system(" ".join(cmd))
        if deleteSource:
            os.remove(source)

    def deCrypt(self):
        """
        使用之前先创造ZipObj类
        解压文件
        """
        zfile = zf.ZipFile(self.filepathname + ".zip")
        zfile.extractall(r"zipdata", pwd=self.passwd.encode('utf-8'))


def getDetpName(code):
    deptInfo = configHandler.getDdepartment()
    for dept in deptInfo:
        if code == dept[0]:
            return dept[1]

    return None


if __name__ == "__main__":
    startswith = '研发成果'
    pwd = configHandler.getZipPwd()
    dst = configHandler.getBackupPath()
    target = configHandler.getTargetPath()
    parent_path = os.path.dirname(dst)
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    zipPath = r'{}\{}-{}'.format(target, startswith, date)

    if os.path.exists(dst) is False:
        print('路径不存在')
    try:
        for dir in os.listdir(target):
            if dir.startswith(startswith):
                shutil.rmtree('{}\{}'.format(target, dir))

    except Exception as e:
        loggingHandler.logger.exception('5001  删除历史归档文件失败，请检查文件是否被占用或无权限访问！')

    if os.path.exists(zipPath) is False:
        os.makedirs(zipPath)
    _dir = ''
    _dep_code = ''
    _dep_name = ''
    _index = 0
    _zip_path = ''
    for dir in os.listdir(dst):
        _index = dir.find("-")

        if os.path.isdir('{}\{}'.format(dst, dir)) == False:
            continue
        if dir.find(".svn") >= 0:
            continue

        if _index > 0:
            _dep_code = dir[:_index]
            _dep_name = getDetpName(_dep_code)
        # 压缩到 的目标文件路径
        _dir = r'{}\{}'.format(zipPath, _dep_name)
        if os.path.exists(_dir) is False:
            os.makedirs(_dir)

        with open('{}\{}'.format(dst, '项目备份保存清单.txt')) as f:
            line = f.readline()
            while line:
                if line.startswith(dir):
                    # str = line.split(':')
                    f = open('{}\工程说明.txt'.format(_dir), 'a+')
                    _index = line.find("-")
                    if _index > 0 and (_index + 1) <= len(line):
                        line = line[_index + 1:]
                    f.write(line)
                    f.close()
                    break
                else:
                    line = f.readline()
        # _dir = r'{}\{}'.format(_dir, os.path.basename(dir))
        _zip_path = r'{}\{}'.format(dst, dir)
        if _index > 0 and (_index + 1) <= len(dir):
            filename = dir[_index + 1:]
        # 进行打包加密压缩
        zipo = ZipObj(_zip_path, pwd)
        zipo.enCrypt(targetPath=_dir, fileName=filename, deleteSource=False)

    # zipo.deCrypt()
