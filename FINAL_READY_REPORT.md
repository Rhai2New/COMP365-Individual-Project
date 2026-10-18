# Final ready report - October 18, 2026

**The feasible technical work is complete and packaged for review. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated.** Student paper, human explanation review, video, Overleaf, approval of a GitHub push, and Canvas submission remain student-owned. Deadline supplied by the student: **October 18, 2026, 11:59 PM ET**.

## 1. Completed technical tasks

- Reviewed the existing implementation, preserved historical evidence, and verified the original rule baseline was unchanged.
- The local .env key authenticated successfully. J01 passed compilation and all tests, then the staged helper automatically continued J02-J20 with at least 65-second request spacing and no retries. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated. Requested model: gemini-3.8-flash; saved served identifier(s): gemini-3.8-flash. Quota failures: 0; service errors: 1; access errors: 0. The user personally confirmed Free Tier with billing disabled; billing was not enabled and no paid API calls were authorized. Earlier HTTP 400/blocked experiments remain historical and are excluded from this comparison.
- Permanent project `.env` authentication is in use and overrides the malformed historical Windows value. The actual local secret stays excluded from Git, ZIPs, prompts, logs, and snapshots. `.env.example` remains placeholder-only.
- Preserved all previous experimental evidence. Fixed explicit Gemini model selection in the runner and added a mocked regression test; selected model identity is now checked through the adapter and saved records. Added an explicit worksheet output root for nested run shards.
- Verified baseline/Qwen source/model/runtime settings, raw responses, envelopes, extracted patches/diffs, compiler/test outcomes, category results, timing records, CSV layers, seals, and regenerated tables. Recompiled/retested all 43 extracted patches across the three systems; every recorded outcome reproduced.
- Verified 20 benchmark classifications and all 94 expected outputs (36 visible, 58 hidden) with Python oracles and authored Java controls. No incorrect expectation was found.
- Completed a local browser review/edit/retest interface with separate compile/visible/hidden results, exact response display, diff, saved-Qwen replay labeling, fresh baseline/local-Qwen modes, and separate retest evidence. Cloud generation is disabled in the UI.
- Prepared a rubric, blank human worksheet, stronger rating provenance checks, factual paper data, figure-ready CSVs, installation/reproduction commands, venue/requirements audit, video checklist, and AI-use disclosure.
- Prepared a separate local Git worktree/branch derived from the actual repository history. Preserved the sibling checkout's pre-existing dirty files. No push, history rewrite, merge to main, or submission.

## 2. Files added or modified

Core changes: `repair_providers.py`, `benchmark_runner.py`, `bug_explainer.py`, `runtime_support.py`, `evidence.py`, `summarize_results.py`, `explanation_review.py`, `verify_project.py`, `prepare_submission.py`, `run_local_comparison.py`, and tests. New continuation tools: `compare_available_cases.py`, `run_gemini_evaluation.py`, `replay_evidence.py`, `finalize_results.py`, `web_app.py`, `web/index.html`, `web/app.js`, `web/style.css`, `tests/test_integrity.py`, and `tests/test_review.py`. `.gitattributes` disables end-of-line conversion so Git preserves exact evidence bytes. `build_handoff.py` now regenerates immutable comparison data instead of outdated status prose.

Documentation: updated README/evidence index and `docs/`; added `FINAL_PAPER_DATA_GUIDE.md`, `VIDEO_DEMO_CHECKLIST.md`, this report, human-review instructions, venue checklist, reference metadata checks, requirements-source provenance, and full audit checklist. Earlier documentation is backed up under `audit/continuation_document_backups/`; the earlier handoff generator is also preserved under `audit/`. New evidence is under timestamped `results/` folders. The ZIP's `FILE_CHANGES.json` lists every changed/added deliverable against the original workspace inventory.

## 3. Verified comparison results

| System | Responses / requests | Compiles / patches | Visible success / patches | Hidden success / patches | All tests / patches | All tests / responses | Invalid | Mean generation s (n) |
|---|---|---|---|---|---|---|---:|---|
| Rule baseline | 20/20 | 17/20 | 1/20 | 2/20 | 1/20 | 1/20 | 0 | 0.000056505 (20) |
| Local Qwen | 20/20 | 13/13 | 9/13 | 10/13 | 9/13 | 9/20 | 7 | 15.431525365 (20) |
| Gemini | 10/11 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0 | 5.210724030 (10) |

| System | Category | Scheduled / responses | Compiles / patches | Hidden success / patches | All tests / responses | Invalid |
|---|---|---|---|---|---|---:|
| Rule baseline | Syntax | 4/4 | 1/4 | 1/4 | 1/4 | 0 |
| Rule baseline | Logic | 14/14 | 14/14 | 1/14 | 0/14 | 0 |
| Rule baseline | Runtime | 2/2 | 2/2 | 0/2 | 0/2 | 0 |
| Local Qwen | Syntax | 4/4 | 4/4 | 4/4 | 4/4 | 0 |
| Local Qwen | Logic | 14/14 | 7/7 | 4/7 | 3/14 | 7 |
| Local Qwen | Runtime | 2/2 | 2/2 | 2/2 | 2/2 | 0 |
| Gemini | Syntax | 4/4 | 4/4 | 4/4 | 4/4 | 0 |
| Gemini | Logic | 14/6 | 6/6 | 6/6 | 6/6 | 0 |
| Gemini | Runtime | 2/0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | 0 |

