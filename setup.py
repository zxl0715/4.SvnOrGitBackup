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
    zip_safe=False ,
    install_requires['svn','apscheduler','gitpython'] #定义依赖模块

)
