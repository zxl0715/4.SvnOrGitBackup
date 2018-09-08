import subprocess
import zipfile as zf
import platform as pf
import os

class ZipObj():

    def __init__(self,filepathname,passwd):
        self.filepathname = filepathname
        self.passwd = passwd
    def enCrypt(self,deleteSource=False):
        """
            压缩加密，并删除原数据
            window系统调用rar程序

            linux等其他系统调用内置命令 zip -P123 tar source
            默认不删除原文件
        """
        target = self.filepathname+".zip"
        source = self.filepathname+".txt"
        if pf.system()=="Windows":
            cmd = ['rar','a','-p%s'%(self.passwd),target,source]
            p = subprocess.Popen(cmd,executable=r'C:\Program Files\WinRAR\WinRAR.exe')
            p.wait()
        else:
            cmd = ['zip','-P %s'%(self.passwd),target,source]
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
        zfile = zf.ZipFile(self.filepathname+".zip")
        zfile.extractall(r"zipdata",pwd=self.passwd.encode('utf-8'))


if __name__ == "__main__":
    zipo = ZipObj(r"研发成果-20180803","123")
    zipo.enCrypt(deleteSource=False)
#     zipo.deCrypt()