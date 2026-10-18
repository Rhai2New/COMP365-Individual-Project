# Technical evaluation protocol

## Dataset and unit of analysis

Retain the existing 20 self-authored Java micro-benchmarks: 4 syntax, 14 logic, and 2 runtime cases. The unit is one case/provider generation with no repair-feedback iterations and no retry. `validate_benchmarks.py` verifies that syntax originals fail compilation, logic originals compile but fail behavior without a process exception, and runtime originals compile and produce a nonzero runtime exit on at least one supplied test. It checks authored positive-control repairs and independently computes all test expectations using Python oracles. Positive controls verify the harness; they are never model outputs, baseline repairs, or experimental successes.

The original 36 visible tests remain in `benchmarks/manifest.json`. `benchmarks/hidden_tests.json` adds 58 held-out tests across all 20 cases, for 94 tests total. For the 15 programs that consume input, these cover new values and boundaries: negative/zero values, equality, exact age limits, integer-division signs, empty counted sequences where defined, string case/whitespace, and zero divisors. No behavior is specified outside this small input domain (for example, empty maximum arrays and integer overflow are not tested).

J01?J04 and J12 take no input. Their additional tests supply ignored input and repeat the fixed behavior in fresh JVMs. They are withheld but add no independent output oracle, and cannot exclude output hardcoding. This is a documented limitation of preserving the fixed original programs. New generalization claims would require parameterized cases or a separately labeled mutation study; neither is claimed here.

## Prompt and test separation

The prompt contains only shared system instructions, language, the original source, and actual failures from visible tests or compilation. It excludes case titles, bug labels, authored controls, hidden tests, and any reference patch. All providers receive identical system/user content; API transport formats differ. The baseline's narrow rule logic is unchanged. Hidden tests are run after generation and are never used for retry feedback. They are stored in the reproducibility artifact and therefore are hidden from the model prompt, not secret from a repository reader. Source filenames may be visible in actual compiler diagnostics.

Compilation uses a temporary build directory, UTF-8, and disabled annotation processing with a 20-second limit. Each test uses a separate JVM, a five-second limit, and a 128 MB heap. Stdout and stderr are saved separately. Passing requires exit code zero and stdout matching expected output after normalizing line endings, trimming outer whitespace, and trimming trailing whitespace per line. Nonzero exit, timeout, or mismatch fails a test. Overall success requires compilation and every visible and hidden test. Child processes do not inherit environment variables whose names contain API_KEY, SECRET, TOKEN, or PASSWORD. Temporary directories and limits are not a filesystem/network sandbox; this harness is intended for these small inspected benchmark programs.

## Outcomes and denominators

| Classification | Meaning |
|---|---|
| `successful_repair` | Nonempty extracted patch compiles and passes every saved visible/hidden test |
| `compilation_failure` | Extracted patch fails compilation or compiler times out |
| `functional_test_failure` | Patch compiles but at least one test fails, crashes, or times out |
| `invalid_response` | Generation returned text/empty content but no nonempty required code block |
| `api_quota_failure` | API HTTP 429 or equivalent structured quota exhaustion |
| `api_service_error` | API service/connection/timeout error; not a code repair outcome |
| `api_access_error` | API authentication, authorization, model/path, or request rejection |
| `configuration_unavailable` | Missing credentials/model/dependency, disabled live access, or request cap; no request made |
| `skipped_after_api_error` | Circuit breaker skipped the provider after an earlier error; no additional request |
| `evaluation_infrastructure_error` | Local tool/process could not execute; excluded from repair-rate denominator |
| `provider_internal_error` | Unexpected adapter failure; separate from model repair outcomes |

A delivered response counts as `response_received` even if the text is empty, malformed, or truncated. A repair attempt means a nonempty extracted code patch with usable local evaluation. Unchanged patches still count as attempts; source-change status is recorded separately. The saved patch is compiled with the original class filename.

- Compile success = compiled patches / repair attempts.
- Functional success = patches passing all tests / repair attempts.
- Functional success per response = patches passing all tests / delivered responses. This additional denominator penalizes invalid responses instead of hiding them outside patch-level rates.
- Functional success given compilation = successful patches / compiled patches.
- Service availability = delivered responses / submitted requests. Missing credentials and circuit-breaker skips are not submitted requests. For the baseline this describes local generation availability.
- Mean successful response time = arithmetic mean over all delivered responses, including invalid ones; ?successful? here describes response delivery, not repair correctness. It includes request/client overhead and excludes compilation/testing.
- Mean request time additionally includes failed submitted requests. Per-case full-precision durations, counts, and denominators are saved. A zero denominator is N/A, never 0% and never a repaired case.

Tables are stratified by provider, exact requested model, and syntax/logic/runtime category. Requested aliases and server-resolved identifiers are recorded separately; alias stability cannot be assumed. Model response envelopes preserve available usage, finish reasons, and model metadata. Gemini and local inference request temperature zero; local inference sets seed 365 and disables prompt reuse. OpenAI retains provider-default sampling because supported controls depend on the chosen model; this difference is recorded. Identical sampling/numerical determinism across different providers is not claimed.

## Reproduction and preservation

Each run uses a UTC timestamp plus random ID. Files use exclusive creation, so writing an existing artifact raises an error. No results are rewritten to fit later code. A pre-run snapshot preserves relevant scripts/tests/data/requirements; the summary stores its exact generator separately so tables from earlier schema versions remain reproducible. `artifact_sha256.json` detects accidental changes; it is not a cryptographic attestation of who performed the experiment. Run completion records distinguish finished records from planned cases.

All comparison tables come from current per-case JSON records with matching per-case CSV and run CSV. `summarize_results.py --check` verifies source evidence, test statuses against process outputs, CSV equality, hashes, and the saved table schema. A regenerated table is written to a new directory. Historical CSV claims are inventoried separately and never pooled with new experiments. One generation per case does not estimate sampling variability; no statistical significance or universal correctness claims are supported.

## Explanation quality

Explanations remain an output of the system. Format checks alone do not establish explanation quality. `explanation_review.py` exports actual root-cause/explanation text and a four-dimension 0?2 rubric worksheet. A reviewer records scores, an exact response quote, rationale, identity, and whether the review is human or AI assisted. The validator computes score means with an explicit rated-response denominator; unrated and unavailable responses remain missing. See `EXPLANATION_RUBRIC.md`. AI-assisted preliminary ratings, if provided, are not human educational-effectiveness evidence. The student must independently review any ratings used in the paper.
