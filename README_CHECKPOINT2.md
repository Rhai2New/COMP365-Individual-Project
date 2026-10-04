# COMP 365 - Individual Project - Checkpoint 2

## Interactive Code Bug Explainer & Patch Generator

Checkpoint 2 scales the Checkpoint 1 prototype from two smoke tests to a 20-case Java micro-benchmark. The same cases are evaluated with:

1. `demo` - the intentionally small local rule-based baseline from Checkpoint 1.
2. `openai` - the LLM repair method.

The benchmark records three required outcomes separately:

- patch compilation success,
- functional test success,
- response time.

This distinction matters because a logic-bug patch can compile and still produce the wrong output.

## Benchmark contents

`benchmarks/` contains all 20 cases used in the Checkpoint 2 results plus `manifest.json` and `manifest.csv`.

The suite includes:

- 4 syntax cases,
- 14 logic cases,
- 2 runtime cases.

All cases are small Java programs intended to represent introductory-programming bugs. They are self-authored micro-benchmarks for this checkpoint. QuixBugs and Defects4J remain the planned public benchmark sources for the larger final evaluation.

## Run the baseline only

From PowerShell in this project folder:

```powershell
.\run_baseline_only.bat
```

Expected baseline result on the 20 included cases:

- compile success: 17/20 (85%)
- functional test success: 1/20 (5%)

The high compile rate but low test rate is intentional evidence that compilation alone is not enough.

## Run the full Checkpoint 2 comparison

Make sure your virtual environment has the dependency:

```powershell
python -m pip install -r requirements.txt
```

Set a NEW API key in the current PowerShell session. Do not put the key in source code or commit it:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY_HERE"
```

Run:

```powershell
.\run_checkpoint2_benchmark.bat
```

This produces:

- `results/checkpoint2_results.csv`
- `results/checkpoint2_summary.txt`

The full run makes 20 small LLM requests, one per benchmark case. The local baseline is also run on those exact 20 cases.

## Quick smoke test before all 20

```powershell
python benchmark_runner.py --providers demo,openai --limit 3 --output results/smoke_results.csv
```

If those three cases finish correctly, run the full batch file.

## Files to submit

For the technical artifact, submit this repository link or a ZIP containing the project. Do not include `.venv/` or an API key.
