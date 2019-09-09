@echo off

%#-w 无控制台模式%
%#-n 生成应用名称%
%#-i 应用图标%
%#--add-data 需要拷贝资源到生存目录%
%#-y 生成时是否删除原来生存的内容%

pyinstaller -w mainBackup.py -n SvnOrGitBackup -i favicon.ico --add-data "conf\app.conf;conf" -y
pause

%
%#生成windows service 使用nssm打包%
%#步骤一：生成exe可执行文件，以上操作， %
%#步骤二：在需要安装电脑上的cmd下 执行 nssm install   ，选择上面生生成的可执行文件，填写后台服务内容等，安装%
%