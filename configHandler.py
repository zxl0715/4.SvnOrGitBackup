import configparser
import sys

cf = configparser.ConfigParser()
'''conf.ini  （ini，conf）'''
cf.read('app.conf', encoding="utf-8-sig")


def getFirstStartup():
    '''#程序启动是否运行，1为运行，0为不运行'''
    return cf.getboolean('system', 'FirstStartup')


def getZipAppPath():
    '''获取WinRAR 压缩文件的路径'''
    return cf.get('config', 'ZipAppPath')


def getZipPwd():
    '''
    获取压缩文件加密密码
    :return:返回密码
    '''
    return cf.get('config', 'ZipPwd')


def getBackupPath():
    '''代码备份的路径'''
    return cf.get('config', 'BackupPath')


def getTargetPath():
    '''压缩到指定的路径'''
    return cf.get('config', 'TargetPath')


def getSvnOrGitPath():
    '''获取git或svn路径信息'''
    sections = cf.sections()
    valueList = []
    numOrder = ''
    for section in sections:
        if section.find('SvnOrGit') == 0:
            # 源码服务类型为svn或者git
            type = cf.get(section, 'Type').lower()
            # 部门代号：软研中心“sp” 硬研中心为“hp” 其他中心待定。
            depCode = cf.get(section, 'DepartmentCode')
            # svn或git 本地路径
            path = cf.get(section, 'LocalPath')
            # 软研中心工程名称格式：sp-工程名称, 硬研中心工程名称格式：hp-工程名称,其他中心待定。
            dept = cf.get(section, 'Department')
            valueList.append([type, depCode, path, dept])
    return valueList
