import subprocess
import zipfile as zf
import platform as pf
import os
import configHandler


class ZipObj():

    def __init__(self, filepathname, passwd):
        self.filepathname = filepathname
        self.passwd = passwd
        '''需使用WinRAR压缩文件处理，该压缩程序支持命令调用及压缩加密'''
        self.zipPath = configHandler.getZipAppPath()

    def enCrypt(self, targetPath='', deleteSource=False):
        """
            压缩加密，并删除原数据
            window系统调用rar程序

            linux等其他系统调用内置命令 zip -P123 tar source
            默认不删除原文件
        """
        target = ''
        target = self.filepathname + ".zip"
        if targetPath.strip():
            target = targetPath + '\\' + os.path.basename(self.filepathname) + ".zip"
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
    pwd = configHandler.getZipPwd()
    dst = configHandler.getSourcePath()
    target = configHandler.getTargetPath()
    if os.path.exists(dst) is False:
        print('路径不存在')
    parent_path = os.path.dirname(dst)

    zipo = ZipObj(dst, pwd)
    zipo.enCrypt(targetPath=target, deleteSource=False)

    # zipo.deCrypt()
