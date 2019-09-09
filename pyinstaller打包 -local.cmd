@echo off
cd /d %~dp0
pyinstaller -w mainBackup.py -n SvnOrGitBackup -i favicon.ico -v 

pause