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