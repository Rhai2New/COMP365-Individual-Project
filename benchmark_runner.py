#!/usr/bin/env python3
"""Final evidence-preserving extension of the Checkpoint 2 Java benchmark runner."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import time
from pathlib import Path

from bug_explainer import extract_patched_code, make_diff
from evidence import ROOT, environment, new_run, save_csv, save_json, save_text, seal, snapshot, utc_now
from repair_providers import DEFAULT_MODELS, LOCAL_MODEL, PROVIDERS, ProviderError, generate, make_prompt, preflight
from runtime_support import configure_java, evaluate_java, failure_context, normalize_output

BENCHMARK_DIR = ROOT / "benchmarks"
RESULTS_DIR = ROOT / "results"


def load_cases() -> tuple[list[dict], dict]:
    cases = json.loads((BENCHMARK_DIR / "manifest.json").read_text(encoding="utf-8"))
    hidden = json.loads((BENCHMARK_DIR / "hidden_tests.json").read_text(encoding="utf-8"))
    ids = [c["case_id"] for c in cases]
    if len(ids) != 20 or len(set(ids)) != 20 or set(ids) != set(hidden):
        raise ValueError("Retain 20 unique cases with hidden tests for every case")
    for case in cases:
        if not re.fullmatch(r"J\d{2}\.java", case["source"]):
            raise ValueError("Invalid benchmark source filename")
        if not case["tests"] or not hidden[case["case_id"]]:
            raise ValueError("Each case requires visible and hidden tests")
        if case["bug_type"].split(":")[0] not in {"syntax", "logic", "runtime"}:
            raise ValueError("Unknown category")
    return cases, hidden


def split_tests(case: dict, hidden: dict) -> list[dict]:
    return [dict(t, split=split, test_id=f"{split}_{i}")
            for split, tests in [("visible", case["tests"]), ("hidden", hidden[case["case_id"]])]
            for i, t in enumerate(tests, 1)]


def request_payload(provider: str, model: str | None, prompt: dict, max_tokens: int) -> dict:
    if provider == "llama_cpp":
        return {"model": model, "messages": [{"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}], "temperature": 0, "seed": 365,
                "max_tokens": max_tokens, "stream": False, "cache_prompt": False}
    if provider == "gemini":
        return {"model": model, "contents": prompt["user"], "config": {
            "system_instruction": prompt["system"], "temperature": 0, "max_output_tokens": max_tokens}}
    if provider == "openai":
        return {"model": model, "instructions": prompt["system"], "input": prompt["user"],
                "max_output_tokens": max_tokens, "store": False}
    return {"model": model, "system": prompt["system"], "prompt": prompt["user"],
            "stream": False, "options": {"temperature": 0, "seed": 365, "num_predict": max_tokens}}


def run_provider(case: dict, provider: str, model: str | None, run: Path,
                 hidden: dict, original: dict, *, unavailable: str | None = None,
                 max_tokens: int = 2048, timeout: float = 60) -> dict:
    """Save a per-case record even when no request can be made."""
    source_path = BENCHMARK_DIR / case["source"]
    source = source_path.read_text(encoding="utf-8")
    directory = run / "cases" / case["case_id"] / provider
    directory.mkdir(parents=True, exist_ok=False)
    save_text(directory / "original.java", source)
    save_json(directory / "original_evaluation.json", original)
    context = failure_context(original)
    save_text(directory / "failure_context.txt", context)
    prompt = make_prompt(source, "java", context)
    save_json(directory / "prompt.json", prompt)
    save_text(directory / "prompt.txt", prompt["system"] + "\n\n" + prompt["user"])
    save_json(directory / "request.json", request_payload(provider, model, prompt, max_tokens))
    tests = split_tests(case, hidden)
    save_json(directory / "evaluation_tests.json", tests)
    row = {"run_id": run.name, "case_id": case["case_id"], "source": case["source"],
           "language": "java", "bug_type": case["bug_type"], "category": case["bug_type"].split(":")[0],
           "provider": provider, "model": model, "resolved_model": None,
           "status": "configuration_unavailable", "request_made": False,
           "response_received": False, "repair_attempted": False, "patch_changed_source": None,
           "patch_compile_success": None, "visible_test_success": None,
           "hidden_test_success": None, "test_success": None, "response_seconds": None,
           "error": None, "artifact_dir": directory.relative_to(run).as_posix()}
    patched = None
    validation = None
    if unavailable:
        row["error"] = unavailable
        if unavailable.startswith("Circuit breaker"):
            row["status"] = "skipped_after_api_error"
        save_json(directory / "error.json", {"status": row["status"], "message": unavailable,
                                              "request_made": False})
    elif original["infrastructure_error"]:
        row.update(status="evaluation_infrastructure_error", error=original["infrastructure_error"])
    else:
        start = time.perf_counter()
        try:
            reply = generate(provider, model, prompt, max_tokens=max_tokens, timeout=timeout)
            row.update(response_seconds=time.perf_counter() - start, request_made=True,
                       response_received=True, resolved_model=reply.resolved_model)
            save_text(directory / "response.txt", reply.text)
            save_json(directory / "response_envelope.json", reply.envelope)
            patched = extract_patched_code(reply.text)
            row["status"] = "invalid_response" if patched is None else "patch_received"
        except ProviderError as exc:
            row.update(status=exc.status, request_made=exc.request_made,
                       response_seconds=time.perf_counter() - start if exc.request_made else None,
                       error=str(exc))
            save_json(directory / "error.json", {"status": exc.status, "message": str(exc),
                "http_status": exc.http_status, "body": exc.body, "request_made": exc.request_made})
    if patched is not None:
        row.update(repair_attempted=True, patch_changed_source=normalize_output(patched) != normalize_output(source))
        save_text(directory / "patch" / source_path.name, patched)
        save_text(directory / "patch.diff", make_diff(source, patched, source_path.name))
        validation = evaluate_java(patched, source_path.name, tests)
        if validation["infrastructure_error"]:
            row.update(status="evaluation_infrastructure_error", error=validation["infrastructure_error"])
        else:
            compiled = validation["compilation"]["success"]
            def passed(split):
                subset = [t for t in validation["tests"] if t["split"] == split]
                return bool(compiled and subset and all(t["success"] for t in subset))
            row.update(patch_compile_success=compiled, visible_test_success=passed("visible"),
                       hidden_test_success=passed("hidden"), test_success=validation["functional_success"])
            row["status"] = ("successful_repair" if row["test_success"] else
                             "compilation_failure" if not compiled else "functional_test_failure")
    save_json(directory / "validation.json", validation or {"not_run": True, "reason": row["status"]})
    save_json(directory / "record.json", row)
    save_csv(directory / "record.csv", [row])
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--providers", default="demo", help=",".join(PROVIDERS))
    parser.add_argument("--model", help="Exact override, only for a single non-demo provider")
    parser.add_argument("--gemini-model", default=DEFAULT_MODELS["gemini"])
    parser.add_argument("--openai-model", help="Required exact OpenAI model; no guessed default")
    parser.add_argument("--ollama-model", help="Exact installed local Ollama tag")
    parser.add_argument("--llama-model", default=LOCAL_MODEL)
    parser.add_argument("--case", action="append")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--results-root", type=Path, default=RESULTS_DIR / "runs")
    parser.add_argument("--output", help="Legacy label only; never overwrites this path")
    parser.add_argument("--allow-live", action="store_true", help="Enable cloud requests after checking billing/quota")
    parser.add_argument("--gemini-free-tier-confirmed", action="store_true",
                        help="Attest that this key's project is verified Free Tier with billing disabled")
    parser.add_argument("--gemini-min-interval", type=float, default=65,
                        help="Minimum seconds between Gemini request starts; default 65, no retries")
    parser.add_argument("--max-requests", type=int, default=1, help="Maximum cloud requests across this run")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    if not providers or len(set(providers)) != len(providers) or set(providers) - set(PROVIDERS):
        parser.error("Supply unique known providers: " + ",".join(PROVIDERS))
    if args.limit < 0 or args.max_requests < 0 or args.max_tokens < 1 or args.timeout <= 0 or args.gemini_min_interval < 0:
        parser.error("Limits must be nonnegative; tokens and timeout must be positive")
    models = {**DEFAULT_MODELS, "openai": args.openai_model, "ollama": args.ollama_model,
              "llama_cpp": args.llama_model}
    if args.model:
        llms = [p for p in providers if p != "demo"]
        if len(llms) != 1:
            parser.error("--model requires exactly one non-demo provider")
        models[llms[0]] = args.model
    cases, hidden = load_cases()
    if args.case:
        unknown = set(args.case) - {c["case_id"] for c in cases}
        if unknown:
            parser.error("Unknown case IDs: " + ",".join(sorted(unknown)))
        cases = [c for c in cases if c["case_id"] in args.case]
    if args.limit:
        cases = cases[:args.limit]
    configure_java()
    if not shutil.which("java") or not shutil.which("javac"):
        parser.error("Install a JDK and put java and javac on PATH (or set JAVA_HOME)")
    checks = {p: preflight(p, models.get(p)) for p in providers}
    run = new_run(args.results_root.resolve(), "benchmark")
    config = {"schema_version": 1, "run_id": run.name, "started_utc": utc_now(),
              "providers": providers, "models": {p: models.get(p) for p in providers},
              "case_ids": [c["case_id"] for c in cases], "preflight": checks,
              "allow_live": args.allow_live, "max_cloud_requests": args.max_requests,
              "gemini_free_tier_confirmed": args.gemini_free_tier_confirmed,
              "gemini_min_interval_seconds": args.gemini_min_interval,
              "max_output_tokens": args.max_tokens, "request_timeout_seconds": args.timeout,
              "retries": 0, "environment": environment(),
              "generation_settings": {"gemini": {"temperature": 0},
                  "openai": {"sampling": "provider default (model-dependent)"},
                  "llama_cpp": {"temperature": 0, "seed": 365, "cache_prompt": False},
                  "ollama": {"temperature": 0, "seed": 365}},
              "legacy_output_hint": args.output, "purpose": "live_or_local_benchmark"}
    provenance = ROOT / "local_model_provenance.json"
    if "llama_cpp" in providers and provenance.exists():
        config["local_model_provenance"] = json.loads(provenance.read_text(encoding="utf-8"))
    save_json(run / "config.json", config)
    snapshot(run)
    rows, circuits, cloud_requests = [], {}, 0
    last_gemini_start = None
    print(f"Evidence directory: {run}", flush=True)
    try:
        for case in cases:
            source = (BENCHMARK_DIR / case["source"]).read_text(encoding="utf-8")
            original = evaluate_java(source, case["source"], [dict(t, split="visible") for t in case["tests"]])
            for provider in providers:
                reason = circuits.get(provider)
                if not reason and not checks[provider]["available"]:
                    reason = checks[provider]["reason"]
                if not reason and provider in {"gemini", "openai"}:
                    if not args.allow_live:
                        reason = "Cloud evaluation disabled; pass --allow-live after checking billing/quota"
                    elif provider == "gemini" and not args.gemini_free_tier_confirmed:
                        reason = "Gemini billing tier unverified; no generation request made (free-tier-only policy)"
                    elif cloud_requests >= args.max_requests:
                        reason = "Cloud request limit reached; no request made"
                if not reason and provider == "gemini":
                    if last_gemini_start is not None:
                        time.sleep(max(0, args.gemini_min_interval - (time.monotonic() - last_gemini_start)))
                    last_gemini_start = time.monotonic()
                row = run_provider(case, provider, models.get(provider), run, hidden, original,
                                   unavailable=reason, max_tokens=args.max_tokens, timeout=args.timeout)
                rows.append(row)
                if row["request_made"] and provider in {"gemini", "openai"}:
                    cloud_requests += 1
                if row["status"].startswith("api_") or row["status"] == "provider_internal_error":
                    circuits[provider] = "Circuit breaker: stopped provider after " + row["status"]
                print(f"{case['case_id']} {provider}: {row['status']}", flush=True)
    finally:
        save_csv(run / "results.csv", rows, fields=list(rows[0]) if rows else ["run_id"])
        save_json(run / "completion.json", {"finished_utc": utc_now(), "records": len(rows),
                  "planned": len(cases) * len(providers), "complete": len(rows) == len(cases) * len(providers)})
        from summarize_results import generate_summary
        generate_summary(run, run / "summary")
        seal(run)
    print(f"Saved {len(rows)} records; summaries: {run / 'summary'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
