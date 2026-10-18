@echo off
cd /d "%~dp0"
call run_python.bat bug_explainer.py --source samples\BuggyGreeting.java --provider demo
pause
