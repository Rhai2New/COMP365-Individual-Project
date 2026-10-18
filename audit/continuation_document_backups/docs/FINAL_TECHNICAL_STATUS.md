# Final technical status — October 18, 2026

This is a factual technical handoff, not research-paper prose. Values below are generated from the linked saved records.

## Verified experiment

Primary run: [`20261018T131412_396245Z_benchmark_41bb2533`](../results/runs/20261018T131412_396245Z_benchmark_41bb2533/summary/tables.md), 60 case/provider records. All 20 original cases were scheduled for the baseline, Gemini, and actual local Qwen model.

| System | Responses / requests | Compiles / extracted patches | Functional / extracted patches | Functional / responses | Invalid responses | Mean response seconds (n) |
|---|---|---|---|---|---:|---|
| demo / local-rule-baseline-v1 | 20/20 (100.0%) | 17/20 (85.0%) | 1/20 (5.0%) | 1/20 (5.0%) | 0 | 0.000057 (20) |
| gemini / gemini-3.8-flash | N/A (no requests/attempts) | N/A (no requests/attempts) | N/A (no requests/attempts) | N/A (no requests/attempts) | 0 | N/A (0) |
| llama_cpp / Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | 20/20 (100.0%) | 13/13 (100.0%) | 9/13 (69.2%) | 9/20 (45.0%) | 7 | 15.431525 (20) |

Qwen test-passing cases: J01, J02, J03, J04, J06, J12, J16, J18, J20. All seven unusable Qwen responses reached the saved output-token limit. The four other extracted Qwen patches compiled but failed functional testing. These are observed failures; none were replaced or retried.

| System | Syntax functional / responses | Logic functional / responses | Runtime functional / responses |
|---|---|---|---|
| demo | 1/4 (25.0%) | 0/14 (0.0%) | 0/2 (0.0%) |
| gemini | N/A (no requests/attempts) | N/A (no requests/attempts) | N/A (no requests/attempts) |
| llama_cpp | 4/4 (100.0%) | 3/14 (21.4%) | 2/2 (100.0%) |

Service delivery was 20/20 for each local generator. Gemini made zero requests because no credential was available; its 20 unavailable rows are not repair failures or measured service outages. The earlier inventory run also recorded OpenAI/Ollama configuration unavailability. No live cloud request or paid API operation was performed.

## Technical work completed

- Preserved all original benchmark sources, manifests, sample programs, and existing results; verified 39 original files by SHA-256. The rule baseline's function AST is unchanged.
- Recovered existing Gemini support from the actual GitHub history; preserved the OpenAI adapter and added actual local Qwen inference plus optional Ollama support.
- Added unique append-only run directories, exact response text, request settings/prompts, patches/diffs, every compiler/test outcome, timing, errors, per-case CSV/JSON, run CSV, snapshots, versions, and hashes.
- Added explicit outcome categories, quota/service/access separation, no retries, a provider circuit breaker, request caps, and denominator-bearing generated tables.
- Added 58 held-out tests to the original 36 visible tests. All 20 case classifications and 94 expectations passed independent-oracle/authored-control checks. Controls are not model results.
- Updated dependencies, Windows commands, API setup, methodological limitations, historical evidence audit, explanation rubric, and AI technical assistance disclosure.
- Established the relationship to the real sibling Git checkout and matching remote HEAD without initializing this folder, changing that checkout, or pushing.

## Validation evidence

- [Final verification report](../results/verification/20261018T132107_618099Z_final_checks_468525eb/verification.json): Python syntax, 14 regression/SDK-contract tests, both runs' CSV/summary/hash consistency, prompt reconstruction, preservation, and credential-pattern scan passed.
- [Benchmark control validation](../results/validation/20261018T131002_378932Z_benchmark_controls_8446b998/summary.json): 20/20 category checks and authored repairs pass; all 94 expected outputs verified.
- Java and C++ interactive demo compilation checks passed, with fresh evidence under `results/interactive/`; functional results come from the Java benchmark, not these smoke checks.
- The original historical screenshot was visually inspected; it contains a demo compile result and no credential. The text credential-pattern scan reported no matches in project/evidence/audit files; model/dependency caches and binary files were excluded.

## Explanation review

A rubric, editable human-review worksheet, structural checks, and 40 preliminary AI-assisted ratings are saved separately from the sealed experiments. These are single-rater AI judgments and must be independently reviewed before use as explanation-quality evidence. They are not human learning-effectiveness measurements.

| Provider | AI-assisted rated responses | Mean preliminary total / 8 |
|---|---:|---:|
| demo | 20 | 2.20 |
| llama_cpp | 20 | 1.90 |

[Review summary and source ratings](../results/explanation_reviews/20261018T132222_582045Z_scored_f320519e/summary.csv). Successful patches sometimes have incorrect explanations; patch success was not used as a proxy for explanation accuracy.

## Incomplete requirements and practical limits

- A fresh complete three-system evaluation remains incomplete: baseline and actual local Qwen were evaluated; Gemini needs a working key and confirmed quota. OpenAI is implemented but not evaluated.
- Historical CSVs support claims for only J01–J03; the corresponding saved response files were overwritten by quota errors. The eight-success and average-time claims remain unverified and are excluded.
- Five fixed-output/no-input programs cannot receive independent input-based output checks without changing their original tasks. Their held-out ignored-input tests provide limited additional assurance.
- Only small self-authored Java cases were evaluated. Public benchmark expansion, broader domains, repeated stochastic trials, human educational validation, and statistical significance were not completed or claimed.
- The local model is small and quantized. Latencies include local request overhead; they are not comparable to a cloud provider with no measured responses. Output-cap failures remain part of the observed result.
- Python 3.8 from the machine's default `python` is unsupported; use the documented Python 3.12 commands. The optional model setup helper downloads Windows x64 binaries; other platforms need an equivalent documented local server setup.
- The working copy remains unversioned. GitHub integration/push and the LMS upload have not been performed.

The student must independently review scores/results, write the RED/no-AI paper, record their own video, approve any GitHub push, and complete the actual LMS submission. See [the student checklist](STUDENT_SUBMISSION_CHECKLIST.md).