The local .env key authenticated successfully. J01 passed compilation and all tests, then the staged helper automatically continued J02-J20 with at least 65-second request spacing and no retries. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated. Requested model: gemini-3.8-flash; saved served identifier(s): gemini-3.8-flash. Quota failures: 0; service errors: 1; access errors: 0. The user personally confirmed Free Tier with billing disabled; billing was not enabled and no paid API calls were authorized. Earlier HTTP 400/blocked experiments remain historical and are excluded from this comparison.

Qwen compilation per delivered response is 13/20, versus 13/13 extracted patches. Invalid outputs stay in per-response denominators. Hidden success alone is insufficient; overall success requires every visible and hidden test. Generation timing includes delivered invalid outputs and excludes compilation/test execution. Service failures and skipped cases have no repair result. See the data guide for full definitions and settings.

J11 returned HTTP 503 UNAVAILABLE (high demand), after 31.546709000 s, with no model response. J12-J20 were skipped without requests. No retry was made. Gemini response coverage is 10/20 scheduled cases; observed delivery is 10/11 submitted requests (90.91%). The ten missing repair outcomes are unevaluated, not model failures. Runtime repair results are unavailable for Gemini.

## Common delivered cases: J01-J10

The overall table has different response coverage. Compare the same ten answered cases separately:

| System | Compiles / responses | All tests / responses | Invalid responses |
|---|---|---|---:|
| Rule baseline | 7/10 | 1/10 (10%) | 0 |
| Local Qwen | 6/10 | 5/10 (50%) | 4 |
| Gemini | 10/10 | 10/10 (100%) | 0 |

This subset contains four syntax and six logic cases, with no runtime cases. It is conditional on API delivery and is not a randomized sample or a full-suite Gemini estimate. Invalid Qwen outputs remain in the response denominator. Reproducible [tables](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/tables.md), [metrics](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/metrics.csv), and [selected case IDs](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/selection.json) preserve the derivation.

## 4. Evidence and reproduction

Authoritative index: [docs/handoff_sources.json](docs/handoff_sources.json). Factual tables/settings/limits: [FINAL_PAPER_DATA_GUIDE.md](FINAL_PAPER_DATA_GUIDE.md).

| Evidence | Location |
|---|---|
| Baseline/Qwen raw experiment | `results/runs/20261018T131412_396245Z_benchmark_41bb2533/` |
| Authenticated Gemini session / run shards | `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/session.json`; `docs/handoff_sources.json:gemini_runs` |
| Single metadata access check | `results/api_preflight/20261018T153628_997812Z_gemini_metadata_5f7d6d26/` |
| Final comparison / figure data | `results/comparisons/20261018T192905_212433Z_final_b6a6bbc3/` |
| Fresh benchmark controls | `results/validation/20261018T191851_935809Z_benchmark_controls_21cad6ec/summary.json` |
| Saved patch replays | `docs/handoff_sources.json:replays` (43 patches across three runs) |
| Gemini human worksheets | `docs/handoff_sources.json:gemini_human_worksheets` (10 delivered responses; blank scores) |
| Human worksheet | `results/explanation_reviews/20261018T154535_622694Z_worksheet_704dd1d7/ratings.csv` |
| Git comparison / checkout preservation | `audit/20261018T154603_945210Z_git_preparation_b7c4855b/` |
| Exact final ZIP/hash/checks | `submission/LATEST_SUBMISSION.json` and its verification sidecar |

```powershell
cd C:\NCAT\COMP365_Checkpoint2_Project
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe validate_benchmarks.py
.\.venv\Scripts\python.exe verify_project.py
.\.venv\Scripts\python.exe summarize_results.py results\runs\20261018T131412_396245Z_benchmark_41bb2533 --check
.\.venv\Scripts\python.exe finalize_results.py --check results\comparisons\20261018T192905_212433Z_final_b6a6bbc3
.\.venv\Scripts\python.exe compare_available_cases.py --check results\availability_comparisons\20261018T193004_385071Z_common_responses_93aa0a9f
.\.venv\Scripts\python.exe replay_evidence.py results\runs\20261018T131412_396245Z_benchmark_41bb2533
.\.venv\Scripts\python.exe web_app.py
```

Install/exact model settings and fresh experiment commands are in README. Every regeneration writes new evidence. Cloud requests are unnecessary for these checks.

## 5. Test and package outcomes

