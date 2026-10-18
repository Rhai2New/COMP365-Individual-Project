"""Package the technical artifact without dependencies, model weights, or credentials.

No Git mutation/push. Original results and audit backups remain in the ZIP.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from evidence import ROOT, save_json, save_text, sha256

EXCLUDED_PARTS = {".git", ".venv", ".tools", "__pycache__", ".idea", "submission", "external"}


def deliverable_files() -> list[Path]:
    return [p for p in sorted(ROOT.rglob("*")) if p.is_file()
            and not any(part in EXCLUDED_PARTS for part in p.relative_to(ROOT).parts)
            and not (p.name == ".env" or p.name.startswith(".env.") and p.name != ".env.example")
            and p.suffix.lower() not in {".pyc", ".class", ".exe", ".dll", ".gguf", ".zip"}]


def main() -> int:
    folder = ROOT / "submission"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    package = folder / f"COMP365_Final_Technical_{stamp}.zip"
    files = deliverable_files()
    # Fail with paths only if recognizable real credentials occur in any packaged text.
    pattern = re.compile(r"AIza[\w-]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    for path in files:
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            continue
        if pattern.search(content):
            raise ValueError(f"Potential secret in packaged file: {path.relative_to(ROOT)}")
    manifest_path = sorted((ROOT / "audit").glob("*/original_sha256.csv"))[0]
    with manifest_path.open(newline="", encoding="utf-8-sig") as handle:
        old = {r["path"].replace("\\", "/"): r["sha256"].lower() for r in csv.DictReader(handle)}
    changes = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        digest = sha256(path)
        if relative not in old or old[relative] != digest:
            changes.append({"path": relative, "change": "modified" if relative in old else "added",
                            "sha256_before": old.get(relative), "sha256_after": digest})
    inventory = {p.relative_to(ROOT).as_posix(): sha256(p) for p in files}
    with zipfile.ZipFile(package, mode="x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("SUBMISSION_MANIFEST.json", json.dumps({"sha256": inventory,
            "excluded": sorted(EXCLUDED_PARTS), "note": "Run setup_local_model.py to download pinned model/runtime; no paper is included."}, indent=2))
        archive.writestr("FILE_CHANGES.json", json.dumps(changes, indent=2))
    # Test the packaged project after extraction using this interpreter's installed SDKs.
    with tempfile.TemporaryDirectory(prefix="comp365_package_check_") as td:
        extracted = Path(td).resolve()
        with zipfile.ZipFile(package) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP CRC check failed")
            for member in archive.infolist():
                if not (extracted / member.filename).resolve().is_relative_to(extracted):
                    raise ValueError("Invalid package path")
            archive.extractall(extracted)
        hash_ok = all(sha256(extracted / name) == digest for name, digest in inventory.items())
        proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=extracted, text=True, encoding="utf-8", errors="replace", capture_output=True)
        save_text(folder / f"{stamp}_package_tests.txt", proc.stdout + proc.stderr)
        summary_checks = []
        for run in sorted((extracted / "results" / "runs").iterdir()):
            check = subprocess.run([sys.executable, "summarize_results.py", str(run), "--check"],
                cwd=extracted, text=True, encoding="utf-8", errors="replace", capture_output=True)
            summary_checks.append({"run_id": run.name, "passed": check.returncode == 0,
                                   "output": check.stdout + check.stderr})
        report = {"package": str(package), "sha256": sha256(package), "files": len(files),
                  "size_bytes": package.stat().st_size, "all_packaged_hashes_match": hash_ok,
                  "extracted_project_tests_exit_code": proc.returncode, "summary_checks": summary_checks,
                  "passed": hash_ok and proc.returncode == 0 and all(r["passed"] for r in summary_checks),
                  "modified_original_files": [r["path"] for r in changes if r["change"] == "modified"],
                  "added_file_count": sum(r["change"] == "added" for r in changes)}
    save_json(folder / f"{stamp}_package_verification.json", report)
    save_json(folder / f"{stamp}_file_changes.json", changes)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
