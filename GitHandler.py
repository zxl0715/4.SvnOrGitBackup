import git
import loggingHandler
import configparser
import os


def pullAndMapping(path, mapping_file_path):
    '''
    拉取目标GIT，并执行映射文件内容
    :param path:
    :param mapping_file_path: 映射文件路径
    :return:返回True or False
    '''
    status = pull(path)
    if status == False:
        return status

        # 设置映射文件生成的目标路径
    mapping_file_path = '{}\{}'.format(path, mapping_file_path)
    if os.path.exists(mapping_file_path) == True:
        try:
            # 设置git映射文件路径
            path_mapping = '{}{}'.format(path, '_mapping')
            if os.path.exists(path_mapping) == False:
                os.mkdir(path_mapping)
            get_mapping_Git(path_mapping, mapping_file_path)
        except Exception as e:
            loggingHandler.logger.exception('Git版本库路径：{}，拉取应映射文件项目失败，映射路径：{}。'.format(path, mapping_file_path))
            return status

        loggingHandler.logger.info('Git版本库路径：{}，拉取应映射文件项目成功，映射路径：{}。'.format(path, mapping_file_path))
        # status = True
    else:
        loggingHandler.logger.info('Git版本库路径：{}，找不到对应映射文件路径：{}。'.format(path, mapping_file_path))
        # status = False
    return status


def pull(path):
    '''
    拉取文件
    :param path:
    :return:
    '''
    try:
        # 创建版本库对象
        repo = git.Repo(path)
        # 版本库是否为空版本库
        if repo.bare is True:
            loggingHandler.logger.info('Git 路径{}为空版本库。'.format(path))
        # 拉取最新版本
        repo.git.checkout('.')
        # 强制放弃本地修改（新增、删除文件）
        repo.git.clean('-df')
    except Exception as e:
        # loggingHandler.logger.error('错误代码{0}：拉取路径为：{1}出错，错误信息{2}'.format(2001, path, e), e)
        loggingHandler.logger.exception('错误代码{0}：拉取{1}路径为：{2}出错，错误信息{3}'.format(3001, 'svn', path, e))
        return False
        # print(type(e))  # 异常实例
        # print('___________________1')
        # print(e)  # 异常参数
        # print('___________________3')
        # print(e.args)  # 异常参数
        # print('___________________3')

    return True


def get_backup_projtect(git_profile_path):
    """读取配置文件，获取git信息"""
    cf = configparser.ConfigParser()
    try:
        cf.read(git_profile_path, encoding="utf-8-sig")
    except Exception as e:
        loggingHandler.logger.exception('错误代码：10002 读取配置文件BackupProject.conf失败，请检查应用程序配置文件信息！')

    value_list = []
    sections = cf.sections()
    for section in sections:
        if section.find('project') == 0:
            name = cf.get(section, 'name')
            description = cf.get(section, 'description')
            url = cf.get(section, 'url')
            value_list.append([name, description, url])
    return value_list


def find_last(string, str):
    '''获取指定字符最后出现的位置'''
    last_position = -1
    while True:
        position = string.find(str, last_position + 1)
        if position == -1:
            return last_position
        last_position = position


def get_git_project_name(url):
    '''获取项目名称'''
    index_begin = find_last(url, '/')
    index_end = find_last(url, '.')
    name = url[index_begin + 1:index_end]
    return name


def get_mapping_Git(root_path, git_profile_path):
    '''
    获取影视的Git库
    :param root_path:目标的路径
    :param git_profile_path:Git映射配置文件路径
    :return:
    '''
    valueList = get_backup_projtect(git_profile_path)
    with open('{}/{}'.format(root_path, '目录说明.txt'), 'w', encoding="GBK")as f:
        for list in valueList:
            prjectURL = list[2]
            name_git = get_git_project_name(prjectURL)

            path = '{}\{}'.format(root_path, name_git)
            line = ''
            if list[1].strip() == '':
                line = '{}'.format(list[0])
            else:
                line = '{}-{}'.format(list[0], list[1])

            f.writelines('{}:{}{}'.format(name_git, line, '\n'))
            print(list[0])
            # continue
            if os.path.exists(path) == False:
                repo = git.Repo.init(path, True)
                # 3远程名称作为外部从仓库的别名，可以通过它push和fetch数据
                test_remote = repo.create_remote('origin', prjectURL)
                # os.mkdir(path)
            # 2
            # ---------
            repo = git.Repo(path)
            # repo.delete_remote(test_remote)  # create and delete remotes
            # 获取默认版本库 origin
            remote = repo.remote()
            # todo
            remote.fetch()  # fetch,pull and push from and to the remote
            # repo.heads.master.checkout()  # checkout the branch using git-checkout

            # # 从远程版本库拉取分支
            # repo.heads.master.checkout()
            remote.pull('master')
            repo.git.checkout('.')
            # 强制放弃本地修改（新增、删除文件）
            repo.git.clean('-df')
            # ---------
            # origin = repo.remotes[0]  # get default remote by name
            # origin.refs  # local remote reference
            # o = origin.rename('new_origin')  # rename remotes

            # repo.git.checkout('.')
            # o.pull()
            # 远程库的配置信息
            # print(o.url)
            # 创建版本库对象
            # # 克隆版本库
            # repo.clone(prjectURL)
            # 4从远程版本库拉取分支
            # repo.remote().pull()
    return True


def test():
    try:
        path = r'D:\testGit\test'
        # 创建版本库对象
        repo = git.Repo(path)

        # 版本库是否为空版本库
        a = repo.bare
        print(str(a))
        # 当前工作区是否干净
        a = repo.is_dirty()
        print(str(a))
        # 版本库中未跟踪的文件列表
        repo.untracked_files
        # 克隆版本库
        repo.clone('clone_path')
        # 获取默认版本库 origin
        remote = repo.remote()
        # 从远程版本库拉取分支
        remote.pull()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # test()
    try:
        get_mapping_Git(r'D:\testGit\GitToSVN', 'conf\BackupProject.conf')
    except Exception as e:
        loggingHandler.logger.exception('错误代码：10002 读取配置文件BackupProject.conf失败，请检查应用程序配置文件信息！')
