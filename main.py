import os

import loggingHandler


def cmdExecute(cmd):
    print('--------begin------------')
    print(cmd)
    result = os.popen(cmd)
    print(result.read())
    print('--------end------------')
    # .encode("GBK")
    # loggingHandler.logger.info(result.read())
    return result


if __name__ == '__main__':
    # loggingHandler.logger.info('开始启动程序！')
    # cmd = 'svn --version'
    # result = cmdExecute(cmd)
    #
    # cmd = 'd:'
    # result = cmdExecute(cmd)
    # cmd = 'cd /'
    # result = cmdExecute(cmd)

    # windows 下 python 连续执行 cmd 命令(多行) ,
    # 方法一：每行末尾 加  “ &; ” 继续往后执行
    # 方法二：windows下命令之间使用&连接。 如cd C:\&dir

    '''svn cleanup 用来清理locked，防止更新时失败'''
    cmd = r'd: &; ' \
          r'cd testSVN &; ' \
          r'dir &;' \
          r'svn info &' \
          r'svn cleanup &' \
          r'svn update '
    result = cmdExecute(cmd)

    cmd = r'd: &; ' \
          r'cd D:\testGit\test &' \
          r'git pull '
    result = cmdExecute(cmd)
    # .管道subprocess模块。运行原理会在当前进程下面产生子进程。
    # print('管道subprocess模块')
    # sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # sub.wait()
    # print(sub.read())

    if result == 0:
        loggingHandler.logger.info('svn 登陆成功！')
