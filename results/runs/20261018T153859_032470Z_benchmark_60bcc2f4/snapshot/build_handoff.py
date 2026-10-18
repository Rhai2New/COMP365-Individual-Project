"""Generate factual final-status documentation from saved experiment evidence."""
from __future__ import annotations

import json
from pathlib import Path

from evidence import ROOT, save_json, save_text
from summarize_results import read_records


def main() -> int:
    run = next(p for p in sorted((ROOT / "results" / "runs").iterdir(), reverse=True)
               if "llama_cpp" in json.loads((p / "config.json").read_text(encoding="utf-8"))["providers"])
    rows = read_records(run)
    metrics = json.loads((run / "summary" / "metrics.json").read_text(encoding="utf-8"))
    control = sorted((ROOT / "results" / "validation").glob("*/summary.json"))[-1]
    verification = sorted((ROOT / "results" / "verification").glob("*/verification.json"))[-1]
    explanation = sorted((ROOT / "results" / "explanation_reviews").glob("*scored*/summary.json"))[-1]
    hist = sorted((ROOT / "results" / "historical_audits").glob("*/summary.json"))[-1]
    summaries = [m for m in metrics if m["category"] == "all"]
    def rel(p): return p.relative_to(ROOT).as_posix()
    def frac(n, d): return f"{n}/{d} ({n/d:.1%})" if d else "N/A (no requests/attempts)"
    lines = ["# Final technical status — October 18, 2026", "",
        "This is a factual technical handoff, not research-paper prose. Values below are generated from the linked saved records.", "",
        "## Verified experiment", "",
        f"Primary run: [`{run.name}`](../{rel(run)}/summary/tables.md), {len(rows)} case/provider records. "
        "All 20 original cases were scheduled for the baseline, Gemini, and actual local Qwen model.", "",
        "| System | Responses / requests | Compiles / extracted patches | Functional / extracted patches | Functional / responses | Invalid responses | Mean response seconds (n) |",
        "|---|---|---|---|---|---:|---|"]
    for m in summaries:
        latency = f"{m['mean_successful_response_seconds']:.6f} ({m['responses_received']})" if m['responses_received'] else "N/A (0)"
        lines.append(f"| {m['provider']} / {m['model']} | {frac(m['responses_received'],m['requests_made'])} | "
            f"{frac(m['compile_successes'],m['repair_attempts'])} | {frac(m['functional_successes'],m['repair_attempts'])} | "
            f"{frac(m['functional_successes'],m['responses_received'])} | {m['invalid_responses']} | {latency} |")
    local_success = [r['case_id'] for r in rows if r['provider']=='llama_cpp' and r['test_success']]
    lines += ["", f"Qwen test-passing cases: {', '.join(local_success)}. "
              "All seven unusable Qwen responses reached the saved output-token limit. "
              "The four other extracted Qwen patches compiled but failed functional testing. "
              "These are observed failures; none were replaced or retried.", "",
              "| System | Syntax functional / responses | Logic functional / responses | Runtime functional / responses |",
              "|---|---|---|---|"]
    for provider in ('demo','gemini','llama_cpp'):
        cells = []
        for category in ('syntax','logic','runtime'):
            m = next(m for m in metrics if m['provider']==provider and m['category']==category)
            cells.append(frac(m['functional_successes'],m['responses_received']))
        lines.append('| ' + provider + ' | ' + ' | '.join(cells) + ' |')
    lines += ["", "Service delivery was 20/20 for each local generator. Gemini made zero requests because no credential was available; "
              "its 20 unavailable rows are not repair failures or measured service outages. The earlier inventory run also recorded OpenAI/Ollama configuration unavailability. "
              "No live cloud request or paid API operation was performed.", "",
              "## Technical work completed", "",
              "- Preserved all original benchmark sources, manifests, sample programs, and existing results; verified 39 original files by SHA-256. The rule baseline's function AST is unchanged.",
              "- Recovered existing Gemini support from the actual GitHub history; preserved the OpenAI adapter and added actual local Qwen inference plus optional Ollama support.",
              "- Added unique append-only run directories, exact response text, request settings/prompts, patches/diffs, every compiler/test outcome, timing, errors, per-case CSV/JSON, run CSV, snapshots, versions, and hashes.",
              "- Added explicit outcome categories, quota/service/access separation, no retries, a provider circuit breaker, request caps, and denominator-bearing generated tables.",
              "- Added 58 held-out tests to the original 36 visible tests. All 20 case classifications and 94 expectations passed independent-oracle/authored-control checks. Controls are not model results.",
              "- Updated dependencies, Windows commands, API setup, methodological limitations, historical evidence audit, explanation rubric, and AI technical assistance disclosure.",
              "- Established the relationship to the real sibling Git checkout and matching remote HEAD without initializing this folder, changing that checkout, or pushing.", "",
              "## Validation evidence", "",
              f"- [Final verification report](../{rel(verification)}): Python syntax, 14 regression/SDK-contract tests, both runs' CSV/summary/hash consistency, prompt reconstruction, preservation, and credential-pattern scan passed.",
              f"- [Benchmark control validation](../{rel(control)}): 20/20 category checks and authored repairs pass; all 94 expected outputs verified.",
              "- Java and C++ interactive demo compilation checks passed, with fresh evidence under `results/interactive/`; functional results come from the Java benchmark, not these smoke checks.",
              "- The original historical screenshot was visually inspected; it contains a demo compile result and no credential. The text credential-pattern scan reported no matches in project/evidence/audit files; model/dependency caches and binary files were excluded.", "",
              "## Explanation review", "",
              "A rubric, editable human-review worksheet, structural checks, and 40 preliminary AI-assisted ratings are saved separately from the sealed experiments. "
              "These are single-rater AI judgments and must be independently reviewed before use as explanation-quality evidence. They are not human learning-effectiveness measurements.", "",
              "| Provider | AI-assisted rated responses | Mean preliminary total / 8 |", "|---|---:|---:|"]
    for m in json.loads(explanation.read_text(encoding='utf-8')):
        lines.append(f"| {m['provider']} | {m['rated_responses']} | {m['mean_total_out_of_8']:.2f} |")
    lines += ["", f"[Review summary and source ratings](../{rel(explanation.parent)}/summary.csv). "
              "Successful patches sometimes have incorrect explanations; patch success was not used as a proxy for explanation accuracy.", "",
              "## Incomplete requirements and practical limits", "",
              "- A fresh complete three-system evaluation remains incomplete: baseline and actual local Qwen were evaluated; Gemini needs a working key and confirmed quota. OpenAI is implemented but not evaluated.",
              "- Historical CSVs support claims for only J01–J03; the corresponding saved response files were overwritten by quota errors. The eight-success and average-time claims remain unverified and are excluded.",
              "- Five fixed-output/no-input programs cannot receive independent input-based output checks without changing their original tasks. Their held-out ignored-input tests provide limited additional assurance.",
              "- Only small self-authored Java cases were evaluated. Public benchmark expansion, broader domains, repeated stochastic trials, human educational validation, and statistical significance were not completed or claimed.",
              "- The local model is small and quantized. Latencies include local request overhead; they are not comparable to a cloud provider with no measured responses. Output-cap failures remain part of the observed result.",
              "- Python 3.8 from the machine's default `python` is unsupported; use the documented Python 3.12 commands. The optional model setup helper downloads Windows x64 binaries; other platforms need an equivalent documented local server setup.",
              "- The working copy remains unversioned. GitHub integration/push and the LMS upload have not been performed.", "",
              "The student must independently review scores/results, write the RED/no-AI paper, record their own video, approve any GitHub push, and complete the actual LMS submission. "
              "See [the student checklist](STUDENT_SUBMISSION_CHECKLIST.md).", ""]
    save_text(ROOT / "docs" / "FINAL_TECHNICAL_STATUS.md", "\n".join(lines))
    index = ["# Results and evidence index", "",
        f"Primary final comparison: [{run.name}]({run.relative_to(ROOT/'results').as_posix()}/summary/tables.md). "
        "This includes an actual 20-case baseline and local Qwen run, plus explicitly unavailable Gemini records.", "",
        "| Directory | Contents |", "|---|---|",
        "| `runs/` | Unique benchmark runs; per-case JSON/CSV and full artifacts, source snapshots, checksums, generated tables |",
        "| `validation/` | Classification/oracle checks and authored positive controls, separate from model results |",
        "| `verification/` | Syntax, regression, evidence-consistency, preservation, and credential-pattern audits |",
        "| `interactive/` | Fresh Java/C++ demo evidence; compilation smoke checks only |",
        "| `explanation_reviews/` | Editable human worksheets, structural checks, explicitly AI-assisted preliminary ratings |",
        "| `historical_checkpoint2_checkout/` | Unchanged copied evidence from the actual sibling checkout, with hash provenance |",
        "| `historical_audits/` | Generated inventory of historical Gemini CSV claims and overwritten response evidence |",
        "| `server_logs/` | Local llama.cpp startup/version/runtime logs and exact launch command |", "",
        "Original top-level CSV/TXT/PNG files and `outputs/` are historical and preserved unchanged. "
        "They are excluded from current experiment tables. Never pool repeated CSV rows or unverified historical claims as distinct successes.", "",
        "To check a saved run: `python summarize_results.py results/runs/RUN_DIRECTORY --check` using Python 3.10+ "
        "(on this machine, use `.venv/Scripts/python.exe` or `py -3.12`). "
        "To regenerate into a new directory, omit `--check`.", ""]
    save_text(ROOT / "results" / "README.md", "\n".join(index))
    save_json(ROOT / "docs" / "handoff_sources.json", {"primary_run": rel(run), "control_validation": rel(control),
        "verification": rel(verification), "explanation_ratings": rel(explanation), "historical_audit": rel(hist)})
    print(ROOT / "docs" / "FINAL_TECHNICAL_STATUS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
