"""Append-only evidence helpers; a run's files are created exclusively."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import platform
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_run(root: Path, label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    path = root / f"{stamp}_{label}_{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def save_json(path: Path, value) -> None:
    save_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def save_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment() -> dict:
    from runtime_support import configure_java, execute
    configure_java()
    packages = {}
    for name in ("openai", "google-genai"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {"python": sys.version, "python_executable": sys.executable,
            "platform": platform.platform(), "packages": packages,
            "java": execute(["java", "-version"], ROOT),
            "javac": execute(["javac", "-version"], ROOT),
            "java_path": shutil.which("java"), "javac_path": shutil.which("javac")}


def snapshot(run: Path) -> dict:
    files = sorted(ROOT.glob("*.py")) + [ROOT / "requirements.txt"]
    files += [p for p in [ROOT / "requirements-lock.txt", ROOT / "local_model_provenance.json"] if p.exists()]
    files += sorted((ROOT / "benchmarks").glob("*.java"))
    files += sorted((ROOT / "benchmarks").glob("*.json"))
    files += sorted((ROOT / "tests").glob("*.py"))
    hashes = {}
    for source in files:
        rel = source.relative_to(ROOT)
        target = run / "snapshot" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(source.read_bytes())
        hashes[rel.as_posix()] = sha256(target)
    save_json(run / "snapshot_sha256.json", hashes)
    return hashes


def seal(run: Path) -> None:
    save_json(run / "artifact_sha256.json", {
        p.relative_to(run).as_posix(): sha256(p) for p in sorted(run.rglob("*"))
        if p.is_file() and p.name != "artifact_sha256.json"})
