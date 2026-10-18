# Verified technical data guide

Factual lookup material only. This is not paper prose. Write the RED/no-AI paper yourself; do not paste AI-authored documentation into it as student-written text.

## Evidence authority

- Baseline/Qwen experiment: `results/runs/20261018T131412_396245Z_benchmark_41bb2533/`.
- Authenticated Gemini session: `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/session.json`. Selected run shards: `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/runs/20261018T191710_229284Z_benchmark_876caa4e`; `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/runs/20261018T191824_916274Z_benchmark_b71c7f0b`. Earlier failed/blocked sessions remain historical.
- Selected comparison: [tables](results/comparisons/20261018T192905_212433Z_final_b6a6bbc3/tables.md), [metrics CSV](results/comparisons/20261018T192905_212433Z_final_b6a6bbc3/metrics.csv), [per-case results](results/comparisons/20261018T192905_212433Z_final_b6a6bbc3/case_results.csv), [figure-ready data](results/comparisons/20261018T192905_212433Z_final_b6a6bbc3/figure_ready_data.csv).
- Every case directory contains the actual prompt/source, response/envelope when one exists, extracted patch/diff when one exists, original and patched evaluation records, and matching JSON/CSV. Source seals and identical source/prompt/test checks: comparison `sources.json`.

## Overall observations

| System | Responses / requests | Compiles / patches | Visible success / patches | Hidden success / patches | All tests / patches | All tests / responses | Invalid | Mean generation s (n) |
|---|---|---|---|---|---|---|---:|---|
| Rule baseline | 20/20 | 17/20 | 1/20 | 2/20 | 1/20 | 1/20 | 0 | 0.000056505 (20) |
| Local Qwen | 20/20 | 13/13 | 9/13 | 10/13 | 9/13 | 9/20 | 7 | 15.431525365 (20) |
| Gemini | 10/11 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0 | 5.210724030 (10) |

Qwen compiles on 13/20 delivered responses (65%) when invalid responses stay in the denominator. Compilation and all-tests success measure different outcomes. Hidden success alone is insufficient: some patches pass hidden checks while failing visible checks. Delivered-response latency includes invalid outputs and excludes rate-limit waiting, compilation/test execution. Local baseline timing is a function call, not browser response time. The local .env key authenticated successfully. J01 passed compilation and all tests, then the staged helper automatically continued J02-J20 with at least 65-second request spacing and no retries. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated. Requested model: gemini-3.8-flash; saved served identifier(s): gemini-3.8-flash. Quota failures: 0; service errors: 1; access errors: 0. The user personally confirmed Free Tier with billing disabled; billing was not enabled and no paid API calls were authorized. Earlier HTTP 400/blocked experiments remain historical and are excluded from this comparison.

J11 returned HTTP 503 UNAVAILABLE (high demand), after 31.546709000 s, with no model response. J12-J20 were skipped without requests. No retry was made. Gemini response coverage is 10/20 scheduled cases; observed delivery is 10/11 submitted requests (90.91%). The ten missing repair outcomes are unevaluated, not model failures. Runtime repair results are unavailable for Gemini.

## Common delivered cases: J01-J10

The overall table has different response coverage. Compare the same ten answered cases separately:

| System | Compiles / responses | All tests / responses | Invalid responses |
|---|---|---|---:|
| Rule baseline | 7/10 | 1/10 (10%) | 0 |
| Local Qwen | 6/10 | 5/10 (50%) | 4 |
| Gemini | 10/10 | 10/10 (100%) | 0 |

This subset contains four syntax and six logic cases, with no runtime cases. It is conditional on API delivery and is not a randomized sample or a full-suite Gemini estimate. Invalid Qwen outputs remain in the response denominator. Reproducible [tables](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/tables.md), [metrics](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/metrics.csv), and [selected case IDs](results/availability_comparisons/20261018T193004_385071Z_common_responses_93aa0a9f/selection.json) preserve the derivation.

## Categories

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

Baseline test-passing case: J01. Qwen test-passing cases: J01, J02, J03, J04, J06, J12, J16, J18, J20. All seven unusable Qwen responses hit the saved output-token cap. Four other extracted Qwen patches compile but fail functional testing. There were no submitted-request failures in the primary local runs. Gemini test-passing cases: J01, J02, J03, J04, J05, J06, J07, J08, J09, J10.

## Model and evaluation settings

