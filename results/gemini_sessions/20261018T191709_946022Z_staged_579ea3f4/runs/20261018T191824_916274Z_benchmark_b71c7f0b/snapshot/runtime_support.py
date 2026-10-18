"""Shared local execution; compilers and programs run in temporary directories."""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path


def configure_java() -> None:
    if shutil.which("javac") and shutil.which("java"):
        return
    candidates = []
    if os.getenv("JAVA_HOME"):
        candidates.append(Path(os.environ["JAVA_HOME"]) / "bin")
    for base, pattern in [(Path.home() / ".jdks", "*/bin"),
                          (Path("C:/NCAT"), "jdk*/bin"),
                          (Path("C:/Program Files/Eclipse Adoptium"), "*/bin")]:
        if base.exists():
            candidates.extend(sorted(base.glob(pattern), reverse=True))
    for candidate in candidates:
        if (candidate / "javac.exe").is_file() and (candidate / "java.exe").is_file():
            os.environ["PATH"] = str(candidate) + os.pathsep + os.environ.get("PATH", "")
            return


def normalize_output(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


def execute(command: list[str], cwd: Path, stdin: str = "", timeout: float = 5) -> dict:
    start = time.perf_counter()
    # Evaluated code should not inherit API credentials from the experiment runner.
    child_env = {k: v for k, v in os.environ.items()
                 if not any(token in k.upper() for token in ("API_KEY", "SECRET", "TOKEN", "PASSWORD"))}
    try:
        proc = subprocess.run(command, cwd=cwd, input=stdin, text=True,
                              encoding="utf-8", errors="replace", capture_output=True,
                              timeout=timeout, env=child_env)
        result = dict(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      timed_out=False, execution_error=None)
    except subprocess.TimeoutExpired as exc:
        def decoded(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else (value or "")
        result = dict(returncode=None, stdout=decoded(exc.stdout), stderr=decoded(exc.stderr),
                      timed_out=True, execution_error=None)
    except OSError as exc:
        result = dict(returncode=None, stdout="", stderr="", timed_out=False,
                      execution_error=f"{type(exc).__name__}: {exc}")
    result.update(command=command, seconds=time.perf_counter() - start)
    return result


def evaluate_java(source: str, filename: str, tests: list[dict]) -> dict:
    import tempfile
    configure_java()
    with tempfile.TemporaryDirectory(prefix="comp365_final_") as td:
        build = Path(td)
        (build / filename).write_text(source, encoding="utf-8")
        compilation = execute(["javac", "-encoding", "UTF-8", "-proc:none", filename], build, timeout=20)
        compilation["success"] = compilation["returncode"] == 0
        outcomes = []
        if compilation["success"]:
            for index, test in enumerate(tests, 1):
                outcome = execute(["java", "-Xmx128m", "-cp", ".", Path(filename).stem],
                                  build, test.get("input", ""))
                outcome.update(index=index, test_id=test.get("test_id", f"test_{index}"),
                               split=test.get("split", "visible"), input=test.get("input", ""),
                               expected=test["expected"])
                outcome["success"] = (outcome["returncode"] == 0 and
                                      normalize_output(outcome["stdout"]) == normalize_output(test["expected"]))
                outcomes.append(outcome)
        infrastructure_error = compilation["execution_error"] or next(
            (t["execution_error"] for t in outcomes if t["execution_error"]), None)
        return {"compilation": compilation, "tests": outcomes,
                "infrastructure_error": infrastructure_error,
                "functional_success": bool(compilation["success"] and outcomes and
                                           all(t["success"] for t in outcomes))}


def failure_context(evaluation: dict) -> str:
    comp = evaluation["compilation"]
    if not comp["success"]:
        return "COMPILER ERROR:\n" + comp["stdout"] + comp["stderr"] + (
            "\nCompilation timed out." if comp["timed_out"] else "")
    failures = []
    for test in evaluation["tests"]:
        if not test["success"]:
            failures.append(f"Test {test['index']} FAILED\nInput: {test['input']!r}\n"
                            f"Expected: {test['expected']!r}\nActual: {test['stdout']!r}\n"
                            f"Stderr: {test['stderr']}\nExit code: {test['returncode']}\n"
                            f"Timed out: {test['timed_out']}")
    return "TEST FAILURE:\n" + "\n\n".join(failures) if failures else "All visible tests passed."
