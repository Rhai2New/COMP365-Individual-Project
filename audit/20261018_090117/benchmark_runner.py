#!/usr/bin/env python3
"""Checkpoint 2 benchmark runner.

Runs the local rule-based baseline and/or OpenAI model on exactly the same Java cases.
Records patch compilation, functional test success, and response time separately.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from bug_explainer import demo_response, extract_patched_code, openai_response

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "benchmarks"
RESULTS_DIR = ROOT / "results"


def normalize_output(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


def compile_java(source_text: str, filename: str) -> tuple[bool, str, Path | None, tempfile.TemporaryDirectory | None]:
    if shutil.which("javac") is None:
        return False, "javac not found on PATH", None, None
    td = tempfile.TemporaryDirectory(prefix="comp365_bench_")
    build_dir = Path(td.name)
    source_path = build_dir / filename
    source_path.write_text(source_text, encoding="utf-8")
    proc = subprocess.run(
        ["javac", filename],
        cwd=build_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20,
    )
    output = proc.stdout.strip() or "Compilation succeeded with no compiler messages."
    if proc.returncode != 0:
        td.cleanup()
        return False, output, None, None
    return True, output, build_dir, td


def run_java_tests(source_text: str, filename: str, tests: list[dict]) -> tuple[bool, str, bool]:
    compile_ok, compile_output, build_dir, td = compile_java(source_text, filename)
    if not compile_ok:
        return False, f"COMPILER ERROR:\n{compile_output}", False

    assert build_dir is not None and td is not None
    class_name = Path(filename).stem
    failures = []
    try:
        for index, test in enumerate(tests, start=1):
            proc = subprocess.run(
                ["java", "-cp", str(build_dir), class_name],
                cwd=build_dir,
                input=test.get("input", ""),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            actual = normalize_output(proc.stdout)
            expected = normalize_output(test["expected"])
            if proc.returncode != 0 or actual != expected:
                failures.append(
                    f"Test {index} FAILED\n"
                    f"Input: {test.get('input', '').rstrip() or '<none>'}\n"
                    f"Expected: {expected!r}\n"
                    f"Actual: {actual!r}\n"
                    f"Exit code: {proc.returncode}"
                )
        return True, ("All tests passed." if not failures else "\n\n".join(failures)), not failures
    finally:
        td.cleanup()


def failure_context_for_original(source: str, filename: str, tests: list[dict]) -> tuple[bool, bool, str]:
    compile_ok, compile_output, build_dir, td = compile_java(source, filename)
    if not compile_ok:
        return False, False, f"COMPILER ERROR:\n{compile_output}"
    assert build_dir is not None and td is not None
    class_name = Path(filename).stem
    failures = []
    try:
        for index, test in enumerate(tests, start=1):
            proc = subprocess.run(
                ["java", "-cp", str(build_dir), class_name],
                cwd=build_dir,
                input=test.get("input", ""),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            actual = normalize_output(proc.stdout)
            expected = normalize_output(test["expected"])
            if proc.returncode != 0 or actual != expected:
                failures.append(
                    f"Test {index} FAILED\n"
                    f"Input: {test.get('input', '').rstrip() or '<none>'}\n"
                    f"Expected: {expected!r}\n"
                    f"Actual: {actual!r}\n"
                    f"Exit code: {proc.returncode}"
                )
        tests_pass = not failures
        context = "All tests passed." if tests_pass else "TEST FAILURE:\n" + "\n\n".join(failures)
        return True, tests_pass, context
    finally:
        td.cleanup()


def run_provider(case: dict, provider: str, model: str, attempts: int = 2) -> dict:
    source_path = BENCHMARK_DIR / case["source"]
    source = source_path.read_text(encoding="utf-8")
    filename = source_path.name
    tests = case["tests"]

    orig_compile, orig_tests, failure_context = failure_context_for_original(source, filename, tests)

    response_text = ""
    error = ""
    latency = 0.0
    patched = None

    for attempt in range(1, attempts + 1):
        start = time.perf_counter()
        try:
            if provider == "demo":
                response_text = demo_response(source, "java", failure_context)
            else:
                response_text = openai_response(source, "java", failure_context, model)
            latency = time.perf_counter() - start
            patched = extract_patched_code(response_text)
            if patched is None:
                error = "No PATCHED CODE block extracted"
                if provider == "openai" and attempt < attempts:
                    time.sleep(0.5)
                    continue
            else:
                error = ""
            break
        except Exception as exc:
            latency = time.perf_counter() - start
            error = str(exc)
            if provider == "openai" and attempt < attempts:
                time.sleep(1.0)
                continue
            break

    patch_compile = False
    test_success = False
    validation = ""
    changed = False
    if patched is not None:
        changed = normalize_output(patched) != normalize_output(source)
        patch_compile, validation, test_success = run_java_tests(patched, filename, tests)

    output_dir = RESULTS_DIR / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{case['case_id']}_{provider}.txt"
    output_file.write_text(
        f"CASE: {case['case_id']}\nPROVIDER: {provider}\nBUG TYPE: {case['bug_type']}\n\n"
        f"FAILURE CONTEXT\n{'-'*60}\n{failure_context}\n\n"
        f"REPAIR RESPONSE\n{'-'*60}\n{response_text or '<no response>'}\n\n"
        f"VALIDATION\n{'-'*60}\n{validation or error or '<not run>'}\n",
        encoding="utf-8",
    )

    return {
        "case_id": case["case_id"],
        "language": case["language"],
        "bug_type": case["bug_type"],
        "difficulty": case["difficulty"],
        "provider": provider,
        "original_compile_success": orig_compile,
        "original_test_success": orig_tests,
        "patch_generated": patched is not None,
        "patch_changed_source": changed,
        "patch_compile_success": patch_compile,
        "test_success": test_success,
        "response_seconds": round(latency, 3),
        "failure_context": failure_context.replace("\n", " | ")[:600],
        "validation_summary": validation.replace("\n", " | ")[:600],
        "error": error,
        "source": case["source"],
    }


def write_results(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> str:
    lines = []
    providers = sorted({r["provider"] for r in rows})
    for provider in providers:
        subset = [r for r in rows if r["provider"] == provider]
        n = len(subset)
        compile_pass = sum(bool(r["patch_compile_success"]) for r in subset)
        test_pass = sum(bool(r["test_success"]) for r in subset)
        avg_latency = sum(float(r["response_seconds"]) for r in subset) / n if n else 0.0
        syntax = [r for r in subset if r["bug_type"].startswith("syntax")]
        logic = [r for r in subset if r["bug_type"].startswith("logic")]
        runtime = [r for r in subset if r["bug_type"].startswith("runtime")]
        lines.extend([
            f"Provider: {provider}",
            f"Cases: {n}",
            f"Patch compile success: {compile_pass}/{n} ({compile_pass/n:.1%})" if n else "Patch compile success: n/a",
            f"Functional test success: {test_pass}/{n} ({test_pass/n:.1%})" if n else "Functional test success: n/a",
            f"Average response time: {avg_latency:.3f} s",
            f"Syntax test success: {sum(bool(r['test_success']) for r in syntax)}/{len(syntax)}" if syntax else "Syntax test success: n/a",
            f"Logic test success: {sum(bool(r['test_success']) for r in logic)}/{len(logic)}" if logic else "Logic test success: n/a",
            f"Runtime test success: {sum(bool(r['test_success']) for r in runtime)}/{len(runtime)}" if runtime else "Runtime test success: n/a",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="demo,openai", help="Comma-separated: demo,openai")
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--limit", type=int, default=0, help="Optional number of cases for a smoke test")
    parser.add_argument("--case", action="append", help="Run only selected case id; can repeat")
    parser.add_argument("--output", default="results/checkpoint2_results.csv")
    args = parser.parse_args()

    if shutil.which("javac") is None or shutil.which("java") is None:
        raise SystemExit("ERROR: java/javac are not available on PATH.")

    if "openai" in args.providers.split(",") and not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("ERROR: OPENAI_API_KEY is not set. Run demo-only or set the key first.")

    cases = json.loads((BENCHMARK_DIR / "manifest.json").read_text(encoding="utf-8"))
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["case_id"] in wanted]
    if args.limit:
        cases = cases[: args.limit]

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    rows = []
    total = len(cases) * len(providers)
    completed = 0
    for case in cases:
        for provider in providers:
            completed += 1
            print(f"[{completed}/{total}] {case['case_id']} - {case['bug_type']} - {provider}")
            row = run_provider(case, provider, args.model)
            rows.append(row)
            print(
                f"    compile={'PASS' if row['patch_compile_success'] else 'FAIL'} "
                f"tests={'PASS' if row['test_success'] else 'FAIL'} "
                f"time={row['response_seconds']:.3f}s"
            )

    output = ROOT / args.output
    write_results(rows, output)
    summary = summarize(rows)
    summary_path = output.with_name("checkpoint2_summary.txt" if output.name == "checkpoint2_results.csv" else output.stem + "_summary.txt")
    summary_path.write_text(summary, encoding="utf-8")
    print("\n" + summary)
    print(f"Saved results: {output}")
    print(f"Saved summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
