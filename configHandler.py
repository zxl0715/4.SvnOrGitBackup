import configparser
import loggingHandler
from collections import Iterable

cf = configparser.ConfigParser()
'''conf.ini  （ini，conf）'''
try:
    cf.read('conf/app.conf', encoding="utf-8-sig")
except Exception as e:
    loggingHandler.logger.exception('错误代码：10001 读取配置文件失败，请检查应用程序配置文件信息！')


def get_first_startup():
    '''#程序启动是否运行，1为运行，0为不运行'''
    return cf.getboolean('system', 'FirstStartup')


def get_logging_level():
    '''#程序启动是否运行，1为运行，0为不运行'''
    return cf.get('logginConfig', 'LoggingLevel')


def get_zip_app_path():
    '''获取WinRAR 压缩文件的路径'''
    return cf.get('config', 'ZipAppPath')


def get_zip_pwd():
    '''
    获取压缩文件加密密码
    :return:返回密码
    '''
    return cf.get('config', 'ZipPwd')


def get_backup_path():
    '''代码备份的路径'''
    return cf.get('config', 'BackupPath')


def get_target_path():
    '''压缩到指定的路径'''
    return cf.get('config', 'TargetPath')


def get_department():
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


def get_project_standard():
    '''项目文件规范，需要包含以下文件夹或文件(目录根目录为项目的根目录)，多个内容以;分隔符连接。，例如：scripts;docs\docs;目录说明.txt'''
    file_or_folder = cf.get('ProjectStandard', 'FileOrFolder')
    file_or_folder_list = file_or_folder.split(';')

    return file_or_folder_list


def get_timed_task():
    '''设置定时任务时间'''
    sections = cf.sections()
    value_list = []
    numOrder = ''
    for section in sections:
        if section.find('TimedTask') == 0:
            # 是否启用归档模式：默认0为不启用（只备份源代码，不进行归档操作），1为启用（备份源代码及归档操作）
            archive_mode = cf.getint(section, 'ArchiveMode')
            # 时
            hour = cf.getint(section, 'Hour')
            # 分
            minute = cf.getint(section, 'Minute')
            # 秒
            second = cf.getint(section, 'Second')
            value_list.append([archive_mode, hour, minute, second])
    return value_list


def get_svn_or_git_path():
    '''获取git或svn路径信息'''
    sections = cf.sections()
    value_list = []
    for section in sections:
        if section.find('SvnOrGit') == 0:
            # 源码服务类型为svn或者git
            type = cf.get(section, 'Type').lower()
            # 部门代号：软研中心“sp” 硬研中心为“hp” 其他中心待定。
            depCode = cf.get(section, 'DepartmentCode')
            # svn或git 本地路径
            path = cf.get(section, 'LocalPath')
            mapping_file_path = None
            if cf.has_option(section, 'MappingFilePath'):
                mapping_file_path = cf.get(section, 'MappingFilePath')

            value_list.append({'type': type, 'depCode': depCode, 'path': path, 'MappingFilePath': mapping_file_path})
    return value_list
