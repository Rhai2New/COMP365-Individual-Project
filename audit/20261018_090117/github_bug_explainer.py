#!/usr/bin/env python3
"""COMP 365 Individual Project: Interactive Code Bug Explainer & Patch Generator.

Checkpoint 2 version.

The module supports three repair providers:
  demo   - a deliberately small local rule-based baseline.
  openai - LLM repair using the OpenAI Responses API.
  gemini - LLM repair using the Google Gemini API.

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

Do not redesign the whole program, add unrelated features, hardcode provided expected outputs,
or introduce advanced patterns when a simple introductory fix is available.

Preserve the program's intended input/output behavior except for correcting the bug.

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

    raise ValueError(
        "Only .java and .cpp/.cc/.cxx source files are supported."
    )


def compiler_available(language: str) -> bool:
    compiler = "javac" if language == "java" else "g++"
    return shutil.which(compiler) is not None


def compile_source(source_path: Path, language: str) -> tuple[bool, str]:
    if not compiler_available(language):
        compiler = "javac" if language == "java" else "g++"
        return False, f"Compiler '{compiler}' was not found on PATH."

    with tempfile.TemporaryDirectory(prefix="comp365_build_") as td:
        build_dir = Path(td)

        copied = build_dir / source_path.name
        copied.write_text(
            source_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        if language == "java":
            command = ["javac", copied.name]
        else:
            command = [
                "g++",
                "-std=c++17",
                copied.name,
                "-o",
                "program",
            ]

        proc = subprocess.run(
            command,
            cwd=build_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=20,
        )

        output = (
            proc.stdout.strip()
            or "Compilation succeeded with no compiler messages."
        )

        return proc.returncode == 0, output


def compile_text(
    source_text: str,
    filename: str,
    language: str,
) -> tuple[bool, str]:

    if not compiler_available(language):
        compiler = "javac" if language == "java" else "g++"
        return False, f"Compiler '{compiler}' was not found on PATH."

    with tempfile.TemporaryDirectory(prefix="comp365_verify_") as td:
        build_dir = Path(td)

        test_file = build_dir / filename
        test_file.write_text(
            source_text,
            encoding="utf-8",
        )

        if language == "java":
            command = ["javac", test_file.name]
        else:
            command = [
                "g++",
                "-std=c++17",
                test_file.name,
                "-o",
                "program",
            ]

        proc = subprocess.run(
            command,
            cwd=build_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=20,
        )

        output = (
            proc.stdout.strip()
            or "Compilation succeeded with no compiler messages."
        )

        return proc.returncode == 0, output


def make_diff(
    original: str,
    patched: str,
    filename: str,
) -> str:

    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
    ).rstrip()


def demo_response(
    source: str,
    language: str,
    failure_context: str,
) -> str:
    """Small local baseline intentionally limited to a few hand-written rules."""

    patched = source

    root = (
        "The local rule-based baseline could not identify this bug "
        "with its small rule set."
    )

    explanation = (
        "This baseline only contains a few hand-written syntax rules. "
        "It leaves the program unchanged when none of those rules match."
    )

    if language == "java" and "';' expected" in failure_context:
        lines = source.splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()

            if (
                stripped
                and not stripped.startswith("//")
                and not stripped.endswith((";", "{", "}"))
                and re.search(
                    r"\b("
                    r"System\.out\.(print|println)"
                    r"|return"
                    r"|[A-Za-z_][\w<>\[\]]*\s+\w+\s*="
                    r")",
                    stripped,
                )
            ):
                lines[i] = line.rstrip() + ";"

                root = (
                    "The statement is missing its terminating semicolon."
                )

                explanation = (
                    "Java statements such as this one normally end "
                    "with a semicolon."
                )

                break

        patched = "\n".join(lines)

        if source.endswith("\n"):
            patched += "\n"

    elif language == "cpp" and "expected" in failure_context:
        lines = source.splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()

            if (
                stripped
                and not stripped.startswith("//")
                and not stripped.endswith((";", "{", "}"))
            ):
                if (
                    "cout" in stripped
                    or "return" in stripped
                    or "=" in stripped
                ):
                    lines[i] = line.rstrip() + ";"

                    root = (
                        "A statement appears to be missing its "
                        "terminating semicolon."
                    )

                    explanation = (
                        "The baseline added a semicolon to the first "
                        "matching statement."
                    )

                    break

        patched = "\n".join(lines)

        if source.endswith("\n"):
            patched += "\n"

    fence = "java" if language == "java" else "cpp"

    return (
        f"ROOT CAUSE:\n{root}\n\n"
        f"BEGINNER EXPLANATION:\n{explanation}\n\n"
        f"PATCHED CODE:\n```{fence}\n{patched.rstrip()}\n```"
    )


def openai_response(
    source: str,
    language: str,
    failure_context: str,
    model: str,
) -> str:

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI package missing. Run: python -m pip install openai"
        ) from exc

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set in this terminal."
        )

    client = OpenAI(api_key=api_key)

    user_input = f"""LANGUAGE:
{language}

