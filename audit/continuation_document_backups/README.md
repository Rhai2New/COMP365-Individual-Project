# Interactive Code Bug Explainer & Patch Generator ? final technical artifact

COMP 365 Individual Project. Final submission due October 18, 2026. This extends the existing Checkpoint 2 implementation. The research paper is written separately by the student; this repository contains code, evidence, and technical instructions.

## Quick local verification (Windows PowerShell)

The system `python` on the inspected machine is Python 3.8.2. Use Python 3.12 explicitly:

```powershell
cd C:\NCAT\COMP365_Checkpoint2_Project
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe validate_benchmarks.py
.\.venv\Scripts\python.exe benchmark_runner.py --providers demo
```

Requires Python 3.10+ (tested with 3.12) and a JDK with `java` and `javac`. Set `JAVA_HOME` to the installed JDK, or add its `bin` to PATH. The helper also discovers local Windows JDK installations. Baseline evaluation and the local HTTP adapters use only Python's standard library; the pinned SDKs are needed for cloud adapters and their contract tests. `requirements-lock.txt` records the installed dependency versions. Each benchmark/control run preserves versions, source snapshots, and hashes.

## Comparison systems

| Provider | System | Access |
|---|---|---|
| `demo` | Existing narrow rule-based baseline, `local-rule-baseline-v1` | Local, no key |
| `gemini` | Existing Gemini `generate_content` adapter recovered from GitHub commit `778a729`; requested default `gemini-3.8-flash` | `GEMINI_API_KEY` or `GOOGLE_API_KEY`; quota/model access must be checked |
| `llama_cpp` | Qwen2.5-Coder-0.5B-Instruct, official GGUF Q4_K_M, local llama.cpp CPU inference | Download once; no paid API |
| `openai` | Existing OpenAI Responses adapter, preserved | `OPENAI_API_KEY` and an explicit accessible model ID; optional |
| `ollama` | Optional installed local LLM through Ollama | Supply an installed exact tag; no automatic installation |

The primary comparison is baseline / Gemini / local Qwen. A configured provider is not an evaluated model: missing access produces unavailable records with no repair attempt. See [the results index](results/README.md) and [the final technical status](docs/FINAL_TECHNICAL_STATUS.md) for actual outcomes.

## Run the local LLM comparison

```powershell
.\.venv\Scripts\python.exe setup_local_model.py
.\.venv\Scripts\python.exe run_local_comparison.py
```

Setup downloads approximately 20 MB of official Windows x64 CPU binaries and a 491 MB official Qwen GGUF into ignored `.tools/`. The pinned build/model URLs, revisions, and SHA-256 digests are recorded in `local_model_provenance.json`. Setup verifies upstream digests when supplied; the run checks installed model/server hashes. No cloud key is used. The helper starts a hidden loopback-only server on port 18080, runs `demo,gemini,llama_cpp`, and stops its own server. Cloud calls are disabled by default, so Gemini is recorded as unavailable. For a short local smoke test, append `--limit 3`.

This small quantized model is a resource-constrained comparison system, not a substitute for a large cloud model. Its runtime, quantization, seed, prompt, responses, and test results must accompany any comparison. Model documentation: [official Qwen model card](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF); server behavior: [llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Gemini API setup and bounded execution

Install requirements, then set the key only in your terminal. Replace the placeholder locally; do not commit credentials. The application does not load `.env` files.

```powershell
$env:GEMINI_API_KEY = "YOUR_LOCAL_KEY"
.\.venv\Scripts\python.exe benchmark_runner.py --providers gemini --gemini-model gemini-3.8-flash --case J01 --allow-live --max-requests 1
```

Only run cloud commands after confirming the selected model's availability and your account's quota/billing. `--allow-live` explicitly enables cloud requests. The default cloud request limit is one; SDK and runner retries are disabled. A quota, access, service, or provider error opens a circuit breaker and skips later requests for that provider. A complete Gemini batch, once access and quota are confirmed, is:

```powershell
.\.venv\Scripts\python.exe benchmark_runner.py --providers demo,gemini --allow-live --max-requests 20
```

To include local Qwen in the same run, use `run_local_comparison.py --allow-live --max-requests 20` after confirming billing/quota. The request cap bounds request count, not dollar spending. No paid API call was authorized or made during this technical work. [Google's official API documentation](https://ai.google.dev/api/generate-content) describes the retained `generate_content` interface.

Optional OpenAI: set `OPENAI_API_KEY`, then pass `--providers openai --openai-model EXACT_ACCESSIBLE_MODEL --allow-live --max-requests 1 --case J01`. There is no guessed default model. The adapter uses the [Responses API](https://developers.openai.com/api/reference/python/resources/responses/methods/create), `store=False`, a 2,048-token output cap, a timeout, and `max_retries=0`. Optional Ollama: `--providers ollama --ollama-model EXACT_INSTALLED_TAG`; only local HTTP endpoints are accepted.

## Saved evidence and generated tables

Every experiment creates a new `results/runs/<UTC timestamp>_benchmark_<random ID>/`. No prior run filename is reused. `--output` is retained only as a legacy label and never writes over that path.

Each case/provider directory saves original source, visible failure context, full prompt, request settings, exact untrimmed model text, the SDK response envelope (or local raw HTTP JSON), extracted patch and diff, compilation stdout/stderr/exit status, every visible and hidden test result, timing, errors, and matching JSON/CSV records. Missing response/patch files mean no response/patch existed; `error.json` and `validation.json` explain why. Run configuration, package/compiler versions, test and code snapshots, completion status, summary generator, and artifact hashes are also saved. The SDK envelope is a parsed SDK serialization, not a network packet capture.

```powershell
.\.venv\Scripts\python.exe summarize_results.py "results\runs\RUN_DIRECTORY" --check
.\.venv\Scripts\python.exe summarize_results.py "results\runs\RUN_DIRECTORY"
```

`--check` verifies saved hashes, both CSV layers, individual process results, and exact summary reproduction using that run's saved generator. Without `--check`, it writes a separate timestamped regenerated summary; the original remains intact. Denominators and failure categories are defined in [methodology](docs/EVALUATION_METHODOLOGY.md).

## Interactive explainer

```powershell
.\.venv\Scripts\python.exe bug_explainer.py --source samples/BuggyGreeting.java --provider demo
```

The existing Java and C++ demo behavior is preserved. Interactive output now lives in a unique `results/interactive/` directory; source-adjacent patched examples and old reports are preserved. Interactive compilation is a smoke check only; functional success comes from the benchmark runner. For logic/runtime bugs provide visible failure text with `--error-file`. Cloud interactive requests also require an explicit model where applicable and `--allow-live`.

## Other materials

- [Evaluation methodology](docs/EVALUATION_METHODOLOGY.md)
- [Explanation-quality rubric](docs/EXPLANATION_RUBRIC.md)
- [Historical evidence and repository audit](docs/REPOSITORY_AND_EVIDENCE_AUDIT.md)
- [AI technical assistance disclosure](docs/AI_ASSISTANCE_DISCLOSURE.md)
- [Student submission checklist](docs/STUDENT_SUBMISSION_CHECKLIST.md)

Existing checkpoint documentation, scripts, and results were backed up under `audit/` before changes. `README_CHECKPOINT2.md`, `README_FIRST.txt`, and `TEST_RESULTS.txt` are historical, not current installation/results authority. Original benchmark Java files and manifests remain unchanged. QuixBugs/Defects4J are planned external datasets, not evaluated datasets in this artifact. The existing fetch script is optional and is not required to reproduce these experiments. Nothing has been pushed to GitHub.
