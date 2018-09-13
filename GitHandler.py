import git
import loggingHandler


def pull(path):
    try:
        # 创建版本库对象
        repo = git.Repo(path)
        # 版本库是否为空版本库
        if repo.bare is False:
            loggingHandler.logger.info('Git 路径{0}为空版本库。'.format(path))
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


if __name__ == '__main__':
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
