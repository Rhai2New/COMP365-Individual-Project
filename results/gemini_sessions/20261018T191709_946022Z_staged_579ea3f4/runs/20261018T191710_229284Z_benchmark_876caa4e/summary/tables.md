# Recorded evaluation results

Generated from per-case records. Unavailable providers have no repair denominator.

| Provider | Exact requested model | Category | Scheduled | Responses / requests | Compile / attempts | Functional / attempts | Functional / responses | Mean response seconds (n) |
|---|---|---|---:|---|---|---|---|---|
| gemini | gemini-3.8-flash | all | 1 | 1/1 (100.0%) | 1/1 (100.0%) | 1/1 (100.0%) | 1/1 (100.0%) | 6.179709 (1) |
| gemini | gemini-3.8-flash | syntax | 1 | 1/1 (100.0%) | 1/1 (100.0%) | 1/1 (100.0%) | 1/1 (100.0%) | 6.179709 (1) |
| gemini | gemini-3.8-flash | logic | 0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| gemini | gemini-3.8-flash | runtime | 0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |

Compile and functional denominators are extracted nonempty patches with usable local evaluation.
Service availability includes all submitted requests, including API errors. Local demo availability describes local generation.
Mean response time includes delivered responses, even invalid ones; request time additionally includes API failures.
Passes mean passing the saved visible and hidden tests, not proven program correctness.
