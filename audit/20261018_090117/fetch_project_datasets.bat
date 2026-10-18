@echo off
cd /d "%~dp0"
where git >nul 2>nul
if not %errorlevel%==0 (
    echo ERROR: Git was not found on PATH.
    pause
    exit /b 1
)
if not exist external mkdir external
cd external
if not exist QuixBugs git clone --depth 1 https://github.com/jkoppel/QuixBugs.git
if not exist defects4j git clone --depth 1 https://github.com/rjust/defects4j.git
cd ..
echo.
echo Dataset source repositories are now under the external folder.
echo Curate only small methods/programs appropriate to the approved project scope.
pause
