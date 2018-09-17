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
        if os.path.isdir(self.filepathname):
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


if __name__ == "__main__":
    pwd = '123'
    _zip_path = '{}\{}'.format(os.getcwd(), 'zipObj.py')
    _dir = os.getcwd()
    filename = '压缩文件夹名称'
    # 进行打包加密压缩
    zipo = ZipObj(_zip_path, pwd)
    zipo.enCrypt(targetPath=_dir, fileName=filename, deleteSource=False)
    pass
