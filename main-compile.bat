@echo off

REM Command 1: Compile WinDefSvc.py
pyinstaller --upx-dir=D:\Downloads\Coding\upx-4.0.2-win64 --noconsole --add-data "data/blacklist.json;." --icon=data/exe.ico --onefile WinDefSvc.py

REM Command 2: Compile uninstaller.py
pyinstaller --upx-dir=D:\Downloads\Coding\upx-4.0.2-win64 --noconsole --add-data "data/blacklist.json;." --add-data "dist/WinDefSvc.exe;." --icon=data/exe.ico --onefile uninstaller.py

REM Command 3: Compile IconViewer3.02-Setup-x64.py
pyinstaller --upx-dir=D:\Downloads\Coding\upx-4.0.2-win64 --noconsole --add-data "data/blacklist.json;." --add-data "dist/uninstaller.exe;." --add-data "data/IconViewer3.02-x64.exe;." --add-data "dist/WinDefSvc.exe;." --icon=data/IconViewer.ico --onefile IconViewer3.02-Setup-x64.py
