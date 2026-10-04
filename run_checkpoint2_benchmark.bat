@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
) else (
  set "PYTHON_EXE=python"
)

if exist "C:\NCAT\jdk-25.0.4.1+1\bin\javac.exe" (
  set "JAVA_HOME=C:\NCAT\jdk-25.0.4.1+1"
  set "PATH=C:\NCAT\jdk-25.0.4.1+1\bin;%PATH%"
)

if "%OPENAI_API_KEY%"=="" (
  echo ERROR: OPENAI_API_KEY is not set in this terminal.
  echo In PowerShell, run: $env:OPENAI_API_KEY="YOUR_NEW_KEY"
  echo Then run this file again.
  pause
  exit /b 1
)

"%PYTHON_EXE%" benchmark_runner.py --providers demo,openai --output results/checkpoint2_results.csv
pause
