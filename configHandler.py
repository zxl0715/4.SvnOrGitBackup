import configparser
import sys
import loggingHandler

cf = configparser.ConfigParser()
'''conf.ini  （ini，conf）'''
try:
    cf.read('app.conf', encoding="utf-8-sig")
except Exception as e:
    loggingHandler.logger.exception('错误代码：10001 读取配置文件失败，请检查应用程序配置文件信息！')


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


def getDdepartment():
    '''获取部门信息'''
    sections = cf.sections()
    valueList = []

    for section in sections:
        if section.find('Department') == 0:
            # 部门代号：软研中心“sp” 硬研中心为“hp” 其他中心待定。
            code = cf.get(section, 'Code')
            # 部门名称：软研中心， 硬研中心
            name = cf.get(section, 'Name')
            valueList.append([code, name])
    return valueList


def getTimedTask():
    '''设置定时任务时间'''
    sections = cf.sections()
    valueList = []
    numOrder = ''
    for section in sections:
        if section.find('TimedTask') == 0:
            # 是否启用归档模式：默认0为不启用（只备份源代码，不进行归档操作），1为启用（备份源代码及归档操作）
            archivemmode = cf.getint(section, 'ArchiveMode')
            # 时
            hour = cf.getint(section, 'Hour')
            # 分
            minute = cf.getint(section, 'Minute')
            # 秒
            second = cf.getint(section, 'Second')
            valueList.append([archivemmode, hour, minute, second])
    return valueList


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
