from distutils.core import setup
import py2exe

options = {"py2exe": {"compressed": 1,  # 压缩
                      "optimize": 2,
                      "bundle_files": 1  # 所有文件打包成一个exe文件
                      }}

setup(console=["PythonService.py"],
      service=["PyWindowsService"],
      options=options,
      zipfile=None)
