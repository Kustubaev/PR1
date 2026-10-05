@echo off
cd /d "%~dp0"
py -3 main.py
if errorlevel 1 python main.py
if errorlevel 1 (
  echo Чтобы открыть ПВК, нужен Python 3 с tkinter.
  pause
)
