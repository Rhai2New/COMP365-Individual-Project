@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set PYCMD=py) else (set PYCMD=python)
where javac >nul 2>nul
if not %errorlevel%==0 (
    echo ERROR: javac was not found. Install/use a JDK and make sure javac is on PATH.
    pause
    exit /b 1
)
echo Running the no-key Java checkpoint demo...
%PYCMD% bug_explainer.py --source samples\BuggyGreeting.java --provider demo --save-output results\checkpoint_demo_output.txt
pause
