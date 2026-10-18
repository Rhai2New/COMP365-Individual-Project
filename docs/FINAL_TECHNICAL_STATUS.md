# Current technical status

See [final report](../FINAL_READY_REPORT.md) and [data guide](../FINAL_PAPER_DATA_GUIDE.md).

The local .env key authenticated successfully. J01 passed compilation and all tests, then the staged helper automatically continued J02-J20 with at least 65-second request spacing and no retries. Gemini delivered 10/11 requests; 9 cases were skipped. Missing cases remain unevaluated. Requested model: gemini-3.8-flash; saved served identifier(s): gemini-3.8-flash. Quota failures: 0; service errors: 1; access errors: 0. The user personally confirmed Free Tier with billing disabled; billing was not enabled and no paid API calls were authorized. Earlier HTTP 400/blocked experiments remain historical and are excluded from this comparison.

| System | Responses / requests | Compiles / patches | Visible success / patches | Hidden success / patches | All tests / patches | All tests / responses | Invalid | Mean generation s (n) |
|---|---|---|---|---|---|---|---:|---|
| Rule baseline | 20/20 | 17/20 | 1/20 | 2/20 | 1/20 | 1/20 | 0 | 0.000056505 (20) |
| Local Qwen | 20/20 | 13/13 | 9/13 | 10/13 | 9/13 | 9/20 | 7 | 15.431525365 (20) |
| Gemini | 10/11 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0 | 5.210724030 (10) |

All 20 benchmark categories and 94 expectations were checked. Human explanation ratings remain absent; blank worksheets are ready. Regression/reproduction and clean-extraction package outcomes are recorded in the final report and submission sidecar. Nothing has been pushed or submitted.

J11 returned HTTP 503 UNAVAILABLE (high demand), after 31.546709000 s, with no model response. J12-J20 were skipped without requests. No retry was made. Gemini response coverage is 10/20 scheduled cases; observed delivery is 10/11 submitted requests (90.91%). The ten missing repair outcomes are unevaluated, not model failures. Runtime repair results are unavailable for Gemini.

Common J01-J10 all-test results: baseline 1/10, Qwen 5/10, Gemini 10/10; no runtime cases. All 43 extracted patches reproduced their original outcomes.
