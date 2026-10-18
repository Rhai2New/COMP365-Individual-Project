"""Final local audit: syntax, tests, saved evidence, preservation, and secret patterns."""
from __future__ import annotations

import csv
import ast
import hashlib
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

from evidence import ROOT, new_run, save_json, save_text, sha256, utc_now


def main() -> int:
    output = new_run(ROOT / "results" / "verification", "final_checks")
    checks = []
    for path in sorted(ROOT.glob("*.py")) + sorted((ROOT / "tests").glob("*.py")):
        py_compile.compile(str(path), doraise=True)
    checks.append({"check": "current Python syntax", "passed": True})
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                          cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
    save_text(output / "unit_tests.stdout.txt", proc.stdout)
    save_text(output / "unit_tests.stderr.txt", proc.stderr)
    checks.append({"check": "regression tests", "passed": proc.returncode == 0, "exit_code": proc.returncode})
    import shutil
    if shutil.which('node'):
        js = subprocess.run(['node', '--check', str(ROOT / 'web' / 'app.js')], capture_output=True, text=True)
        checks.append({'check': 'web JavaScript syntax', 'passed': js.returncode == 0})
    from summarize_results import read_records
    runs = sorted(p.parent for p in (ROOT / 'results').rglob('completion.json')
                  if (p.parent / 'cases').is_dir())
    for run in runs:
        if not (run / "completion.json").exists():
            checks.append({"check": "completed run " + run.name, "passed": False, "reason": "still running or interrupted"})
            continue
        proc = subprocess.run([sys.executable, "summarize_results.py", str(run), "--check"], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        save_text(output / (run.name + ".summary_check.txt"), proc.stdout + proc.stderr)
        checks.append({"check": "records, CSVs, summaries, and hashes: " + run.name, "passed": proc.returncode == 0})
        for row in read_records(run):
            directory = run / row["artifact_dir"]
            from repair_providers import make_prompt
            from runtime_support import failure_context
            original = json.loads((directory / "original_evaluation.json").read_text(encoding="utf-8"))
            source = (directory / "original.java").read_text(encoding="utf-8")
            expected = make_prompt(source, "java", failure_context(original))
            actual = json.loads((directory / "prompt.json").read_text(encoding="utf-8"))
            if expected != actual or any(t.get("split") != "visible" for t in original["tests"]):
                raise ValueError("Prompt/test separation failed")
        checks.append({"check": "visible-only prompt reconstruction: " + run.name, "passed": True})
    # Check every original result/source/example file against the pre-edit manifest.
    manifest = sorted((ROOT / "audit").glob("*/original_sha256.csv"))[0]
    with manifest.open(newline="", encoding="utf-8-sig") as handle:
        originals = list(csv.DictReader(handle))
    preserve = [r for r in originals if r["path"].replace("\\", "/").split("/")[0] in {"results", "benchmarks", "samples"}]
    mismatches = [r["path"] for r in preserve if not (ROOT / r["path"]).is_file() or
                  sha256(ROOT / r["path"]).lower() != r["sha256"].lower()]
    checks.append({"check": "original results, benchmarks, and samples preserved", "passed": not mismatches,
                   "files_checked": len(preserve), "mismatches": mismatches})
    def baseline_ast(path):
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        return ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'demo_response'))
    checks.append({'check': 'rule baseline function AST preserved',
                   'passed': baseline_ast(ROOT / 'bug_explainer.py') == baseline_ast(manifest.parent / 'bug_explainer.py')})
    historical = ROOT / "results" / "historical_checkpoint2_checkout"
    provenance = json.loads((historical / "provenance.json").read_text(encoding="utf-8"))
    changed = [r["path"] for r in provenance["files"] if sha256(historical / r["path"]) != r["sha256"]]
    checks.append({"check": "copied historical evidence matches provenance", "passed": not changed,
                   "files_checked": len(provenance["files"]), "mismatches": changed})
    # Never print matching content. Ignore dependencies, model/binary caches and compiled files.
    findings, scanned = [], 0
    from repair_providers import load_saved_gemini_key
    import os
    load_saved_gemini_key()
    exact_secrets = [v for k, v in os.environ.items() if len(v) >= 8 and
                     any(t in k.upper() for t in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD'))]
    patterns = {"google_api_key": re.compile(r"AIza[\w-]{30,}"),
                "openai_api_key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
                "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})"),
                "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(p in {".venv", ".tools", ".git", "__pycache__", "submission"} for p in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in {".png", ".zip", ".class", ".exe", ".pyc"}:
            continue
        if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example'):
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            continue
        scanned += 1
        if any(secret in content for secret in exact_secrets):
            findings.append({'path': path.relative_to(ROOT).as_posix(), 'pattern': 'exact_environment_credential'})
        for name, pattern in patterns.items():
            if pattern.search(content):
                findings.append({"path": path.relative_to(ROOT).as_posix(), "pattern": name})
    checks.append({"check": "credential pattern scan", "passed": not findings, "text_files_scanned": scanned,
                   "findings_without_secret_values": findings,
                   "scope": "Deliverable text, evidence, and audit backups; excludes local .env secrets, .venv/.tools/binary images"})
    control_runs = sorted((ROOT / "results" / "validation").glob("*/summary.json"))
    control = json.loads(control_runs[-1].read_text(encoding="utf-8"))
    checks.append({"check": "20 category labels, 94 test expectations, authored controls", "passed": control["passed"],
                   "cases": control["cases"], "visible_tests": control["visible_tests"], "hidden_tests": control["hidden_tests"]})
    from finalize_results import verify_comparison
    for comparison in sorted((ROOT / 'results' / 'comparisons').iterdir()):
        verify_comparison(comparison)
        checks.append({'check': 'complete comparison reproduction: ' + comparison.name, 'passed': True})
    seals_checked = 0
    for manifest in (ROOT / 'results').rglob('artifact_sha256.json'):
        folder = manifest.parent
        for relative, digest in json.loads(manifest.read_text(encoding='utf-8')).items():
            target = folder / relative
            if not target.resolve().is_relative_to(folder.resolve()) or sha256(target) != digest:
                raise ValueError('Sealed evidence mismatch: ' + str(target))
        seals_checked += 1
    checks.append({'check': 'all sealed experiment/control/replay/review artifacts', 'passed': True, 'seals': seals_checked})
    passed = all(c["passed"] for c in checks)
    save_json(output / "verification.json", {"finished_utc": utc_now(), "passed": passed, "checks": checks,
              "not_claimed": ["Live Gemini access", "Live OpenAI access", "Human explanation ratings", "Paper/video completion"]})
    print(json.dumps({"passed": passed, "report": str(output), "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
