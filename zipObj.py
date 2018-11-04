import subprocess
import zipfile as zf
import platform as pf
import os
import configHandler
import loggingHandler


class ZipObj():

    def __init__(self, file_path_name, passwd):
        self.file_path_name = file_path_name
        self.passwd = passwd
        '''需使用WinRAR压缩文件处理，该压缩程序支持命令调用及压缩加密'''
        self.zipPath = configHandler.get_zip_app_path()

    def enCrypt(self, target_path='', file_name=None, delete_source=False):
        """
            压缩加密，并删除原数据
            window系统调用rar程序

            linux等其他系统调用内置命令 zip -P123 tar source
            默认不删除原文件
        """
        target_object = ''
        if file_name is not None:
            # 自定义压缩文件名称
            target_object = target_path + '\\' + file_name + ".zip"
        elif target_path.strip():
            # 设置源文件目录为压缩文件名称
            target_object = target_path + '\\' + os.path.basename(self.file_path_name) + ".zip"
        else:
            target_object = self.file_path_name + ".zip"
        if os.path.isdir(self.file_path_name):
            source = self.file_path_name + '\*.*'
        if pf.system() == "Windows":
            cmd = ['rar', 'a', '-r', '-ibck', '-ad', '-ep1', '-p{0}'.format(self.passwd), target_object, source]
            p = subprocess.Popen(cmd, executable=self.zipPath, stdout=subprocess.PIPE)
            p.wait()
        else:
            cmd = ['zip', '-P %s' % self.passwd, target_object, source]
            p = subprocess.Popen(cmd)
            p.wait()
        #            os.system(" ".join(cmd))
        if delete_source:
            os.remove(source)

    def deCrypt(self):
        """
        使用之前先创造ZipObj类
        解压文件
        """
        zfile = zf.ZipFile(self.file_path_name + ".zip")
        zfile.extractall(r"zipdata", pwd=self.passwd.encode('utf-8'))


if __name__ == "__main__":
    pwd = '123'
    _zip_path = '{}\{}'.format(os.getcwd(), 'zipObj.py')
    _dir = os.getcwd()
    file_name = '压缩文件夹名称'
    # 进行打包加密压缩
    zipo = ZipObj(_zip_path, pwd)
    zipo.enCrypt(target_path=_dir, file_name=file_name, delete_source=False)
    pass
