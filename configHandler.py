import configparser

cf = configparser.ConfigParser()
'''conf.ini  （ini，conf）'''
cf.read('app.conf',encoding="utf-8-sig" )


def getZipAppPath():
    '''获取WinRAR 压缩文件的路径'''
    return cf.get('config', 'zipAppPath')

def getZipPwd():
    '''
    获取压缩文件加密密码
    :return:返回密码
    '''
    return cf.get('config','zipPwd')

def getSourcePath():
    '''压缩到指定的路径'''
    return cf.get('config','sourcePath')

def getTargetPath():
    '''压缩到指定的路径'''
    return cf.get('config','targetPath')