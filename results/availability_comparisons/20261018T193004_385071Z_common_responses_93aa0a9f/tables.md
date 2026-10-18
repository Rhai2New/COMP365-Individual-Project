# Recorded evaluation results

Generated from per-case records. Unavailable providers have no repair denominator.

| Provider | Exact requested model | Category | Scheduled | Responses / requests | Compile / attempts | Functional / attempts | Functional / responses | Mean response seconds (n) |
|---|---|---|---:|---|---|---|---|---|
| demo | local-rule-baseline-v1 | all | 10 | 10/10 (100.0%) | 7/10 (70.0%) | 1/10 (10.0%) | 1/10 (10.0%) | 0.000076 (10) |
| demo | local-rule-baseline-v1 | syntax | 4 | 4/4 (100.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 0.000135 (4) |
| demo | local-rule-baseline-v1 | logic | 6 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) | 0/6 (0.0%) | 0.000036 (6) |
| demo | local-rule-baseline-v1 | runtime | 0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| gemini | gemini-3.8-flash | all | 10 | 10/10 (100.0%) | 10/10 (100.0%) | 10/10 (100.0%) | 10/10 (100.0%) | 5.210724 (10) |
| gemini | gemini-3.8-flash | syntax | 4 | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 5.223721 (4) |
| gemini | gemini-3.8-flash | logic | 6 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) | 5.202059 (6) |
| gemini | gemini-3.8-flash | runtime | 0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | all | 10 | 10/10 (100.0%) | 6/6 (100.0%) | 5/6 (83.3%) | 5/10 (50.0%) | 16.753643 (10) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | syntax | 4 | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 2.886323 (4) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | logic | 6 | 6/6 (100.0%) | 2/2 (100.0%) | 1/2 (50.0%) | 1/6 (16.7%) | 25.998523 (6) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | runtime | 0 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |

Compile and functional denominators are extracted nonempty patches with usable local evaluation.
Service availability includes all submitted requests, including API errors. Local demo availability describes local generation.
Mean response time includes delivered responses, even invalid ones; request time additionally includes API failures.
Passes mean passing the saved visible and hidden tests, not proven program correctness.
