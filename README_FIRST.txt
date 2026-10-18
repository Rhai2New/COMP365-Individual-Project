HISTORICAL CHECKPOINT MATERIAL: current instructions and verified results are in README.md and docs/FINAL_TECHNICAL_STATUS.md.

COMP 365 - Practical Checkpoint 1
Interactive Code Bug Explainer & Patch Generator

WHAT IS INCLUDED
----------------
bug_explainer.py            Main Python checkpoint prototype
requirements.txt            Python package needed for the live OpenAI test
samples/BuggyGreeting.java  Small Java syntax-error test
samples/BuggyTotal.cpp      Small C++ syntax-error test
run_demo_test.bat           Windows test that works without an API key
run_cpp_demo_test.bat       C++ demo test
run_live_openai_test.bat    Live AI/API checkpoint test
results/                    Output files are saved here

FASTEST TEST (NO API KEY)
-------------------------
1. Extract the ZIP.
2. Double-click run_demo_test.bat.
3. The program will:
   - compile BuggyGreeting.java,
   - capture javac's real compiler error,
   - generate a beginner-friendly local demo explanation + patch,
   - save BuggyGreeting_patched.java,
   - compile the patched file,
   - show PASS if the patch compiles,
   - save results/checkpoint_demo_output.txt.

LIVE AI TEST FOR THE PROJECT CHECKPOINT
---------------------------------------
You need an OpenAI API key with API access/credits. A ChatGPT subscription by itself is
not the same thing as API billing/access.

Open Command Prompt inside this folder and run:

    set OPENAI_API_KEY=YOUR_KEY_HERE
    run_live_openai_test.bat

The live script installs the OpenAI Python package, sends the Java source and javac error
to the OpenAI Responses API, prints the model explanation/patch, writes a patched source
file, and recompiles it for a PASS/FAIL verification.

COMMAND-LINE VERSION
--------------------
Demo:
    py bug_explainer.py --source samples\BuggyGreeting.java --provider demo

Live API:
    py -m pip install -r requirements.txt
    set OPENAI_API_KEY=YOUR_KEY_HERE
    py bug_explainer.py --source samples\BuggyGreeting.java --provider openai --save-output results\checkpoint_live_output.txt

WHAT TO SCREENSHOT FOR THE REPORT
---------------------------------
For the strongest checkpoint evidence, screenshot the live API run after it finishes.
Make sure the screenshot includes:
- ORIGINAL COMPILER / RUNTIME ERROR
- AI / PATCH ENGINE OUTPUT
- PATCH VERIFICATION showing PASS

If you have not run the live API yet, the included report uses the verified local demo
result as the current technical-result figure and correctly labels the AI/API portion as
ready for live testing rather than claiming a live API call occurred.
