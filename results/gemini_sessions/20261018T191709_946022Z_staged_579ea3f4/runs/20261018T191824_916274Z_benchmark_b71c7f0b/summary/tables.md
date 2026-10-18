# Recorded evaluation results

Generated from per-case records. Unavailable providers have no repair denominator.

| Provider | Exact requested model | Category | Scheduled | Responses / requests | Compile / attempts | Functional / attempts | Functional / responses | Mean response seconds (n) |
|---|---|---|---:|---|---|---|---|---|
| gemini | gemini-3.8-flash | all | 19 | 9/10 (90.0%) | 9/9 (100.0%) | 9/9 (100.0%) | 9/9 (100.0%) | 5.103059 (9) |
| gemini | gemini-3.8-flash | syntax | 3 | 3/3 (100.0%) | 3/3 (100.0%) | 3/3 (100.0%) | 3/3 (100.0%) | 4.905059 (3) |
| gemini | gemini-3.8-flash | logic | 14 | 6/7 (85.7%) | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) | 5.202059 (6) |
| gemini | gemini-3.8-flash | runtime | 2 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |

Compile and functional denominators are extracted nonempty patches with usable local evaluation.
Service availability includes all submitted requests, including API errors. Local demo availability describes local generation.
Mean response time includes delivered responses, even invalid ones; request time additionally includes API failures.
Passes mean passing the saved visible and hidden tests, not proven program correctness.
