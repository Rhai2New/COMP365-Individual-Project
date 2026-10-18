"""Start the pinned local server, run evaluation, and stop this server afterwards."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

from evidence import ROOT, new_run, save_json
from repair_providers import LOCAL_MODEL
from setup_local_model import MODEL_FILE, TAG


def main() -> int:
    binary = next((ROOT / ".tools" / f"llama-{TAG}").rglob("llama-server.exe"), None)
    model = ROOT / ".tools" / MODEL_FILE
    if binary is None or not model.is_file():
        raise SystemExit("Run: py -3.12 setup_local_model.py")
    from evidence import sha256
    provenance = json.loads((ROOT / "local_model_provenance.json").read_text(encoding="utf-8"))
    if sha256(binary) != provenance["server_sha256"] or sha256(model) != provenance["model_sha256"]:
        raise SystemExit("Installed local server/model does not match recorded hashes")
    # Never claim or stop a server belonging to another process.
    import socket
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 18080)) == 0:
            raise SystemExit("Port 18080 is occupied; stop or inspect that server first")
    logs = new_run(ROOT / "results" / "server_logs", "llama_cpp")
    command = [str(binary), "-m", str(model), "--host", "127.0.0.1", "--port", "18080",
               "--alias", LOCAL_MODEL, "-c", "4096", "-t", "8", "-np", "1", "--seed", "365"]
    save_json(logs / "command.json", {"command": command, "cwd": str(ROOT)})
    with (logs / "server.stdout.txt").open("x", encoding="utf-8") as stdout, \
         (logs / "server.stderr.txt").open("x", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            for attempt in range(120):
                if process.poll() is not None:
                    raise RuntimeError(f"Local server exited; inspect {logs}")
                try:
                    with urllib.request.urlopen("http://127.0.0.1:18080/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.5)
            else:
                raise RuntimeError(f"Local server failed to become ready; inspect {logs}")
            # The default cloud flag is off; Gemini rows record unavailability without a request.
            args = [sys.executable, str(ROOT / "benchmark_runner.py"),
                    "--providers", "demo,gemini,llama_cpp", "--timeout", "120", *sys.argv[1:]]
            return subprocess.run(args, cwd=ROOT).returncode
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
