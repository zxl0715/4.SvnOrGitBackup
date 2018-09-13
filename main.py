import svn.local

import GitHandler
import SvnHandler
import configHandler


def svn_pull():
    paths = configHandler.getSvnPath().split(';')
    try:
        for path in paths:
            SvnHandler.pull(path)
    except Exception as e:
        print(e)

def git_pull():
    paths = configHandler.getGitPath().split(';')
    try:
        for path in paths:
            GitHandler.pull(path)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # svn_pull()
    git_pull()
