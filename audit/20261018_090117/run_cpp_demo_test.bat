@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set PYCMD=py) else (set PYCMD=python)
where g++ >nul 2>nul
if not %errorlevel%==0 (
    echo ERROR: g++ was not found. Install/use a C++ compiler and make sure g++ is on PATH.
    pause
    exit /b 1
)
echo Running the C++ no-key checkpoint demo...
%PYCMD% bug_explainer.py --source samples\BuggyTotal.cpp --provider demo --save-output results\checkpoint_cpp_demo_output.txt
pause
