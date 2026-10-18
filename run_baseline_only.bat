@echo off
cd /d "%~dp0"
call run_python.bat benchmark_runner.py --providers demo
pause
