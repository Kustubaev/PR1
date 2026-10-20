@echo off
cd /d "%~dp0"
if exist ".python313\pythonw.exe" (
  start "" ".python313\pythonw.exe" main.py
  exit /b
)
py -3 main.py
if errorlevel 1 python main.py
if errorlevel 1 (
  echo Чтобы открыть ПВК, нужен Python 3 с tkinter.
  pause
)
