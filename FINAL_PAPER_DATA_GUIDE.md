# Verified technical data guide

Factual lookup material only. This is not paper prose. Write the RED/no-AI paper yourself; do not paste AI-authored documentation into it as student-written text.

## Evidence authority

- Baseline/Qwen experiment: `results/runs/20261018T131412_396245Z_benchmark_41bb2533/`.
- Actual Gemini smoke request: `results/gemini_sessions/20261018T165537_356590Z_staged_5cca6e5c/runs/20261018T165537_647234Z_benchmark_d0b0ae7b/`. J02-J20 skipped records: `results/runs/20261018T165729_486199Z_benchmark_d3df46ae/`. Earlier billing-blocked records remain historical.
- Selected comparison: [tables](results/comparisons/20261018T165842_557570Z_final_a1ed1438/tables.md), [metrics CSV](results/comparisons/20261018T165842_557570Z_final_a1ed1438/metrics.csv), [per-case results](results/comparisons/20261018T165842_557570Z_final_a1ed1438/case_results.csv), [figure-ready data](results/comparisons/20261018T165842_557570Z_final_a1ed1438/figure_ready_data.csv).
- Every case directory contains the actual prompt/source, response/envelope when one exists, extracted patch/diff when one exists, original and patched evaluation records, and matching JSON/CSV. Source seals and identical source/prompt/test checks: comparison `sources.json`.

## Overall observations

| System | Responses / requests | Compiles / extracted patches | Visible success / patches | Hidden success / patches | All tests / patches | All tests / responses | Invalid outputs | Mean generation seconds (n) |
|---|---|---|---|---|---|---|---:|---|
| Rule baseline | 20/20 | 17/20 (85%) | 1/20 | 2/20 | 1/20 (5%) | 1/20 (5%) | 0 | 0.000056505 (20) |
| Local Qwen | 20/20 | 13/13 (100%) | 9/13 | 10/13 | 9/13 (69.23%) | 9/20 (45%) | 7 | 15.431525365 (20) |
| Gemini | 0/1 (access error) | N/A | N/A | N/A | N/A | N/A | 0 received | N/A (0) |

Qwen compiles on 13/20 delivered responses (65%) when invalid responses stay in the denominator. Compilation and all-tests success measure different outcomes. Hidden success alone is insufficient: some patches pass hidden checks while failing visible checks. Delivered-response latency includes invalid outputs and excludes compilation/test execution. Local baseline timing is a function call, not browser response time. Gemini delivery was 0/1 submitted requests, with one HTTP 400 access error; this single request does not establish a general service outage. Failed-request latency was 2.081643800 s (n=1), not model-response latency. J01 has no response/repair result; J02-J20 were skipped without requests. All 20 lack usable repair outcomes.

## Categories

| System | Category | Cases / responses | Compiles / patches | Hidden success / patches | All tests / responses | Invalid |
|---|---|---|---|---|---|---:|
| Baseline | Syntax | 4/4 | 1/4 | 1/4 | 1/4 (25%) | 0 |
| Baseline | Logic | 14/14 | 14/14 | 1/14 | 0/14 (0%) | 0 |
| Baseline | Runtime | 2/2 | 2/2 | 0/2 | 0/2 (0%) | 0 |
| Qwen | Syntax | 4/4 | 4/4 | 4/4 | 4/4 (100%) | 0 |
| Qwen | Logic | 14/14 | 7/7 | 4/7 | 3/14 (21.43%) | 7 |
| Qwen | Runtime | 2/2 | 2/2 | 2/2 | 2/2 (100%) | 0 |
| Gemini | Syntax / logic / runtime | 4 / 14 / 2 scheduled; zero responses | N/A | N/A | N/A | 0 received |

Baseline test-passing case: J01. Qwen test-passing cases: J01, J02, J03, J04, J06, J12, J16, J18, J20. All seven unusable Qwen responses hit the saved output-token cap. Four other extracted Qwen patches compile but fail functional testing. There were no submitted-request failures in the primary local runs.

## Model and evaluation settings

