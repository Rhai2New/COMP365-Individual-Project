@echo off
cd /d "%~dp0"
echo Final runner: cloud calls are disabled by default. See README.md.
call run_python.bat benchmark_runner.py --providers demo,gemini
pause