| Item | Verified value / authority |
|---|---|
| Baseline | `local-rule-baseline-v1`; original `demo_response` AST unchanged |
| Qwen | Official `Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF`, Q4_K_M, revision `ebb2015119c907b064c512bf053e945850b5875f` |
| Model SHA-256 | `1d9614638d18024d0fbb36575a15f1302a3adf044df10345688ec4f6e1c4ff32` |
| Local runtime | llama.cpp b11719; response fingerprint `b11719-5aeac37a3`; pinned executable hash in `local_model_provenance.json` |
| Local request/server | Temperature 0; seed 365; 2,048 output tokens; cache reuse disabled; timeout 120 s; context 4,096; 8 CPU threads; 1 slot |
| Gemini | Requested `gemini-3.8-flash`; served `gemini-3.8-flash`; temperature 0; output cap 2,048; timeout 120 s; SDK retry attempts 1 (no retries); default thinking/sampling settings otherwise |
| Software | Python 3.12.1; OpenJDK/javac 23.0.1; google-genai 2.31.0; openai 2.54.0; full lock file |
| Cases | 20 self-authored Java micro-benchmarks: 4 syntax, 14 logic, 2 runtime |
| Tests | 36 original visible + 58 held-out = 94; all expectations verified by Python oracles and authored Java controls |
| Prompt | `bug_explainer.py:SYSTEM_INSTRUCTIONS`; each case's exact `prompt.json`/`prompt.txt`; original source plus visible failures only |
| Protocol | One response per case/system, no retries or iterative repair; hidden tests excluded from prompts; exact-output normalization documented in methodology |

The local .env key authenticated successfully. J01 passed compilation and all tests, then the staged helper automatically continued J02-J20 with at least 65-second request spacing and no retries. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated. Requested model: gemini-3.8-flash; saved served identifier(s): gemini-3.8-flash. Quota failures: 0; service errors: 1; access errors: 0. The user personally confirmed Free Tier with billing disabled; billing was not enabled and no paid API calls were authorized. Earlier HTTP 400/blocked experiments remain historical and are excluded from this comparison. Official [model catalogue](https://ai.google.dev/gemini-api/docs/models), [Free Tier pricing](https://ai.google.dev/gemini-api/docs/pricing), and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) were checked on October 18, 2026. Public prices do not establish account tier; the user supplied that attestation.

## Explanation evaluation

- Rubric: four dimensions, 0-2 each, total 0-8; root-cause accuracy, repair reasoning, beginner clarity, case specificity.
- Genuine human ratings currently available: **zero**.
- Earlier preliminary AI-assisted ratings: 20 baseline responses, mean 2.20/8; 20 Qwen responses, mean 1.90/8. These are AI judgments, not independent human findings or learning-effectiveness results.
- Blank human worksheet: `results/explanation_reviews/20261018T154535_622694Z_worksheet_704dd1d7/ratings.csv`. Procedure: [human review](docs/HUMAN_EXPLANATION_REVIEW.md). Preliminary sources: `results/explanation_reviews/20261018T132222_582045Z_scored_f320519e/`.

- Additional blank Gemini worksheets (one per run shard): `results/explanation_reviews/20261018T192906_275469Z_worksheet_f153bd84/ratings.csv`; `results/explanation_reviews/20261018T192906_526278Z_worksheet_36b1ff42/ratings.csv`. All rating fields remain blank; there are no new AI-assigned Gemini scores.

## Limits and unsupported claims to avoid

- Passing the saved tests does not prove general program correctness, educational effectiveness, or explanation accuracy.
- Five fixed-output programs have ignored-input held-out checks with limited added coverage. The input domain excludes overflow and unspecified cases; controls/tests were AI-assisted.
- Small curated Java suite, single generation per case, no participant study, no statistical significance, no public QuixBugs/Defects4J experiment, no C++ benchmark evaluation. C++ has compilation smoke checks only.
- The proposal's 50-100 public Java/C++ cases, under-four-second end-to-end latency, and over-75% functional target on the proposed scaled public dataset were not established by this experiment, regardless of Gemini performance on these 20 cases. The local Qwen mean generation time alone exceeds four seconds.
- Historical CSV claims are excluded: only J01-J03 have distinct historical successful Gemini CSV entries, and successful response text was overwritten by later quota errors. The historical eight-success/average-time claim is unverified.
- Browser workflow was HTTP/functionally tested; visual inspection was unavailable. UI replay and edited-patch retests are not new benchmark trials.

- Served Gemini identifiers are recorded exactly as returned; the alias is not an immutable weight revision. Gemini default thinking was not disabled. Equal prompts and requested output caps do not equalize internal reasoning budgets, model capacity, quantization, or hardware. Qwen ran locally on CPU; Gemini ran remotely.

## Reproduction and references

Use the root README commands for `validate_benchmarks.py`, `replay_evidence.py`, `summarize_results.py --check`, and `finalize_results.py --check`. Final technical verification is indexed by `docs/handoff_sources.json`; the final ZIP sidecar records clean-extraction tests.

Selected venue: SIGCSE 2027, established from the existing student proposal. See [venue requirements](docs/VENUE_REQUIREMENTS_CHECKLIST.md), [reference metadata checks](docs/REFERENCE_VERIFICATION.md), existing `RELATED_WORKS.md`, and the official model/runtime sources linked in README. Read and select your own references; no paper text or bibliography was written.
