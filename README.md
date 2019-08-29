# 环境

 序号  | 应用名称  | 版本| 说明 
 ---- | ----- | ------ | ------ 
1   |  Python  |  3.6以上  |  
2	|Git	|建议2.18以上	  
3	|TortoiseSVN	|不限（建议1.10以上）  	
4	|Subversion	|（建议3.9以上）	  

[1.SvnOrGitBackup部署环境要求](docs/1.SvnOrGitBackup部署环境要求.doc)
#使用 Setup 将Python 代码 打包

python setup.py build           # 编译  
python setup.py install         #安装  
python setup.py sdist           #源码安装包 生成压缩包(zip/tar.gz)  
python setup.py bdist_wininst   #Windows 下使用 生成NT平台安装包(.exe)  
python setup.py bdist_rpm       #/Linux 下使用 生成rpm包

#源代码打包成可执行文件 
`yinstaller  --hidden-import=main -w main.py -n SvnOrGitBackup -i favicon.ico -r app.conf`  
 
    --hidden-import=main  解决运行弹出错误提示框：failed to execute script main 
    -w：窗口模式打包，不显示控制台。  
    -i favicon.ico 程序的图标  
    -r app.conf   加入配置文件  
