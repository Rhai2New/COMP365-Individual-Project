@echo off
cd /d "%~dp0"
if "%OPENAI_MODEL%"=="" (
  echo Set OPENAI_MODEL to an exact accessible model identifier; check API billing first.
  pause
  exit /b 1
)
call run_python.bat bug_explainer.py --source samples\BuggyGreeting.java --provider openai --model "%OPENAI_MODEL%" --allow-live
pause
