# coding=utf-8
import svn.remote
import locale
import svn.local
import pprint
import os
import svn.config

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
        print(e)


def pull(path):
    '''通过SVN本地客户端，从SVN服务器上把最新版本下载到本地；'''
    try:
        r = svn.local.LocalClient(path)
        # 用来清理locked，防止更新时失败
        r.cleanup()
        r.update()
    except Exception as e:
        print(e)


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
