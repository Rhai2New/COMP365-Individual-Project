@echo off
echo Running the no-key Java checkpoint demo...

set "PYTHON_EXE=C:\NCAT\COMP365_Checkpoint1_Project\.venv\Scripts\python.exe"
set "JAVA_HOME=C:\NCAT\jdk-25.0.4.1+1"
set "PATH=%JAVA_HOME%\bin;%PATH%"

"%PYTHON_EXE%" bug_explainer.py --source samples\BuggyGreeting.java --provider demo --save-output results\checkpoint_demo_output.txt

echo.
pause
