@echo off
cd C:\MyData\Work_ZH\WIS\100.project\4.SvnOrGitBackup
pyinstaller -w main.py -n SvnOrGitBackup -i favicon.ico -y

#-w 无控制台模式
#-n 生成应用名称
#-i 应用图标
#--add-data 需要拷贝资源到生存目录
#-y 生成时是否删除原来生存的内容
pyinstaller -w main.py -n SvnOrGitBackup -i favicon.ico --add-data "conf\app.conf;conf" -y
pause


#生成windows service 使用nssm打包
步骤一：生成exe可执行文件，在cmd命令下执行如下信息
pyinstaller -w mainBackup.py -n SvnOrGitBackup -i favicon.ico 
步骤二：在需要安装电脑上的cmd下 执行 nssm install   ，选择上面生生成的可执行文件，填写后台服务内容等，安装