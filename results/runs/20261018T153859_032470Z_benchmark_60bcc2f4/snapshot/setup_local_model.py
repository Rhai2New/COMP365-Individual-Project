"""Download a pinned official Qwen GGUF and Windows CPU llama.cpp build.

No API key or paid service. Files stay in ignored .tools/; downloads are verified.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

from evidence import ROOT, save_json, utc_now

TAG = "b11719"
REVISION = "ebb2015119c907b064c512bf053e945850b5875f"
REPO = "Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-coder-0.5b-instruct-q4_k_m.gguf"


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def download(url: str, target: Path, digest: str | None) -> str:
    if not target.exists():
        print(f"Downloading {target.name}", flush=True)
        with urllib.request.urlopen(url, timeout=60) as response, target.open("xb") as handle:
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
    hasher = hashlib.sha256()
    with target.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    actual = hasher.hexdigest()
    if digest and actual != digest.removeprefix("sha256:"):
        raise ValueError(f"Checksum mismatch for {target}; preserve failed download for inspection")
    return actual


def main() -> int:
    tools = ROOT / ".tools"
    tools.mkdir(exist_ok=True)
    release = get_json(f"https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/{TAG}")
    asset = next(a for a in release["assets"] if a["name"] == f"llama-{TAG}-bin-win-cpu-x64.zip")
    archive = tools / asset["name"]
    archive_hash = download(asset["browser_download_url"], archive, asset.get("digest"))
    extracted = tools / f"llama-{TAG}"
    if not extracted.exists():
        extracted.mkdir()
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                if not (extracted / member.filename).resolve().is_relative_to(extracted.resolve()):
                    raise ValueError("Unsafe zip path")
            package.extractall(extracted)
    metadata = get_json(f"https://huggingface.co/api/models/{REPO}/revision/{REVISION}?blobs=true")
    file_info = next(s for s in metadata["siblings"] if s["rfilename"] == MODEL_FILE)
    model_url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{MODEL_FILE}"
    model_hash = download(model_url, tools / MODEL_FILE, file_info["lfs"]["sha256"])
    binary = next(extracted.rglob("llama-server.exe"))
    info = {"downloaded_utc": utc_now(), "model_repository": REPO, "model_revision": REVISION,
            "model_filename": MODEL_FILE, "quantization": "Q4_K_M", "model_url": model_url,
            "model_sha256": model_hash, "model_size_bytes": (tools / MODEL_FILE).stat().st_size,
            "llama_cpp_tag": TAG, "binary_url": asset["browser_download_url"],
            "archive_sha256": archive_hash, "server_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "model_license": "Apache-2.0 (see official model repository)",
            "binary_license": "MIT (see llama.cpp repository)"}
    path = ROOT / "local_model_provenance.json"
    if not path.exists():
        save_json(path, info)
    else:
        old = json.loads(path.read_text(encoding="utf-8"))
        if old["model_sha256"] != model_hash or old["server_sha256"] != info["server_sha256"]:
            raise ValueError("Existing provenance does not match installed model/server")
    print(f"Verified local model: {model_hash}; server: {binary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
