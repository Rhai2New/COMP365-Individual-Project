# Results and evidence index

Primary final comparison: [20261018T131412_396245Z_benchmark_41bb2533](runs/20261018T131412_396245Z_benchmark_41bb2533/summary/tables.md). This includes an actual 20-case baseline and local Qwen run, plus explicitly unavailable Gemini records.

| Directory | Contents |
|---|---|
| `runs/` | Unique benchmark runs; per-case JSON/CSV and full artifacts, source snapshots, checksums, generated tables |
| `validation/` | Classification/oracle checks and authored positive controls, separate from model results |
| `verification/` | Syntax, regression, evidence-consistency, preservation, and credential-pattern audits |
| `interactive/` | Fresh Java/C++ demo evidence; compilation smoke checks only |
| `explanation_reviews/` | Editable human worksheets, structural checks, explicitly AI-assisted preliminary ratings |
| `historical_checkpoint2_checkout/` | Unchanged copied evidence from the actual sibling checkout, with hash provenance |
| `historical_audits/` | Generated inventory of historical Gemini CSV claims and overwritten response evidence |
| `server_logs/` | Local llama.cpp startup/version/runtime logs and exact launch command |

Original top-level CSV/TXT/PNG files and `outputs/` are historical and preserved unchanged. They are excluded from current experiment tables. Never pool repeated CSV rows or unverified historical claims as distinct successes.

To check a saved run: `python summarize_results.py results/runs/RUN_DIRECTORY --check` using Python 3.10+ (on this machine, use `.venv/Scripts/python.exe` or `py -3.12`). To regenerate into a new directory, omit `--check`.
