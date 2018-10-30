# coding=utf-8
import svn.remote
import locale
import svn.local
import pprint
import os
import svn.config

import loggingHandler

'''配置svn编码，否则在控制台输出svn信息报错'''
# 'zh_CN.UTF-8' GBK
codeing = 'GBK'
# DEFAULT_CONSOLE_ENCODING = codeing
# CONSOLE_ENCODING = os.environ.get('SVN_COMMAND_OUTPUT_ENCODING', DEFAULT_CONSOLE_ENCODING)

svn.config.CONSOLE_ENCODING = codeing


def get_client(url_or_path, *args, **kwargs):
    if url_or_path[0] == '/':
        return svn.local.LocalClient(url_or_path, *args, **kwargs)
    else:
        return svn.remote.RemoteClient(url_or_path, *args, **kwargs)


def remote(url, path):
    # 1.服务器仓库检出服务器上的配置库到指定目录

    try:
        r = svn.remote.RemoteClient(url)
        r.checkout(path)
    except Exception as e:
        loggingHandler.logger.exception('服务器仓库检出服务器上的配置库到指定目录出错')


def pull(path):
    '''通过SVN本地客户端，从SVN服务器上把最新版本下载到本地；'''
    try:
        r = svn.local.LocalClient(path)
        # 用来清理locked，防止更新时失败
        r.cleanup()
        r.update()

    # todo:svn 执行 update 报UnicodeDecodeError: 'utf-8' codec can't decode byte 0xca in position 8: invalid continuation byte 错误时修改，svn包下 common_base.py文件，以下代码
    # return stdout.decode().strip('\n').split('\n')
    # return stdout.decode(svn.config.CONSOLE_ENCODING).strip('\n').split('\n')
    except UnicodeDecodeError as e:
        loggingHandler.logger.warning('拉取{}路径为：{}信息{}'.format('svn', path, e))


    except Exception as e:
        loggingHandler.logger.exception('错误代码{0}：拉取{1}路径为：{2}出错，路径可能不是为svn目录，错误信息{3}'.format(3001, 'svn', path, e))
        return False
    return True


def add(path):
    r = svn.local.LocalClient(path)
    # 用来清理locked，防止更新时失败
    r.add(path)


def commit(path):
    r = svn.local.LocalClient(path)
    r.commit()


if __name__ == '__main__':
    url = u'https://zxl0715:8443/svn/testSVN/'
    path = r'D:\testSvnPython'
    # 1远程和本地操作
    # r = get_client(path)
    # r.checkout()
    # 2.远程操作
    remote(url, path)
    # 3.本地操作拉取
    pull
    # pprint.pprint(r.info())
