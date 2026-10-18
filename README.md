# Interactive Code Bug Explainer & Patch Generator

COMP 365 technical artifact, October 18, 2026. Start with [FINAL_READY_REPORT.md](FINAL_READY_REPORT.md). The RED/no-AI research paper is written separately by the student.

## Install and verify

Windows PowerShell; Python 3.10+ and a JDK required. Tested with Python 3.12.1 and OpenJDK 23.0.1. This machine's default Python 3.8 is unsupported.

```powershell
cd C:\NCAT\COMP365_Checkpoint2_Project
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe validate_benchmarks.py
.\.venv\Scripts\python.exe verify_project.py
```

`requirements.txt` pins the cloud SDKs; the lock file records the tested environment. Baseline, local HTTP adapters, and web app use the standard library. SDK tests use mocks and need installed SDKs. Java is discovered from PATH/JAVA_HOME and common Windows JDK folders. C++ checks require `g++`.

## Browser review/edit/retest

```powershell
.\.venv\Scripts\python.exe web_app.py
```

Open **http://127.0.0.1:8365**. Choose a case/system, request an explanation, inspect source/patch/diff, edit the patch, then click **Approve current patch and retest**. Compilation, visible tests, held-out tests, and exact response appear separately. Fresh generations/retests save unique `results/web_reviews/` folders without changing benchmarks or primary results. Saved Qwen is explicitly a replay with original timing; live Qwen requires a local server. Cloud calls are disabled in the UI.

The server binds to loopback, checks Host/Origin and JSON requests, and serves only its static assets. It executes Java with local user permissions and timeouts: use trusted code, not hostile uploads or public hosting. HTTP behavior, edited patches, source preservation, and JavaScript syntax were tested. Browser visual inspection was unavailable in this session.

## Actual systems and findings

| Provider | Exact system | Observed functional result |
|---|---|---|
| `demo` | Unchanged `local-rule-baseline-v1` | 1/20 delivered responses passes all tests |
| `llama_cpp` | Qwen2.5-Coder-0.5B-Instruct GGUF Q4_K_M | 9/20 passes all tests; 7 invalid outputs |
| `gemini` | Requested `gemini-3.8-flash`; served version unknown | J01 HTTP 400; no response; J02-J20 skipped |
| `openai`, `ollama` | Preserved optional adapters | Not evaluated |

Evidence paths: [docs/handoff_sources.json](docs/handoff_sources.json). One Google models-metadata GET returned HTTP 400, without retry. The user has personally confirmed Free Tier with billing disabled. The staged J01 generation attempt returned HTTP 400 with no model response; the saved credential contains control characters and needs private correction. J02-J20 were skipped without requests. These are access limitations, not Gemini repair failures. The requested ID appears in [Google's model catalogue](https://ai.google.dev/gemini-api/docs/models); this does not prove account access or served version.

## Reproduce saved evidence without model calls

```powershell
.\.venv\Scripts\python.exe summarize_results.py results\runs\20261018T131412_396245Z_benchmark_41bb2533 --check
.\.venv\Scripts\python.exe replay_evidence.py results\runs\20261018T131412_396245Z_benchmark_41bb2533
.\.venv\Scripts\python.exe finalize_results.py --check results\comparisons\20261018T165842_557570Z_final_a1ed1438
.\.venv\Scripts\python.exe finalize_results.py
```

The last command creates new tables and figure-ready CSVs. Comparison checks identical source, full prompts, tests, and output caps. Original runs remain sealed. Historical claims, controls, replays, UI edits, and duplicate trials are excluded. `build_handoff.py` is a compatibility entry point for immutable regeneration.

## Fresh local experiments

```powershell
.\.venv\Scripts\python.exe benchmark_runner.py --providers demo
.\.venv\Scripts\python.exe setup_local_model.py
.\.venv\Scripts\python.exe run_local_comparison.py
```

Setup downloads pinned official Windows CPU llama.cpp b11719 and a 491 MB official Qwen GGUF into ignored `.tools/`. URLs, revision, licenses, and hashes: `local_model_provenance.json`. The helper checks hashes, starts a hidden loopback server, evaluates with cloud calls disabled, then stops its own server. Request settings: temperature 0, seed 365, 2,048 output tokens, prompt-cache reuse disabled, timeout 120 seconds. Server: context 4,096, eight CPU threads, one slot. To keep a server for the UI, run the executable/arguments recorded in `results/server_logs/*/command.json` in another terminal; stop with Ctrl+C. [Qwen card](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF), [llama.cpp docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Gemini: verify free access before generation

The application reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the process or Windows user environment without printing it. It does not load `.env` files. Never put a key in commands, reports, source, or Git. In [AI Studio Projects](https://aistudio.google.com/projects), verify the exact key's project is Free Tier with billing disabled, its model is accessible, and quota remains. Public pricing does not prove account tier. References: [billing](https://ai.google.dev/gemini-api/docs/billing), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

Only after resolving access and verifying those conditions:

```powershell
.\.venv\Scripts\python.exe run_gemini_evaluation.py --model gemini-3.8-flash --free-tier-confirmed
```

The helper sends one J01 request first and the remaining 19 only after a delivered smoke response. Evidence goes under `results/gemini_sessions/`. It spaces starts by at least 65 seconds, disables retries/fallback, and stops further calls after API/quota failure. Spacing does not guarantee available project quota. Do not run with uncertain or paid billing, or repeatedly retry a failed request. Failed smoke sessions now also save explicit skipped-case evidence linked to the failed run, without making further network requests. Comparisons accept repeated `--gemini RUN` arguments to combine smoke and remaining-case shards. Reconcile any new observations and rebuild the ZIP before reporting them.

The underlying runner requires `--allow-live` and `--gemini-free-tier-confirmed`, with a default cap of one cloud request. Interactive Gemini requires both flags. Optional OpenAI requires an explicit model, uses Responses with `store=False`, output cap/timeout and `max_retries=0`, and was not called. Ollama requires a local endpoint and exact installed tag.

## CLI and packaging

```powershell
.\.venv\Scripts\python.exe bug_explainer.py --source samples\BuggyGreeting.java --provider demo
.\.venv\Scripts\python.exe bug_explainer.py --source samples\BuggyTotal.cpp --provider demo
.\.venv\Scripts\python.exe prepare_submission.py
```

CLI examples verify compilation; benchmark tests establish functionality. Packaging excludes credentials, caches/dependencies, model/runtime binaries, Git metadata, and previous ZIPs. It scans patterns and exact environment secrets, extracts into a clean directory, checks every hash, runs regression tests/all 20 controls, and reproduces summaries/comparisons. The sidecar verification report is authoritative. `SUBMISSION_MANIFEST.json` and `FILE_CHANGES.json` are inside the ZIP.

See [data guide](FINAL_PAPER_DATA_GUIDE.md), [video checklist](VIDEO_DEMO_CHECKLIST.md), [venue checklist](docs/VENUE_REQUIREMENTS_CHECKLIST.md), [audit](docs/FINAL_AUDIT_CHECKLIST.md), [methodology](docs/EVALUATION_METHODOLOGY.md), [rubric](docs/EXPLANATION_RUBRIC.md), [human review](docs/HUMAN_EXPLANATION_REVIEW.md), and [AI disclosure](docs/AI_ASSISTANCE_DISCLOSURE.md). Earlier READMEs/results are preserved historical materials. QuixBugs/Defects4J were proposed but not evaluated. Nothing has been pushed or submitted.
