# Evidence index

Current paths: [docs/handoff_sources.json](../docs/handoff_sources.json).

- Primary baseline/Qwen run: `runs/20261018T131412_396245Z_benchmark_41bb2533`.
- Authenticated Gemini session: `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/session.json`. Exact selected shards are in `docs/handoff_sources.json:gemini_runs`. Earlier access failures remain historical.
- Final comparison: `comparisons/20261018T192905_212433Z_final_b6a6bbc3`.

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

- Common delivered J01-J10 comparison: `results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f`; generated separately from the full scheduled-case table.
