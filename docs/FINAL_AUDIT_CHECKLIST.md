# Final technical audit and scope reconciliation

Sources: the user's October 18 requirements, checkpoint evidence, the [student proposal](https://docs.google.com/document/d/1r90jC-yk4t5z8vx2VfqlwlTklgsz-0PEWEe-juHo2XQ/edit), and `requirements_sources.json`. Professor Pope's original feedback text and the final Canvas rubric were not found. The proposal has no Drive comments; targeted Gmail searches returned no matching feedback. This checks all known requirements and cannot certify unseen criteria.

| Requirement / concern | Status | Evidence / remaining action |
|---|---|---|
| Preserve exact outputs; prevent overwriting | Complete | Unique folders, raw responses/envelopes, source/prompt/patch/test files, CSV/JSON, hashes; historical evidence preserved |
| Three actual systems evaluated | Partial cloud coverage | Gemini J01-J10 passed; J11 HTTP 503; J12-J20 skipped. Common-case results reported separately. |
| Same source, prompt, caps, tests | Verified | Comparison source/prompt/test hashes checked for all 20 cases |
| Actual Qwen identity | Verified | Official pinned GGUF revision/hash, server hash/build/fingerprint, saved configuration |
| Actual Gemini served version | Recorded | `gemini-3.8-flash` from actual response envelopes |
| Syntax, logic, runtime breakdown | Complete | 4/14/2 cases; generated category metrics |
| Compilation distinct from functionality | Complete | Separate compiler, visible, hidden, and all-test outcomes |
| Correct denominators / service failures | Complete | Invalid outputs included per response; unavailable rows have no repair denominator; metadata call outside benchmark |
| All Java cases and hidden outputs | Passed | 20 category checks, 94 expectations, authored controls; 43 saved patches replayed |
| Explanation quality | Human work pending | Rubric, blank worksheet, provenance checks; 40 preliminary AI judgments labeled separately |
| Browser review/edit/apply/retest promised in proposal | Implemented; HTTP-tested | `web_app.py`, `web/`; fresh local generation, labeled replay, editable patch, separate retest evidence |
| UI visual inspection | Unavailable | No browser surface; student should open localhost before recording |
| Public datasets / 50-100 Java/C++ cases promised | Scope not reached | Actual experiments: 20 self-authored Java cases; no QuixBugs/Defects4J or C++ benchmark claim |
| Under-four-second end-to-end target | Not established | Qwen mean generation alone is 15.431525 s; compilation/browser latency excluded |
| Over-75% functional target on scaled dataset | Not established | 20-case results cannot establish the proposed scaled public-dataset target; see all three systems in the data guide |
| Regression, syntax, reproducibility | Passed | Verification logs; comparison regeneration; patch/envelope/diff/split-result checks |
| Safe Git preparation | Separate branch/worktree | Sibling dirty files preserved; inspect local commits before approving push |
| Technical package | Sidecar is authority | `submission/LATEST_SUBMISSION.json`: extraction hashes, regression tests, 20 controls, summary/table reproduction |
| Credentials / model binaries | Scanned / excluded | .env and backups excluded from Git/ZIP/snapshots; placeholder-only example; pattern and exact-secret scans on deliverables; cache/binary exclusions |
| Persistent local authentication | Complete | Automatic project .env loading, precedence over stale Windows values, blank-field no-network guard, six dedicated regression tests; local secret populated privately by the user and authentication verified; no repeated setup needed |
| Paper, Overleaf, video, Canvas | Student-owned | No paper writing, upload, conference submission, push, or merge performed |

Limits: one generation per case, small curated suite, no participant study or statistical significance, exact-output tests on a limited domain, and five programs whose ignored-input hidden checks add little behavioral coverage. Tests and technical controls were AI-assisted; an independent human test-suite review is not claimed. See `EVALUATION_METHODOLOGY.md`.
