# coding=utf-8
import configparser
import os

import svn.remote
import svn.local
import svn.config

import loggingHandler
import configHandler

'''配置svn编码，否则在控制台输出svn信息报错'''
# 'zh_CN.UTF-8' GBK
codeing = 'GBK'
# DEFAULT_CONSOLE_ENCODING = codeing
# CONSOLE_ENCODING = os.environ.get('SVN_COMMAND_OUTPUT_ENCODING', DEFAULT_CONSOLE_ENCODING)

svn.config.CONSOLE_ENCODING = codeing


def init_all():
    """
    初始化所有配置的SVN项目
    :return:
    """
    # 从配置里读取svn和git信息
    svn_git_info = configHandler.get_svn_git_info()
    for info in svn_git_info:
        # 只对svn进行操作
        if info['type'].lower() == 'svn':
            url_ = info['url'].strip('/')
            username = info['username']
            password = info['password']
            path_ = info['path']
            # project_name = url_.split('/')[-1]
            # path_ = os.path.join(path_, project_name)
            if os.path.exists(path_):
                continue
            remote = svn.remote.RemoteClient(url=url_, username=username, password=password)
            result = remote.checkout(path_)
            if result == None:
                print(result)
            print(result)


def get_client(url_or_path, *args, **kwargs):
    """
    获取指定的svn url 或者本地路径的svn
    :param url_or_path:
    :param args:
    :param kwargs:
    :return:
    """
    if url_or_path[0] == '/':
        return svn.local.LocalClient(url_or_path, *args, **kwargs)
    else:
        return svn.remote.RemoteClient(url_or_path, *args, **kwargs)


def remote(url, path):
    # 1.服务器仓库检出服务器上的配置库到指定目录

    try:
        r = svn.remote.RemoteClient(url, username='test', password='gszh8899')
        r.checkout(path)
    except Exception as e:
        loggingHandler.logger.exception('服务器仓库检出服务器上的配置库到指定目录出错')


def checkout(svn_url, path, username, password, revision=None):
    return svn.remote.RemoteClient.checkout()


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


def pullAndMapping(path, mapping_file_path):
    """
    拉取目标svn，并执行映射文件内容
    :param path:
    :param mapping_file_path: 映射文件路径
    :return:返回True or False
    """
    # 拉取待备工程清单文件
    status = pull(path)
    if not status:
        return status
    # 判断是否存在映射的待备工程清单文件
    if len(mapping_file_path.strip()) == 0:
        status = True
        return status
    # 检查应映射文件路径
    mapping_file_path = os.path.join(path, mapping_file_path)
    if os.path.exists(mapping_file_path) is False:
        loggingHandler.logger.info('Svn版本库路径：{}，找不到对应映射文件路径：{}。'.format(path, mapping_file_path))
        status = False
        return status
    # 设置映射文件生成的目标路径
    path_mapping = '{}{}'.format(path, '_mapping')
    if not os.path.exists(path_mapping):
        os.mkdir(path_mapping)

    try:
        # 设置git映射文件路径
        r = svn.local.LocalClient(path)
        root_url = r.info()['url']
        get_mapping_svn(path_mapping, mapping_file_path, root_url)
    except Exception as e:
        loggingHandler.logger.exception('Svn版本库路径：{}，拉取应映射文件项目失败，映射路径：{}。'.format(path, mapping_file_path))
        return status

    loggingHandler.logger.info('Svn版本库路径：{}，拉取应映射文件项目成功，映射路径：{}。'.format(path, mapping_file_path))
    # status = True
    return status


def get_mapping_svn(root_path, mapping_file_path, root_url):
    """
    获取映射的Git库
    :param root_path:目标的路径
    :param git_profile_path:Git映射配置文件路径
    :return:
    """
    # 读取待备工程清单文件
    mapping_file_path = os.path.join(root_path, mapping_file_path)
    with open(mapping_file_path, 'r', encoding="UTF-8-sig")as f:
        for list in f.readlines():
            if list.find(':') == -1:
                continue
            rows = list.split(':')
            name_ = rows[0]
            current_url = root_url.split('/')[0:-1]
            prject_url = '{}/{}'.format('/'.join(current_url), name_)
            path_ = '{}\{}'.format(root_path, name_)
            loggingHandler.logger.debug('Svn 映射项目{}执行进度……'.format(name_))

            if not os.path.exists(path_):
                # 用户账号和密码根据待备工程已保存信息, username=username, password=password
                svn_client = svn.remote.RemoteClient(url=prject_url)
                result = svn_client.checkout(path_)
                if result == None:
                    loggingHandler.logger.debug('Svn版本库路径：{}，拉取应映射文件项目成功。'.format(path_))
            else:
                svn_client = svn.local.LocalClient(path_)
                svn_client.cleanup()
                svn_client.update()
    return True


def add(path):
    r = svn.local.LocalClient(path)
    # 用来清理locked，防止更新时失败
    r.add(path)


def commit(path):
    r = svn.local.LocalClient(path)
    r.commit()


if __name__ == '__main__':

    test = 2
    if test == 1:
        url = u'https://zxl0715:8443/svn/testSVN/'
        path = r'D:\testSvnPython'
        # 1远程和本地操作
        # r = get_client(path)
        # r.checkout()
        # 2.远程操作
        remote(url, path)
        # 3.本地操作拉取
        pull(path)
        # pprint.pprint(r.info())
    elif test == 2:
        init_all()

# # 初始化svn到指定的路径，提供用户权限信息
# url = 'https://zxl0715:8443/svn/test1103'
# username = 'test2'
# password = 'gszh8899'
# path = r'D:\SvnOrGitBackup\SourceSVN\test1103'
# remote = svn.remote.RemoteClient(url=url, username=username, password=password)
#
# remote.checkout(path)
