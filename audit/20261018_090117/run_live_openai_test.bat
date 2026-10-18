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
if "%OPENAI_API_KEY%"=="" (
    echo OPENAI_API_KEY is not set.
    echo.
    echo In this same Command Prompt, run:
    echo     set OPENAI_API_KEY=your_api_key_here
    echo Then run this file again.
    echo.
    pause
    exit /b 1
)
%PYCMD% -m pip install -r requirements.txt
%PYCMD% bug_explainer.py --source samples\BuggyGreeting.java --provider openai --save-output results\checkpoint_live_output.txt
pause
