# Video demo checklist

This is an operating checklist, not a narration script. Speak in your own voice. Confirm the actual Canvas video length/link requirements; none were verified for this final. The separate Build 2 assignment's 60-90-second requirement must not be assumed here.

## Before recording

- [ ] Read `FINAL_READY_REPORT.md`, the comparison tables, and API limitations. Keep environment settings and credentials off-screen.
- [ ] Open a terminal at `C:\NCAT\COMP365_Checkpoint2_Project`; use `.\.venv\Scripts\python.exe`.
- [ ] Run `web_app.py`, open `http://127.0.0.1:8365`, and visually inspect it. Saved Qwen is an explicitly labeled offline replay; baseline generates a fresh local response.

## Screens and actions

- [ ] J01 / baseline: original missing semicolon, explanation, editable patch, diff, separate successful compilation and test results.
- [ ] J05 / baseline: unchanged patch compiles but fails functional tests. If you personally change `a - b` to `a + b` and retest, identify your edit as excluded from model benchmark results.
- [ ] J12 or J20 / saved Qwen: runtime bug, exact response, replay label, recorded generation time, held-out results. Retest for a fresh local execution check.
- [ ] Open the displayed evidence directory: source, response/envelope, patch/diff, compiler output, tests, and CSV/JSON. Distinguish original experiments from UI reviews.
- [ ] Open `results/comparisons/20261018T154343_232420Z_final_328a03d4/tables.md` and `figure_ready_data.csv`. Show baseline 1/20 and Qwen 9/20 functional per response; Gemini unevaluated. Distinguish Qwen's 13/13 extracted-patch compile rate from 13/20 delivered responses.
- [ ] Show syntax/logic/runtime results and seven invalid Qwen responses. Patch success does not establish explanation accuracy.
- [ ] Show Gemini metadata preflight and unavailable records; there is no generation response or repair score. Never display the key.
- [ ] Show the blank human worksheet and separate preliminary AI ratings. Report only human judgments you personally completed.

## Commands worth showing

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe validate_benchmarks.py
.\.venv\Scripts\python.exe summarize_results.py results\runs\20261018T131412_396245Z_benchmark_41bb2533 --check
.\.venv\Scripts\python.exe finalize_results.py --check results\comparisons\20261018T154343_232420Z_final_328a03d4
```

- [ ] Show `submission/LATEST_SUBMISSION.json`, its verification sidecar, and the local review branch. Do not push without approval.
- [ ] State actual scope: 20 self-authored Java cases, 36 visible and 58 held-out tests. C++ has a separate compilation smoke demo. No measured student learning benefit or public-dataset experiment.
- [ ] Play back the recording, check readable text/audio and link access, and submit yourself before October 18, 2026 at 11:59 PM ET.
