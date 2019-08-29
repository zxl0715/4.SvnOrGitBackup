import git
import loggingHandler
import configparser
import os


def pull(path):
    """
    拉取文件
    :param path:
    :return:
    """
    try:
        # 创建版本库对象
        repo = git.Repo(path)
        # 版本库是否为空版本库
        if repo.bare is True:
            loggingHandler.logger.info('Git 路径{}为空版本库。'.format(path))
        # 拉取最新版本
        repo.git.checkout('.')

        remote = repo.remote()
        import time
        time.sleep(5)
        loggingHandler.logger.debug('remote.name1:{}'.format(remote.name))
        remote.fetch()
        loggingHandler.logger.debug('remote.name2:{}'.format(remote.name))
        remote.pull()
        loggingHandler.logger.debug('remote.name3:{}'.format(remote.name))
        # 强制放弃本地修改（新增、删除文件）
        repo.git.clean('-df')
    except Exception as ee:
        # loggingHandler.logger.error('错误代码{0}：拉取路径为：{1}出错，错误信息{2}'.format(2001, path, ee), ee)
        loggingHandler.logger.exception('错误代码{0}：拉取{1}路径为：{2}出错，错误信息{3}'.format(3001, 'svn', path, ee))
        return False
        # print(type(e))  # 异常实例
        # print('___________________1')
        # print(e)  # 异常参数
        # print('___________________3')
        # print(e.args)  # 异常参数
        # print('___________________3')

    return True


def pullAndMapping(path, mapping_file_path):
    """
    拉取目标Git，并执行映射文件内容
    :param path:
    :param mapping_file_path: 映射文件路径
    :return:返回True or False
    """
    status = pull(path)
    if not status:
        return status

        # 设置映射文件生成的目标路径
    mapping_file_path = os.path.join(path, mapping_file_path)
    if os.path.exists(mapping_file_path):
        try:
            # 设置git映射文件路径
            path_mapping = '{}{}'.format(path, '_mapping')
            if not os.path.exists(path_mapping):
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


def get_backup_project(git_profile_path):
    """读取配置文件，获取子git 映射信息"""
    cf = configparser.ConfigParser()
    try:
        cf.read(git_profile_path, encoding="UTF-8-sig")
    except Exception as e:
        loggingHandler.logger.exception('错误代码：10002 读取配置文件{}失败，请检查应用程序配置文件信息！'.format(git_profile_path))

    value_list = []
    sections = cf.sections()
    for section in sections:
        if section.find('project') == 0:
            name = cf.get(section, 'name')
            description = cf.get(section, 'description')
            url = cf.get(section, 'url')
            value_list.append([name, description, url])
    return value_list


def find_last(string, str_char):
    """
    获取指定字符最后出现的位置
    :param string:
    :param str_char:
    :return:
    """
    last_position = -1
    while True:
        position = string.find(str_char, last_position + 1)
        if position == -1:
            return last_position
        last_position = position


def get_git_project_name(url):
    """
    获取项目名称
    :param url:
    :return:
    """
    index_begin = find_last(url, '/')
    index_end = find_last(url, '.')
    name = url[index_begin + 1:index_end]
    return name


def get_mapping_Git(root_path, git_profile_path):
    """
    获取映射的Git库
    :param root_path:目标的路径
    :param git_profile_path:Git映射配置文件路径
    :return:
    """
    valueList = get_backup_project(git_profile_path)
    with open('{}/{}'.format(root_path, '目录说明.txt'), 'w', encoding="UTF-8-sig")as f:
        for list in valueList:
            try:
                prject_url = list[2]
                name_git = get_git_project_name(prject_url)

                path = '{}\{}'.format(root_path, name_git)
                if list[1].strip() == '':
                    line = '{}'.format(list[0])
                else:
                    line = '{}-{}'.format(list[0], list[1])

                f.writelines('{}:{}{}'.format(name_git, line, '\n'))
                loggingHandler.logger.debug('Git 映射项目{}执行进度……'.format(list[0]))
                # continue
                if not os.path.exists(path):
                    # c初始化空的git目录
                    bare_repo = git.Repo.init(path, True)
                    # 3远程名称作为外部从仓库的别名，可以通过它push和fetch数据
                    origin = bare_repo.create_remote('origin', url=prject_url)

                    # bare_repo.config_reader()  # 获得仓库中只读的配置信息
                    # bare_repo.config_writer()  # 更新仓库中的配置信息
                    assert origin.exists()
                    assert origin == bare_repo.remotes.origin == bare_repo.remotes['origin']
                    # 确保我们有数据。fetch()                返回有用的信息
                    origin.fetch()  # fetch,pull and push from and to the remote

                    origin = bare_repo.remotes.origin  # get default remote by name
                    origin.refs  # local remote reference

                    # 从远程“master”创建本地分支“master”
                    if (len(bare_repo.heads) == 0 and len(bare_repo.remote().refs) > 0):  # 判断是否存在分支
                        bare_repo.create_head('master', origin.refs.master)
                        # 设置本地“master”跟踪远程“master”
                        bare_repo.heads.master.set_tracking_branch(origin.refs.master)

                bare_repo = git.Repo(path)
                # 获取默认版本库 origin
                remote = bare_repo.remote()
                if (len(bare_repo.heads) == 0 and len(bare_repo.remote().refs) > 0):  # 判断是否存在分支
                    bare_repo.create_head('master', origin.refs.master)
                    # 设置本地“master”跟踪远程“master”
                    bare_repo.heads.master.set_tracking_branch(origin.refs.master)
                if len(bare_repo.heads)>0 :
                    # 拉取信息
                    remote.pull()
                    # 从远程版本库拉取分支
                    bare_repo.heads.master.checkout()
                    # bare_repo.git.checkout('.')
                    # 强制放弃本地修改（新增、删除文件）
                    bare_repo.git.clean('-df')
                    loggingHandler.logger.debug('Git 映射项目{}拉取完成。'.format(list[0]))
                else:
                    loggingHandler.logger.debug('Git 映射项目{}为空内容！'.format(list[0]))

            except Exception as e:
                loggingHandler.logger.exception('获取Git项目{}内容失败！'.format(list[0]))
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
        # untracked_file=repo.untracked_files
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
        # get_mapping_Git(r'D:\testGit\GitToSVN', 'conf\BackupProject.conf')
        rw_dir = 'D:\testGit\git175'
        repo_dir = os.path.join(rw_dir, 'my-new-repo')
        file_name = os.path.join(repo_dir, 'new-file')

        r = git.Repo.init(repo_dir)
        # This function just creates an empty file ...
        open(file_name, 'wb').close()
        r.index.add([file_name])
        r.index.commit("initial commit")
    except Exception as e:
        loggingHandler.logger.exception('错误代码：10002 读取配置文件BackupProject.conf失败，请检查应用程序配置文件信息！')
