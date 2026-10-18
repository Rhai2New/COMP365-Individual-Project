# Recorded evaluation results

Generated from per-case records. Unavailable providers have no repair denominator.

| Provider | Exact requested model | Category | Scheduled | Responses / requests | Compile / attempts | Functional / attempts | Functional / responses | Mean response seconds (n) |
|---|---|---|---:|---|---|---|---|---|
| demo | local-rule-baseline-v1 | all | 20 | 20/20 (100.0%) | 17/20 (85.0%) | 1/20 (5.0%) | 1/20 (5.0%) | 0.000057 (20) |
| demo | local-rule-baseline-v1 | syntax | 4 | 4/4 (100.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) | 0.000135 (4) |
| demo | local-rule-baseline-v1 | logic | 14 | 14/14 (100.0%) | 14/14 (100.0%) | 0/14 (0.0%) | 0/14 (0.0%) | 0.000038 (14) |
| demo | local-rule-baseline-v1 | runtime | 2 | 2/2 (100.0%) | 2/2 (100.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 0.000033 (2) |
| gemini | gemini-3.8-flash | all | 20 | 0/1 (0.0%) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| gemini | gemini-3.8-flash | syntax | 4 | 0/1 (0.0%) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| gemini | gemini-3.8-flash | logic | 14 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| gemini | gemini-3.8-flash | runtime | 2 | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0 denominator) | N/A (0) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | all | 20 | 20/20 (100.0%) | 13/13 (100.0%) | 9/13 (69.2%) | 9/20 (45.0%) | 15.431525 (20) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | syntax | 4 | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 2.886323 (4) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | logic | 14 | 14/14 (100.0%) | 7/7 (100.0%) | 3/7 (42.9%) | 3/14 (21.4%) | 20.592974 (14) |
| llama_cpp | Qwen2.5-Coder-0.5B-Instruct-Q4_K_M | runtime | 2 | 2/2 (100.0%) | 2/2 (100.0%) | 2/2 (100.0%) | 2/2 (100.0%) | 4.391791 (2) |

Compile and functional denominators are extracted nonempty patches with usable local evaluation.
Service availability includes all submitted requests, including API errors. Local demo availability describes local generation.
Mean response time includes delivered responses, even invalid ones; request time additionally includes API failures.
Passes mean passing the saved visible and hidden tests, not proven program correctness.
