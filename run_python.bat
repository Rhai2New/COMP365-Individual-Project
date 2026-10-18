@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" %*
) else (
  py -3.12 %*
)
exit /b %errorlevel%