FAILURE CONTEXT:
{failure_context}

SOURCE CODE:
```{language}
{source}
```

Analyze the bug and return the required structured response.
"""

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=user_input,
    )

    result = response.output_text

    if not result:
        raise RuntimeError("OpenAI returned no text.")

    return result.strip()


def gemini_response(
    source: str,
    language: str,
    failure_context: str,
    model: str,
) -> str:

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "Gemini package missing. Run: python -m pip install -U google-genai"
        ) from exc

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set in this terminal."
        )

    client = genai.Client(api_key=api_key)

    user_input = f"""{SYSTEM_INSTRUCTIONS}

LANGUAGE:
{language}

FAILURE CONTEXT:
{failure_context}

SOURCE CODE:
```{language}
{source}
```

Analyze the bug and return the required structured response.
"""

    response = client.models.generate_content(
        model=model,
        contents=user_input,
    )

    result = response.text

    if not result:
        raise RuntimeError("Gemini returned no text.")

    return result.strip()


def extract_patched_code(response_text: str) -> str | None:
    match = re.search(
        r"PATCHED CODE:\s*```(?:java|cpp|c\+\+)?\s*\n(.*?)```",
        response_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if match:
        return match.group(1).strip() + "\n"

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="COMP 365 code bug explainer"
    )

    parser.add_argument(
        "--source",
        required=True,
    )

    parser.add_argument(
        "--provider",
        choices=["demo", "openai", "gemini"],
        default="demo",
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override",
    )

    parser.add_argument(
        "--error-file",
        help="Optional compiler/runtime/test failure text file",
    )

    parser.add_argument(
        "--save-output",
    )

    args = parser.parse_args()

    source_path = Path(args.source).resolve()

    if not source_path.exists():
        print(
            f"ERROR: Source file not found: {source_path}",
            file=sys.stderr,
        )
        return 2

    language = detect_language(source_path)

    source = source_path.read_text(
        encoding="utf-8"
    )

    if args.error_file:
        failure_context = Path(
            args.error_file
        ).read_text(
            encoding="utf-8"
        ).strip()

        original_compile_ok = None

    else:
        original_compile_ok, failure_context = compile_source(
            source_path,
            language,
        )

        if original_compile_ok:
            print(
                "The source compiles. For a logic bug, "
                "pass a test failure using --error-file."
            )
            return 1

    start = time.perf_counter()

    try:
        if args.provider == "openai":
            model = args.model or "gpt-5.6-luna"

            response_text = openai_response(
                source,
                language,
                failure_context,
                model,
            )

            provider_label = (
                f"OpenAI Responses API ({model})"
            )

        elif args.provider == "gemini":
            model = args.model or "gemini-3.8-flash"

            response_text = gemini_response(
                source,
                language,
                failure_context,
                model,
            )

            provider_label = (
                f"Google Gemini API ({model})"
            )

        else:
            response_text = demo_response(
                source,
                language,
                failure_context,
            )

            provider_label = (
                "Local rule-based demo baseline"
            )

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 3

    latency = time.perf_counter() - start

    patched = extract_patched_code(
        response_text
    )

    if patched is None:
        verify_text = (
            "No patched code block could be extracted for verification."
        )

        diff = "No diff available."

    else:
        patch_file = source_path.with_name(
            source_path.stem
            + "_patched"
            + source_path.suffix
        )

        patch_file.write_text(
            patched,
            encoding="utf-8",
        )

        verify_ok, verify_output = compile_text(
            patched,
            source_path.name,
            language,
        )

        verify_text = (
            f"Patched file: {patch_file.name}\n"
            f"Compilation check: "
            f"{'PASS' if verify_ok else 'FAIL'}\n"
            f"Compiler output: {verify_output}"
        )

        diff = make_diff(
            source,
            patched,
            source_path.name,
        )

    report_parts = [
        (
            "COMP 365 - INTERACTIVE CODE BUG EXPLAINER & PATCH GENERATOR",
            (
                f"Provider: {provider_label}\n"
                f"Source: {source_path.name}\n"
                f"Language: {language}\n"
                f"Response latency: {latency:.3f} seconds"
            ),
        ),
        (
            "FAILURE CONTEXT",
            failure_context,
        ),
        (
            "PATCH ENGINE OUTPUT",
            response_text,
        ),
        (
            "LOCALIZED DIFF",
            diff,
        ),
        (
            "PATCH COMPILATION VERIFICATION",
            verify_text,
        ),
    ]

    full_report = ""

    for title, text in report_parts:
        section = (
            f"{'=' * 72}\n"
            f"{title}\n"
            f"{'=' * 72}\n"
            f"{text.rstrip()}\n\n"
        )

        full_report += section
        print(section, end="")

    if args.save_output:
        output_path = Path(
            args.save_output
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            full_report,
            encoding="utf-8",
        )

        print(
            f"Saved report to: {output_path.resolve()}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())