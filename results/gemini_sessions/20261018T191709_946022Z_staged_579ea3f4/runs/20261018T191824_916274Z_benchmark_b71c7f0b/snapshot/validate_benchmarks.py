"""Validate category labels and test oracles using authored positive controls.

These repairs are harness controls, never provider outputs or model results.
"""
from __future__ import annotations

import json
from pathlib import Path

from benchmark_runner import BENCHMARK_DIR, load_cases, split_tests
from evidence import ROOT, environment, new_run, save_csv, save_json, save_text, seal, snapshot
from runtime_support import evaluate_java

# Minimal, explicitly authored reference edits, isolated from prompt construction.
REFERENCE_EDITS = {
    "J01": [('System.out.println("Hello")', 'System.out.println("Hello");')],
    "J02": [('System.out.println(x * 2;', 'System.out.println(x * 2);')],
    "J03": [(None, "}\n")],
    "J04": [('int total == 7;', 'int total = 7;')],
    "J05": [('a - b', 'a + b')],
    "J06": [('i < n', 'i <= n')],
    "J07": [('b < a', 'b > a')],
    "J08": [('n % 2 == 0', 'n % 2 != 0')],
    "J09": [('(a + b) / 2', '(a + b) / 2.0')],
    "J10": [('answer == "yes"', 'answer.equals("yes")')],
    "J11": [('age < 0 && age > 120', 'age < 0 || age > 120')],
    "J12": [('i <= values.length', 'i < values.length')],
    "J13": [('int max = 0;', 'int max = Integer.MIN_VALUE;')],
    "J14": [('length + width', 'length * width')],
    "J15": [('positives--;', 'positives++;')],
    "J16": [('product += value;', 'product *= value;')],
    "J17": [('score > 60', 'score >= 60')],
    "J18": [('b = a;', 'b = temp;')],
    "J19": [('b > min', 'b < min')],
    "J20": [('int average = total / count;', 'int average = count == 0 ? 0 : total / count;')],
}


def reference_source(case_id: str, source: str) -> str:
    for before, after in REFERENCE_EDITS[case_id]:
        if before is None:
            source += after
        else:
            if source.count(before) != 1:
                raise ValueError(f"Reference edit mismatch: {case_id}: {before}")
            source = source.replace(before, after)
    return source


def oracle(case_id: str, stdin: str) -> str:
    constants = {"J01": "Hello", "J02": "8", "J03": "positive", "J04": "7", "J12": "12"}
    if case_id in constants:
        return constants[case_id]
    if case_id == "J10":
        return "accepted" if stdin.splitlines()[0] == "yes" else "rejected"
    nums = list(map(int, stdin.split()))
    a = nums[0]
    if case_id in {"J05", "J07", "J09", "J14", "J18", "J19", "J20"}:
        b = nums[1]
    if case_id == "J05": return str(a + b)
    if case_id == "J06": return str(sum(range(1, a + 1)))
    if case_id == "J07": return str(max(a, b))
    if case_id == "J08": return "even" if a % 2 == 0 else "odd"
    if case_id == "J09": return str((a + b) / 2)
    if case_id == "J11": return "valid" if 0 <= a <= 120 else "invalid"
    if case_id == "J13": return str(max(nums[1:1+a]))
    if case_id == "J14": return str(a * b)
    if case_id == "J15": return str(sum(v > 0 for v in nums[1:1+a]))
    if case_id == "J16":
        product = 1
        for v in nums[1:1+a]: product *= v
        return str(product)
    if case_id == "J17": return "pass" if a >= 60 else "fail"
    if case_id == "J18": return f"{b} {a}"
    if case_id == "J19": return str(min(a, b))
    if case_id == "J20": return "undefined" if b == 0 else str(int(a / b))
    raise ValueError(case_id)


def main() -> int:
    cases, hidden = load_cases()
    run = new_run(ROOT / "results" / "validation", "benchmark_controls")
    save_json(run / "config.json", {"purpose": "authored_positive_controls_not_model_results",
                                    "environment": environment()})
    snapshot(run)
    rows = []
    for case in cases:
        case_id = case["case_id"]
        source = (BENCHMARK_DIR / case["source"]).read_text(encoding="utf-8")
        tests = split_tests(case, hidden)
        oracle_ok = all(oracle(case_id, t["input"]) == t["expected"] for t in tests)
        original = evaluate_java(source, case["source"], tests)
        fixed = reference_source(case_id, source)
        control = evaluate_java(fixed, case["source"], tests)
        category = case["bug_type"].split(":")[0]
        compiled = original["compilation"]["success"]
        crashed = any(t["returncode"] not in (0, None) for t in original["tests"])
        category_ok = (not compiled if category == "syntax" else
                       compiled and not original["functional_success"] and
                       (crashed if category == "runtime" else not crashed))
        row = {"case_id": case_id, "category": category, "classification_verified": category_ok,
               "oracle_verified": oracle_ok, "original_compiles": compiled,
               "original_functional_success": original["functional_success"],
               "authored_control_success": control["functional_success"],
               "visible_tests": len(case["tests"]), "hidden_tests": len(hidden[case_id])}
        save_json(run / case_id / "original_evaluation.json", original)
        save_json(run / case_id / "authored_control_evaluation.json", control)
        save_text(run / case_id / case["source"], fixed)
        rows.append(row)
        print(f"{case_id}: category={category_ok}, oracle={oracle_ok}, authored control={control['functional_success']}", flush=True)
    save_csv(run / "validation.csv", rows)
    ok = all(r["classification_verified"] and r["oracle_verified"] and r["authored_control_success"] for r in rows)
    save_json(run / "summary.json", {"passed": ok, "cases": len(rows), "visible_tests": sum(r["visible_tests"] for r in rows),
                                    "hidden_tests": sum(r["hidden_tests"] for r in rows), "rows": rows})
    seal(run)
    print(f"{'PASS' if ok else 'FAIL'}: {run}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