- All 33 Python regression tests passed. They cover API contracts without network, local client errors versus submitted requests, quota circuit breaking, no generation with unverified billing, hidden-test separation, invalid responses, output extraction, evidence corruption, rating provenance, web requests, edited-patch behavior, and source preservation.
- Python syntax and web JavaScript syntax checked. Dependencies checked with `pip check`; installed model/server hashes match provenance.
- All 20 original case categories and authored repairs validated; all 94 expectations verified. All 43 saved patches reproduced their outcomes. Java/C++ CLI demo patches compile.
- Original 39 source/sample/result files and 67 copied historical evidence files match preservation hashes. Baseline function AST matches its original.
- Both CSV layers and summaries reproduce for every saved run. Selected comparison CSVs/figure data reproduce and all source/prompt/test conditions match. Sealed artifact hashes verify. Exact-environment-secret and credential-pattern scans passed.
- The final package process extracts into a clean temporary directory, checks every hash/ZIP CRC, runs regression tests and all 20 benchmark controls, reproduces run/comparison tables, and checks excluded entries. Read `submission/LATEST_SUBMISSION.json`: use only a package whose verification has `passed: true`. The sidecar records exact counts, hash, file inventory, and clean-extraction outcomes after packaging finishes. Model binaries, virtual environments, credentials, Git metadata, and prior ZIPs are excluded.

## 6. GitHub branch and commit status

Actual repository: `https://github.com/Rhai2New/COMP365-Individual-Project`; base commit `778a729e9ad0ecd9d508738d05ed04ec74350429`.

Separate review worktree: **`C:\NCAT\COMP365_Final_Review_20261018`**. Local branch: **`final/technical-20261018`**. Final local commit hashes, working-tree state, and sibling preservation verification are recorded in **`submission/GIT_FINAL_STATUS.json`** after final preparation. Use `git -C C:\NCAT\COMP365_Final_Review_20261018 log -2 --oneline` to inspect them. The follow-up changes are prepared as another local commit on this same branch; the exact current hash is in the sidecar. The source workspace remains unversioned; the sibling `C:\NCAT\COMP365_Checkpoint2` retains its original uncommitted files. Local commits are allowed; no push or main merge was performed.

## 7. Remaining technical blockers and limits

1. **Gemini service availability**: J11 returned HTTP 503 UNAVAILABLE (high demand), after 31.546709000 s, with no model response. J12-J20 were skipped without requests. No retry was made. Gemini response coverage is 10/20 scheduled cases; observed delivery is 10/11 submitted requests (90.91%). The ten missing repair outcomes are unevaluated, not model failures. Runtime repair results are unavailable for Gemini. Authentication works; no credential setup remains. Completing J11-J20 requires a later separately authorized/available service window and a newly reconciled package; no retry was attempted.
2. **Human evaluation**: zero genuine human ratings. Forty earlier AI-assisted ratings remain explicitly preliminary and separate. The student must personally score/review or report this absence.
3. **Unseen instructor requirements**: Professor Pope's original feedback text and final Canvas rubric were unavailable. [Full audit](docs/FINAL_AUDIT_CHECKLIST.md) checks all known requirements and the actual proposal without claiming unseen criteria passed.
4. **Scope**: 20 self-authored Java cases, not the proposed 50-100 public Java/C++ cases. The four-second end-to-end and over-75% functional targets on the proposed scaled public dataset were not established. No participant study, significance claim, independent human test-suite review, or proven general correctness.
5. **Browser visual QA**: no browser surface available. HTTP workflow and JavaScript were verified; personally open localhost before recording. The local Java runner is not a sandbox for hostile code.

## 8. Exact student-owned next actions

1. **Research paper**: read this report and raw evidence, select supported findings, personally review explanation quality, and write the paper entirely yourself under the RED/no-AI policy. Do not convert AI documentation into paper prose. Check references yourself and distinguish preprints from publication years.
2. **Overleaf**: open your own project, use the selected SIGCSE 2027 format subject to actual course instructions, enter your own writing, compile, inspect, and export PDF. [Venue checklist](docs/VENUE_REQUIREMENTS_CHECKLIST.md) links official requirements; conference submission deadlines already passed and are distinct from today's course deadline. No Overleaf paper was generated or edited.
3. **Video**: open `web_app.py`, visually check it, record your own demonstration using [VIDEO_DEMO_CHECKLIST.md](VIDEO_DEMO_CHECKLIST.md), and verify playback/readability/link access. No narration script was written.
4. **GitHub approval**: inspect the local branch/commits and exact diff. Explicitly approve any future push; do not merge to main or force-push. Nothing is published by these local commits.
5. **Canvas**: inspect the actual final assignment/rubric, select the verified ZIP identified by `submission/LATEST_SUBMISSION.json`, add your student-written paper and video/link in required formats, submit yourself before **11:59 PM ET tonight**, and verify the receipt. No Canvas submission was performed.
6. **Credentials**: no further credential setup is needed in this workspace. Keep `.env` private. Do not repeat live experiments merely to demonstrate the project; saved evidence and local replay are available.
