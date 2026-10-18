"""Reproduce tables from per-case JSON, checking CSV and artifact integrity."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from evidence import new_run, save_csv, save_json, save_text, sha256


def csv_value(value) -> str:
    return "" if value is None else str(value)


def read_records(run: Path, verify: bool = True) -> list[dict]:
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((run / "cases").glob("*/*/record.json"))]
    identities = [(r["case_id"], r["provider"]) for r in rows]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate case/provider records")
    for row in rows:
        if row["run_id"] != run.name:
            raise ValueError("Record run ID does not match its directory")
        directory = run / row["artifact_dir"]
        if not directory.resolve().is_relative_to(run.resolve()):
            raise ValueError("Artifact path outside run")
        if row["response_received"] and not (directory / "response.txt").is_file():
            raise ValueError("Missing response evidence")
        if row["repair_attempted"]:
            if not (directory / "patch" / row["source"]).is_file():
                raise ValueError("Missing patch evidence")
            validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
            if row["status"] != "evaluation_infrastructure_error":
                from runtime_support import normalize_output
                comp = validation["compilation"]
                if comp["success"] != (comp["returncode"] == 0):
                    raise ValueError("Compilation status disagrees with exit code")
                expected_tests = json.loads((directory / "evaluation_tests.json").read_text(encoding="utf-8"))
                if comp["success"] and len(validation["tests"]) != len(expected_tests):
                    raise ValueError("Missing functional tests")
                for test, expected in zip(validation["tests"], expected_tests):
                    if (test["input"], test["expected"], test["split"]) != (expected["input"], expected["expected"], expected["split"]):
                        raise ValueError("Executed tests differ from saved test specification")
                    actual_success = test["returncode"] == 0 and normalize_output(test["stdout"]) == normalize_output(test["expected"])
                    if test["success"] != actual_success:
                        raise ValueError("Test result disagrees with process output")
                correct = bool(comp["success"] and validation["tests"] and all(t["success"] for t in validation["tests"]))
                if validation["functional_success"] != correct:
                    raise ValueError("Functional aggregate disagrees with individual tests")
                if row["patch_compile_success"] != validation["compilation"]["success"]:
                    raise ValueError("Compilation disagrees with validation")
                if row["test_success"] != validation["functional_success"]:
                    raise ValueError("Functional result disagrees with validation")
        if row["test_success"] and not (row["patch_compile_success"] and row["visible_test_success"] and row["hidden_test_success"]):
            raise ValueError("Inconsistent successful repair")
        with (directory / "record.csv").open(newline="", encoding="utf-8") as handle:
            saved = list(csv.DictReader(handle))
        if saved != [{k: csv_value(v) for k, v in row.items()}]:
            raise ValueError("Per-case CSV differs from JSON")
    if (run / "results.csv").exists():
        with (run / "results.csv").open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
        expected = [{k: csv_value(v) for k, v in row.items()} for row in rows]
        key = lambda r: (r.get("case_id", ""), r.get("provider", ""))
        if sorted(csv_rows, key=key) != sorted(expected, key=key):
            raise ValueError("Run CSV differs from per-case JSON")
    if verify and (run / "artifact_sha256.json").exists():
        hashes = json.loads((run / "artifact_sha256.json").read_text(encoding="utf-8"))
        for relative, digest in hashes.items():
            target = run / relative
            if not target.resolve().is_relative_to(run.resolve()) or not target.is_file() or sha256(target) != digest:
                raise ValueError(f"Artifact integrity check failed: {relative}")
    return rows


def metrics(rows: list[dict]) -> list[dict]:
    summaries = []
    groups = sorted({(r["provider"], r["model"] or "<not configured>") for r in rows})
    for provider, model in groups:
        group = [r for r in rows if r["provider"] == provider and (r["model"] or "<not configured>") == model]
        for category in ["all", "syntax", "logic", "runtime"]:
            subset = [r for r in group if category == "all" or r["category"] == category]
            requested = [r for r in subset if r["request_made"]]
            delivered = [r for r in requested if r["response_received"]]
            attempted = [r for r in subset if r["repair_attempted"] and r["status"] != "evaluation_infrastructure_error"]
            compiled = [r for r in attempted if r["patch_compile_success"]]
            correct = [r for r in attempted if r["test_success"]]
            def ratio(n, d):
                return n / d if d else None
            summaries.append({"provider": provider, "model": model, "category": category,
                "scheduled_cases": len(subset), "requests_made": len(requested),
                "responses_received": len(delivered), "repair_attempts": len(attempted),
                "compile_successes": len(compiled), "functional_successes": len(correct),
                "service_availability_denominator": len(requested),
                "service_availability": ratio(len(delivered), len(requested)),
                "compile_denominator": len(attempted), "compile_success_rate": ratio(len(compiled), len(attempted)),
                "functional_denominator": len(attempted), "functional_success_rate": ratio(len(correct), len(attempted)),
                "functional_given_compile_denominator": len(compiled),
                "functional_given_compile": ratio(len(correct), len(compiled)),
                "functional_per_response_denominator": len(delivered),
                "functional_per_response_rate": ratio(len(correct), len(delivered)),
                "successful_response_seconds_n": len(delivered),
                "mean_successful_response_seconds": sum(r["response_seconds"] for r in delivered) / len(delivered) if delivered else None,
                "request_seconds_n": len(requested),
                "mean_request_seconds": sum(r["response_seconds"] for r in requested) / len(requested) if requested else None,
                "invalid_responses": sum(r["status"] == "invalid_response" for r in subset),
                "api_quota_failures": sum(r["status"] == "api_quota_failure" for r in subset),
                "api_service_errors": sum(r["status"] == "api_service_error" for r in subset),
                "api_access_errors": sum(r["status"] == "api_access_error" for r in subset),
                "unavailable_or_skipped": sum(not r["request_made"] for r in subset),
                "status_counts_json": json.dumps(dict(sorted(Counter(r["status"] for r in subset).items())))})
    return summaries


def table(summaries: list[dict]) -> str:
    def fraction(n, d):
        return f"{n}/{d} ({n/d:.1%})" if d else "N/A (0 denominator)"
    lines = ["# Recorded evaluation results", "",
             "Generated from per-case records. Unavailable providers have no repair denominator.", "",
             "| Provider | Exact requested model | Category | Scheduled | Responses / requests | Compile / attempts | Functional / attempts | Functional / responses | Mean response seconds (n) |",
             "|---|---|---|---:|---|---|---|---|---|"]
    for m in summaries:
        latency = (f"{m['mean_successful_response_seconds']:.6f} ({m['successful_response_seconds_n']})"
                   if m["successful_response_seconds_n"] else "N/A (0)")
        lines.append(f"| {m['provider']} | {m['model']} | {m['category']} | {m['scheduled_cases']} | "
                     f"{fraction(m['responses_received'],m['requests_made'])} | "
                     f"{fraction(m['compile_successes'],m['repair_attempts'])} | "
                     f"{fraction(m['functional_successes'],m['repair_attempts'])} | "
                     f"{fraction(m['functional_successes'],m['responses_received'])} | {latency} |")
    lines += ["", "Compile and functional denominators are extracted nonempty patches with usable local evaluation.",
              "Service availability includes all submitted requests, including API errors. Local demo availability describes local generation.",
              "Mean response time includes delivered responses, even invalid ones; request time additionally includes API failures.",
              "Passes mean passing the saved visible and hidden tests, not proven program correctness.", ""]
    return "\n".join(lines)


def generate_summary(run: Path, destination: Path) -> list[dict]:
    rows = read_records(run)
    result = metrics(rows)
    if result:
        save_csv(destination / "metrics.csv", result)
    save_json(destination / "metrics.json", result)
    save_text(destination / "tables.md", table(result))
    save_text(destination / "generator.py", Path(__file__).read_text(encoding="utf-8-sig"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--check", action="store_true", help="Verify artifacts and reproduce the stored summary in memory")
    args = parser.parse_args()
    rows = read_records(args.run)
    expected = metrics(rows)
    if args.check:
        # Earlier runs retain their exact table schema and generator; never rewrite them.
        import importlib.util
        generator_path = args.run / "summary" / "generator.py"
        if not generator_path.exists():
            generator_path = args.run / "snapshot" / "summarize_results.py"
        spec = importlib.util.spec_from_file_location("saved_summary_generator", generator_path)
        saved = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(saved)
        expected = saved.metrics(rows)
        stored = json.loads((args.run / "summary" / "metrics.json").read_text(encoding="utf-8"))
        if stored != expected or (args.run / "summary" / "tables.md").read_text(encoding="utf-8") != saved.table(expected):
            raise ValueError("Stored summary cannot be reproduced")
        with (args.run / "summary" / "metrics.csv").open(newline="", encoding="utf-8") as handle:
            if list(csv.DictReader(handle)) != [{k: csv_value(v) for k, v in r.items()} for r in expected]:
                raise ValueError("Summary CSV cannot be reproduced")
        print(f"PASS: {len(rows)} per-case records, both CSV layers, summaries, and saved hashes")
    else:
        destination = new_run(args.run.parent.parent / "regenerated", "summary")
        generate_summary(args.run, destination)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
