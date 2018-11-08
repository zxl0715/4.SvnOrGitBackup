@echo off
E:
cd E:\4.SvnOrGitBackup
pyinstaller  --hidden-import=main -w main.py -n SvnOrGitBackup -i favicon.ico -r app.conf

pause