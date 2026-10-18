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

"%PYTHON_EXE%" benchmark_runner.py --providers demo --output results/baseline_results.csv
pause
