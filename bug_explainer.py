#!/usr/bin/env python3
"""COMP 365 Checkpoint 1 prototype: Interactive Code Bug Explainer & Patch Generator.

The program accepts a small Java or C++ source file, captures its compiler error,
then generates a beginner-friendly explanation and localized patch.

Providers:
  demo   - local deterministic fallback for the included sample; no API key needed.
  openai - sends the source + compiler error to the OpenAI Responses API.
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
Analyze only the supplied Java or C++ program and compiler/runtime error.
Use beginner-friendly concepts. Do not redesign the whole program, introduce advanced
patterns, or change unrelated lines. Return a minimal fix.

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
    """Compile a source file in a temporary directory and return (success, output)."""
    if not compiler_available(language):
        compiler = "javac" if language == "java" else "g++"
        return False, f"Compiler '{compiler}' was not found on PATH."

    with tempfile.TemporaryDirectory(prefix="comp365_build_") as td:
        build_dir = Path(td)
        copied = build_dir / source_path.name
        copied.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

        if language == "java":
            command = ["javac", copied.name]
        else:
            command = ["g++", "-std=c++17", copied.name, "-o", "program"]

        proc = subprocess.run(
            command,
            cwd=build_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=20,
        )
        output = proc.stdout.strip()
        if not output:
            output = "Compilation succeeded with no compiler messages."
        return proc.returncode == 0, output


def compile_text(source_text: str, filename: str, language: str) -> tuple[bool, str]:
    """Compile source text while preserving the original filename (important for Java public classes)."""
    if not compiler_available(language):
        compiler = "javac" if language == "java" else "g++"
        return False, f"Compiler '{compiler}' was not found on PATH."

    with tempfile.TemporaryDirectory(prefix="comp365_verify_") as td:
        build_dir = Path(td)
        test_file = build_dir / filename
        test_file.write_text(source_text, encoding="utf-8")
        if language == "java":
            command = ["javac", test_file.name]
        else:
            command = ["g++", "-std=c++17", test_file.name, "-o", "program"]
        proc = subprocess.run(
            command, cwd=build_dir, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=20
        )
        output = proc.stdout.strip() or "Compilation succeeded with no compiler messages."
        return proc.returncode == 0, output


def make_diff(original: str, patched: str, filename: str) -> str:
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
    ).rstrip()


def demo_response(source: str, language: str, compiler_error: str) -> str:
    """Small local fallback used only so the checkpoint artifact can be tested offline."""
    patched = source
    root = "The compiler found a syntax error near a statement that is missing its terminator."
    explanation = (
        "In Java and C++, many statements end with a semicolon. The compiler reaches the end "
        "of the statement and cannot tell that the instruction is finished. Add the missing "
        "semicolon without changing the rest of the program."
    )

    # Included Java sample: add a semicolon to a println line when javac says ';' expected.
    if language == "java" and "';' expected" in compiler_error:
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("//")
                and not stripped.endswith((";", "{", "}"))
                and re.search(r"\b(System\.out\.(print|println)|return|[A-Za-z_][\w<>\[\]]*\s+\w+\s*=)", stripped)
            ):
                lines[i] = line.rstrip() + ";"
                break
        patched = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
    elif language == "cpp" and "expected" in compiler_error:
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.endswith((";", "{", "}")):
                if "cout" in stripped or "return" in stripped or "=" in stripped:
                    lines[i] = line.rstrip() + ";"
                    break
        patched = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
    else:
        root = "Demo mode could not identify this error with its intentionally small rule set."
        explanation = (
            "Use --provider openai for general Java/C++ debugging. Demo mode is only a local "
            "checkpoint fallback and is not the project's AI/ML component."
        )

    fence = "java" if language == "java" else "cpp"
    return (
        f"ROOT CAUSE:\n{root}\n\n"
        f"BEGINNER EXPLANATION:\n{explanation}\n\n"
        f"PATCHED CODE:\n```{fence}\n{patched.rstrip()}\n```"
    )


def openai_response(source: str, language: str, compiler_error: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI package is not installed. Run: py -m pip install -r requirements.txt"
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it in your terminal, then run the live test again."
        )

    client = OpenAI()
    user_input = f"""LANGUAGE: {language}

COMPILER/RUNTIME ERROR:
{compiler_error}

SOURCE CODE:
```{language}
{source}
```
"""
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=user_input,
    )
    return response.output_text.strip()


def extract_patched_code(response_text: str) -> str | None:
    match = re.search(
        r"PATCHED CODE:\s*```(?:java|cpp|c\+\+)?\s*\n(.*?)```",
        response_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() + "\n" if match else None


def print_block(title: str, text: str) -> None:
    width = 72
    print("=" * width)
    print(title)
    print("=" * width)
    print(text.rstrip())
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="COMP 365 code bug explainer checkpoint prototype")
    parser.add_argument("--source", required=True, help="Path to a .java or .cpp source file")
    parser.add_argument(
        "--provider",
        choices=["demo", "openai"],
        default="demo",
        help="demo runs offline; openai performs the live LLM API call",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.6-luna",
        help="OpenAI model used when --provider openai is selected",
    )
    parser.add_argument("--error-file", help="Optional text file containing a runtime/compiler error")
    parser.add_argument("--save-output", help="Optional path to save the full console report")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}", file=sys.stderr)
        return 2

    try:
        language = detect_language(source_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    source = source_path.read_text(encoding="utf-8")

    if args.error_file:
        compiler_error = Path(args.error_file).read_text(encoding="utf-8").strip()
        compile_ok = False
    else:
        compile_ok, compiler_error = compile_source(source_path, language)

    if compile_ok and not args.error_file:
        print("The source already compiles. Supply --error-file for a runtime/logic-error test.")
        return 1

    start = time.perf_counter()
    try:
        if args.provider == "openai":
            response_text = openai_response(source, language, compiler_error, args.model)
            provider_label = f"OpenAI Responses API ({args.model})"
        else:
            response_text = demo_response(source, language, compiler_error)
            provider_label = "Local demo fallback (no API call)"
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    latency = time.perf_counter() - start

    patched = extract_patched_code(response_text)
    verify_text = "No patched code block could be extracted for verification."
    patch_file = None
    if patched is not None:
        patch_file = source_path.with_name(source_path.stem + "_patched" + source_path.suffix)
        patch_file.write_text(patched, encoding="utf-8")
        verify_ok, verify_output = compile_text(patched, source_path.name, language)
        verify_text = (
            f"Patched file: {patch_file.name}\n"
            f"Compilation check: {'PASS' if verify_ok else 'FAIL'}\n"
            f"Compiler output: {verify_output}"
        )

    diff = make_diff(source, patched, source_path.name) if patched else "No diff available."

    report_parts = [
        ("CHECKPOINT 1 - INTERACTIVE CODE BUG EXPLAINER & PATCH GENERATOR", f"Provider: {provider_label}\nSource: {source_path.name}\nLanguage: {language}\nResponse latency: {latency:.3f} seconds"),
        ("ORIGINAL COMPILER / RUNTIME ERROR", compiler_error),
        ("PATCH ENGINE OUTPUT", response_text),
        ("LOCALIZED DIFF", diff),
        ("PATCH VERIFICATION", verify_text),
    ]

    full_report = ""
    for title, text in report_parts:
        section = f"{'=' * 72}\n{title}\n{'=' * 72}\n{text.rstrip()}\n\n"
        full_report += section
        print(section, end="")

    if args.save_output:
        output_path = Path(args.save_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_report, encoding="utf-8")
        print(f"Saved report to: {output_path.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
