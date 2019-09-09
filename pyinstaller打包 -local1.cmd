@echo off
cd /d %~dp0
pyinstaller -w main.py -n SvnOrGitBackup -i favicon.ico -v 

pause