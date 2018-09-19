# coding:utf-8
import os.path
import setuptools

setuptools.setup(
    name='svn_or_git_backup',
    version='1.0',
    description="智恒公司 svn或git源代码备份归档操作",
    long_description='',
    classifiers=[],
    keywords='svn git backup',
    author='zhangxiaolin',
    author_email='zhangxioalin@gszh.cn',
    url='www.gszh.cn',
    packages=setuptools.find_packages(exclude=['venv']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['svn', 'apscheduler', 'gitpython']

)
# '''install_requires#定义依赖模块''''

'''
安装 
#python setup.py build     # 编译

#python setup.py install     #安装

#python setup.py sdist       #源码安装包 生成压缩包(zip/tar.gz)

#python setup.py bdist_wininst   #Windows 下使用 生成NT平台安装包(.exe)

#python setup.py bdist_rpm #/Linux 下使用 生成rpm包
'''