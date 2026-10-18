#!/usr/bin/env python3
"""COMP 365 Individual Project: Interactive Code Bug Explainer & Patch Generator.

Final technical version; preserves the Checkpoint 2 baseline.

The module supports four repair providers:
  demo   - a deliberately small local rule-based baseline.
  openai - the existing OpenAI Responses API adapter.
  gemini - the existing GitHub Gemini adapter, restored in this copy.
  ollama - an optional installed local LLM.

The failure context may be a compiler error, runtime failure, or failed test output.
Checkpoint 2 evaluates compilation success and functional test success separately.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SYSTEM_INSTRUCTIONS = """You are a debugging assistant for an introductory programming course.
Analyze only the supplied Java or C++ program and the supplied failure context.
The failure context may be a compiler error, runtime error, or failed black-box test.
Use beginner-friendly concepts and make the smallest general repair that fixes the underlying bug.
Do not redesign the whole program, add unrelated features, hardcode the provided expected outputs,
or introduce advanced patterns when a simple introductory fix is available.
Preserve the program's input/output behavior except for correcting the bug.

Return EXACTLY these sections:
ROOT CAUSE:
<1-3 concise sentences>

BEGINNER EXPLANATION:
<plain-English explanation suitable for an introductory student>

PATCHED CODE:
```<language>
<complete corrected source code>
```
"""


def detect_language(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".java":
        return "java"
    if suffix in {".cpp", ".cc", ".cxx"}:
        return "cpp"
    raise ValueError("Only .java and .cpp/.cc/.cxx source files are supported.")


def compiler_available(language: str) -> bool:
    return shutil.which("javac" if language == "java" else "g++") is not None


def compile_source(source_path: Path, language: str) -> tuple[bool, str]:
    return compile_text(source_path.read_text(encoding="utf-8"), source_path.name, language)


def compile_text(source_text: str, filename: str, language: str) -> tuple[bool, str]:
    from runtime_support import configure_java, execute
    configure_java()
    if not compiler_available(language):
        return False, "Compiler not found on PATH."
    with tempfile.TemporaryDirectory(prefix="comp365_verify_") as td:
        build_dir = Path(td)
        (build_dir / filename).write_text(source_text, encoding="utf-8")
        command = (["javac", "-encoding", "UTF-8", "-proc:none", filename] if language == "java" else
                   ["g++", "-std=c++17", filename, "-o", "program"])
        result = execute(command, build_dir, timeout=20)
        output = result["stdout"] + result["stderr"]
        if result["timed_out"]:
            output += "Compilation timed out."
        if result["execution_error"]:
            output += result["execution_error"]
        return result["returncode"] == 0, output or "Compilation succeeded with no compiler messages."


def make_diff(original: str, patched: str, filename: str) -> str:
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
    ).rstrip()


def demo_response(source: str, language: str, failure_context: str) -> str:
    """Small local baseline. Intentionally narrow so it is a meaningful comparison."""
    patched = source
    root = "The local rule-based baseline could not identify this bug with its small rule set."
    explanation = (
        "This baseline only contains a few hand-written syntax rules. It leaves the program "
        "unchanged when none of those rules match."
    )

    # Java missing semicolon rule.
    if language == "java" and "';' expected" in failure_context:
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("//")
                and not stripped.endswith((";", "{", "}"))
                and re.search(
                    r"\b(System\.out\.(print|println)|return|[A-Za-z_][\w<>\[\]]*\s+\w+\s*=)",
                    stripped,
                )
            ):
                lines[i] = line.rstrip() + ";"
                root = "The statement is missing its terminating semicolon."
                explanation = "Java statements such as this one normally end with a semicolon."
                break
        patched = "\n".join(lines) + ("\n" if source.endswith("\n") else "")

    # C++ missing semicolon fallback retained from Checkpoint 1.
    elif language == "cpp" and "expected" in failure_context:
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.endswith((";", "{", "}")):
                if "cout" in stripped or "return" in stripped or "=" in stripped:
                    lines[i] = line.rstrip() + ";"
                    root = "A statement appears to be missing its terminating semicolon."
                    explanation = "The baseline added a semicolon to the first matching statement."
                    break
        patched = "\n".join(lines) + ("\n" if source.endswith("\n") else "")

    fence = "java" if language == "java" else "cpp"
    return (
        f"ROOT CAUSE:\n{root}\n\n"
        f"BEGINNER EXPLANATION:\n{explanation}\n\n"
        f"PATCHED CODE:\n```{fence}\n{patched.rstrip()}\n```"
    )


def openai_response(source: str, language: str, failure_context: str, model: str) -> str:
    from repair_providers import generate, make_prompt
    return generate("openai", model, make_prompt(source, language, failure_context)).text


def gemini_response(source: str, language: str, failure_context: str, model: str) -> str:
    """Gemini generate_content adapter recovered from GitHub commit 778a729."""
    from repair_providers import generate, make_prompt
    return generate("gemini", model, make_prompt(source, language, failure_context)).text


def extract_patched_code(response_text: str) -> str | None:
    match = re.search(
        r"PATCHED CODE:\s*```(?:java|cpp|c\+\+)?\s*\n(.*?)```",
        response_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() + "\n" if match and match.group(1).strip() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="COMP 365 code bug explainer")
    parser.add_argument("--source", required=True)
    parser.add_argument("--provider", choices=["demo", "openai", "gemini", "ollama"], default="demo")
    parser.add_argument("--model", help="Exact provider model identifier")
    parser.add_argument("--allow-live", action="store_true", help="Explicitly enable cloud requests")
    parser.add_argument("--gemini-free-tier-confirmed", action="store_true",
                        help="Attest this key's project is verified Free Tier with billing disabled")
    parser.add_argument("--error-file", help="Optional compiler/runtime/test failure text file")
    parser.add_argument("--save-output")
    args = parser.parse_args()

    from runtime_support import configure_java
    configure_java()
    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}", file=sys.stderr)
        return 2

    language = detect_language(source_path)
    source = source_path.read_text(encoding="utf-8")

    if args.error_file:
        failure_context = Path(args.error_file).read_text(encoding="utf-8").strip()
        original_compile_ok = None
    else:
        original_compile_ok, failure_context = compile_source(source_path, language)
        if original_compile_ok:
            print("The source compiles. For a logic bug, pass a test failure using --error-file.")
            return 1

    from evidence import new_run, save_json, save_text, environment, seal
    from repair_providers import DEFAULT_MODELS, generate, make_prompt, ProviderError
    model = args.model or DEFAULT_MODELS.get(args.provider)
    if not model:
        parser.error("--model is required for OpenAI and Ollama")
    if args.provider in {"gemini", "openai"} and not args.allow_live:
        parser.error("Cloud requests require --allow-live after you verify quota/billing")
    if args.provider == "gemini" and not args.gemini_free_tier_confirmed:
        parser.error("Gemini requires verified Free Tier with billing disabled: --gemini-free-tier-confirmed")
    run = new_run(Path(__file__).resolve().parent / "results" / "interactive", args.provider)
    save_text(run / source_path.name, source)
    prompt = make_prompt(source, language, failure_context)
    save_json(run / "prompt.json", prompt)
    save_json(run / "config.json", {"provider": args.provider, "model": model,
                                  "environment": environment(), "max_tokens": 2048, "retries": 0})
    start = time.perf_counter()
    try:
        reply = generate(args.provider, model, prompt)
    except ProviderError as exc:
        save_json(run / "error.json", {"status": exc.status, "message": str(exc),
                  "http_status": exc.http_status, "body": exc.body,
                  "request_made": exc.request_made, "seconds": time.perf_counter() - start})
        seal(run)
        print(f"ERROR: {exc.status}: {exc}; evidence: {run}", file=sys.stderr)
        return 3
    latency = time.perf_counter() - start
    response_text = reply.text
    provider_label = f"{args.provider} ({model})"
    save_text(run / "response.txt", response_text)
    save_json(run / "response_envelope.json", reply.envelope)
    save_json(run / "timing.json", {"response_seconds": latency, "resolved_model": reply.resolved_model})
    patched = extract_patched_code(response_text)
    if patched is None:
        verify_text = "No nonempty patched code block could be extracted for verification."
        diff = "No diff available."
    else:
        patch_file = run / "patch" / source_path.name
        save_text(patch_file, patched)
        verify_ok, verify_output = compile_text(patched, source_path.name, language)
        save_json(run / "compilation.json", {"success": verify_ok, "output": verify_output})
        verify_text = (f"Patched file: {patch_file}\n"
                       f"Compilation check: {'PASS' if verify_ok else 'FAIL'}\n"
                       f"Compiler output: {verify_output}\nFunctional tests: NOT RUN (use benchmark_runner.py)")
        diff = make_diff(source, patched, source_path.name)
        save_text(run / "patch.diff", diff)

    report_parts = [
        ("COMP 365 - INTERACTIVE CODE BUG EXPLAINER & PATCH GENERATOR", f"Provider: {provider_label}\nSource: {source_path.name}\nLanguage: {language}\nResponse latency: {latency:.3f} seconds"),
        ("FAILURE CONTEXT", failure_context),
        ("PATCH ENGINE OUTPUT", response_text),
        ("LOCALIZED DIFF", diff),
        ("PATCH COMPILATION VERIFICATION", verify_text),
    ]

    full_report = ""
    for title, text in report_parts:
        section = f"{'=' * 72}\n{title}\n{'=' * 72}\n{text.rstrip()}\n\n"
        full_report += section
        print(section, end="")

    save_text(run / "report.txt", full_report)
    if args.save_output:
        print("--save-output is a legacy hint; report preserved in unique run directory.")
    seal(run)
    print(f"Saved evidence: {run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