| Item | Verified value / authority |
|---|---|
| Baseline | `local-rule-baseline-v1`; original `demo_response` AST unchanged |
| Qwen | Official `Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF`, Q4_K_M, revision `ebb2015119c907b064c512bf053e945850b5875f` |
| Model SHA-256 | `1d9614638d18024d0fbb36575a15f1302a3adf044df10345688ec4f6e1c4ff32` |
| Local runtime | llama.cpp b11719; response fingerprint `b11719-5aeac37a3`; pinned executable hash in `local_model_provenance.json` |
| Local request/server | Temperature 0; seed 365; 2,048 output tokens; cache reuse disabled; timeout 120 s; context 4,096; 8 CPU threads; 1 slot |
| Gemini | Requested `gemini-3.8-flash`; actual served version unknown; requested temperature 0/output cap 2,048; one request failed before any model response |
| Software | Python 3.12.1; OpenJDK/javac 23.0.1; google-genai 2.31.0; openai 2.54.0; full lock file |
| Cases | 20 self-authored Java micro-benchmarks: 4 syntax, 14 logic, 2 runtime |
| Tests | 36 original visible + 58 held-out = 94; all expectations verified by Python oracles and authored Java controls |
| Prompt | `bug_explainer.py:SYSTEM_INSTRUCTIONS`; each case's exact `prompt.json`/`prompt.txt`; original source plus visible failures only |
| Protocol | One response per case/system, no retries or iterative repair; hidden tests excluded from prompts; exact-output normalization documented in methodology |

Google's [model catalogue](https://ai.google.dev/gemini-api/docs/models) confirms the public requested ID, not access for this account. The single models-metadata GET returned HTTP 400; only its status/error summary was retained, not the detailed HTTP error body. In the later authorized follow-up, the user personally confirmed Free Tier with billing disabled. The staged helper submitted J01 once; it returned HTTP 400 with an HTML error and no model response. The saved value contains control characters and no recognizable Google API key could be extracted. There was no whitespace/quote, proxy, base-URL, or Vertex-mode correction to apply, and no evidence of a model-ID-specific rejection. No retry or model cycling followed. Credential validity/access remain unresolved; billing is no longer the blocker. [Billing verification](https://ai.google.dev/gemini-api/docs/billing) requires the account's project tier; [active limits](https://ai.google.dev/gemini-api/docs/rate-limits) are project-specific. No paid generation requests were made.

## Explanation evaluation

- Rubric: four dimensions, 0-2 each, total 0-8; root-cause accuracy, repair reasoning, beginner clarity, case specificity.
- Genuine human ratings currently available: **zero**.
- Earlier preliminary AI-assisted ratings: 20 baseline responses, mean 2.20/8; 20 Qwen responses, mean 1.90/8. These are AI judgments, not independent human findings or learning-effectiveness results.
- Blank human worksheet: `results/explanation_reviews/20261018T154535_622694Z_worksheet_704dd1d7/ratings.csv`. Procedure: [human review](docs/HUMAN_EXPLANATION_REVIEW.md). Preliminary sources: `results/explanation_reviews/20261018T132222_582045Z_scored_f320519e/`.

## Limits and unsupported claims to avoid

- Passing the saved tests does not prove general program correctness, educational effectiveness, or explanation accuracy.
- Five fixed-output programs have ignored-input held-out checks with limited added coverage. The input domain excludes overflow and unspecified cases; controls/tests were AI-assisted.
- Small curated Java suite, single generation per case, no participant study, no statistical significance, no public QuixBugs/Defects4J experiment, no C++ benchmark evaluation. C++ has compilation smoke checks only.
- The proposal's 50-100 public Java/C++ cases, under-four-second end-to-end latency, and over-75% functional target were not established by this experiment. The local Qwen mean generation time alone exceeds four seconds.
- Historical CSV claims are excluded: only J01-J03 have distinct historical successful Gemini CSV entries, and successful response text was overwritten by later quota errors. The historical eight-success/average-time claim is unverified.
- Browser workflow was HTTP/functionally tested; visual inspection was unavailable. UI replay and edited-patch retests are not new benchmark trials.

## Reproduction and references

Use the root README commands for `validate_benchmarks.py`, `replay_evidence.py`, `summarize_results.py --check`, and `finalize_results.py --check`. Final technical verification is indexed by `docs/handoff_sources.json`; the final ZIP sidecar records clean-extraction tests.

Selected venue: SIGCSE 2027, established from the existing student proposal. See [venue requirements](docs/VENUE_REQUIREMENTS_CHECKLIST.md), [reference metadata checks](docs/REFERENCE_VERIFICATION.md), existing `RELATED_WORKS.md`, and the official model/runtime sources linked in README. Read and select your own references; no paper text or bibliography was written.
