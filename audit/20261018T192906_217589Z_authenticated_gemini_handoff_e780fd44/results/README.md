# Evidence index

Current paths: [docs/handoff_sources.json](../docs/handoff_sources.json).

- Primary baseline/Qwen run: `runs/20261018T131412_396245Z_benchmark_41bb2533`.
- Actual Gemini smoke: `gemini_sessions/20261018T165537_356590Z_staged_5cca6e5c/runs/20261018T165537_647234Z_benchmark_d0b0ae7b` (one HTTP 400, no response).
- Remaining Gemini cases: `runs/20261018T165729_486199Z_benchmark_d3df46ae` (19 skipped, no requests). Earlier billing-blocked evidence is historical.
- Final comparison: `comparisons/20261018T165842_557570Z_final_a1ed1438`.

| Folder | Meaning |
|---|---|
| `runs/` | Sealed experimental or explicit unavailability records |
| `comparisons/` | Selected-run metrics, case CSV, tables, figure-ready data, source seals |
| `api_preflight/` | Credential presence and single metadata-request status; not a benchmark response |
| `validation/` | Authored controls and Python expectation checks; not model repairs |
| `replays/` | Fresh execution of saved patches; not more model trials |
| `interactive/` | Java/C++ CLI compilation smoke checks |
| `web_reviews/` | Fresh local UI generation and retests; excluded from primary comparison |
| `explanation_reviews/` | Blank human worksheets and separately labeled preliminary AI ratings |
| `verification/` | Regression/syntax, preservation, secret scans, raw evidence/CSV/summary checks |
| `server_logs/` | Exact local launch command and runtime metadata |
| `historical_checkpoint2_checkout/`, `historical_audits/` | Preserved history and unsupported-claim inventory |

Top-level results and `outputs/` are historical and excluded. Use `summarize_results.py RUN --check` for an experiment and `finalize_results.py --check DIRECTORY` for the comparison. Full commands are in the root README.
