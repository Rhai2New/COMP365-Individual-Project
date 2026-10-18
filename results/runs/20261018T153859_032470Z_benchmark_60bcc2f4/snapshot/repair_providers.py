"""Adapters for the existing baseline/Gemini/OpenAI and optional local Ollama.

One request only, no automatic SDK retries. Exact response text is not stripped.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse

PROVIDERS = ("demo", "gemini", "openai", "ollama", "llama_cpp")
DEFAULT_MODELS = {"demo": "local-rule-baseline-v1", "gemini": "gemini-3.8-flash"}
LOCAL_MODEL = "Qwen2.5-Coder-0.5B-Instruct-Q4_K_M"


def load_saved_gemini_key() -> bool:
    """Read only the named Windows user variables; never print or persist keys.

    Registry values may be newer than the environment inherited by this process.
    Installing the value in the process also enables error redaction. Evaluated
    compiler/program subprocesses remove credential variables.
    """
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return True
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as registry:
                for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                    try:
                        value, _ = winreg.QueryValueEx(registry, name)
                    except FileNotFoundError:
                        continue
                    if isinstance(value, str) and value.strip():
                        os.environ[name] = value
                        return True
        except OSError:
            pass
    return False


@dataclass
class Reply:
    text: str
    envelope: dict
    resolved_model: str | None = None


class ProviderError(Exception):
    def __init__(self, status: str, message: str, *, request_made: bool = False,
                 http_status: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status = status
        self.request_made = request_made
        self.http_status = http_status
        self.body = body


def redact(text: str) -> str:
    for name, value in os.environ.items():
        if ("API_KEY" in name or name.endswith("TOKEN")) and len(value) >= 8:
            text = text.replace(value, "<REDACTED>")
    text = re.sub(r"AIza[\w-]{30,}", "<REDACTED_GOOGLE_KEY>", text)
    return re.sub(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}", "<REDACTED_OPENAI_KEY>", text)


def make_prompt(source: str, language: str, context: str) -> dict:
    from bug_explainer import SYSTEM_INSTRUCTIONS
    return {"system": SYSTEM_INSTRUCTIONS,
            "user": f"LANGUAGE: {language}\n\nFAILURE CONTEXT:\n{context}\n\n"
                    f"SOURCE CODE:\n```{language}\n{source}\n```\n"}


def ollama_url() -> str:
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    parsed = urlparse(host)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"} or parsed.username:
        raise ProviderError("configuration_unavailable", "Ollama must use a local HTTP endpoint.")
    return host


def local_models() -> list[dict]:
    try:
        with urllib.request.urlopen(ollama_url() + "/api/tags", timeout=2) as response:
            return json.load(response).get("models", [])
    except (OSError, ValueError) as exc:
        raise ProviderError("configuration_unavailable", "Local Ollama server is unavailable.") from exc


def preflight(provider: str, model: str | None) -> dict:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    if not model:
        return {"available": False, "reason": "An exact model identifier must be supplied."}
    if provider == "demo":
        return {"available": model == DEFAULT_MODELS["demo"], "reason": "Built-in rule baseline"}
    if provider in {"gemini", "openai"}:
        if provider == "gemini":
            load_saved_gemini_key()
        key = "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
        module = "google.genai" if provider == "gemini" else "openai"
        if not os.getenv(key) and not (provider == "gemini" and os.getenv("GOOGLE_API_KEY")):
            return {"available": False, "reason": f"{key} is not set; no live request made."}
        try:
            installed = importlib.util.find_spec(module) is not None
        except ModuleNotFoundError:
            installed = False
        return {"available": installed, "reason": "Credentials present; quota/access unverified" if installed
                else f"Missing dependency: {module}"}
    if provider == "llama_cpp":
        try:
            with urllib.request.urlopen("http://127.0.0.1:18080/v1/models", timeout=2) as response:
                models = json.load(response)
            return {"available": any(m["id"] == model for m in models["data"]),
                    "reason": "Local llama.cpp model ID must match", "model_metadata": models}
        except (OSError, ValueError) as exc:
            return {"available": False, "reason": "Local llama.cpp server unavailable"}
    try:
        models = local_models()
        selected = next((m for m in models if model in {m.get("name"), m.get("model")}), None)
        return {"available": bool(selected), "reason": "Installed local model" if selected else "Model not installed",
                "model_metadata": selected}
    except ProviderError as exc:
        return {"available": False, "reason": str(exc)}


def classify_exception(exc: Exception) -> ProviderError:
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    try:
        status = int(status) if status is not None else None
    except (TypeError, ValueError):
        status = None
    message = redact(str(exc))
    # Use structured HTTP status first; text is only a fallback for SDK variations.
    if status == 429 or (status is None and re.search(r"quota|resource_exhausted|rate.limit", message, re.I)):
        category = "api_quota_failure"
    elif status in {400, 401, 403, 404, 422}:
        category = "api_access_error"
    elif status is not None and status >= 500:
        category = "api_service_error"
    elif any(word in type(exc).__name__.lower() for word in ("timeout", "connection", "network")):
        category = "api_service_error"
    else:
        category = "provider_internal_error"
    body = getattr(exc, "body", None)
    return ProviderError(category, message, request_made=True, http_status=status,
                         body=redact(json.dumps(body, default=str)) if body is not None else None)


def generate(provider: str, model: str, prompt: dict, *, max_tokens: int = 2048,
             timeout: float = 60) -> Reply:
    from bug_explainer import demo_response
    if provider == "demo":
        # The baseline receives the identical source/context, via a separate local adapter.
        match = re.search(r"SOURCE CODE:\n```(\w+)\n(.*)\n```\n$", prompt["user"], re.S)
        if not match:
            raise ProviderError("provider_internal_error", "Malformed baseline prompt")
        context = prompt["user"].split("FAILURE CONTEXT:\n", 1)[1].split("\n\nSOURCE CODE:", 1)[0]
        text = demo_response(match.group(2), match.group(1), context)
        return Reply(text, {"provider": "demo", "model": model, "text": text}, model)
    check = preflight(provider, model)
    if not check["available"]:
        raise ProviderError("configuration_unavailable", check["reason"])
    try:
        if provider == "openai":
            from openai import OpenAI
            with OpenAI(max_retries=0, timeout=timeout) as client:
                response = client.responses.create(model=model, instructions=prompt["system"],
                    input=prompt["user"], max_output_tokens=max_tokens, store=False)
                return Reply(response.output_text or "", response.model_dump(mode="json"), response.model)
        if provider == "gemini":
            from google import genai
            from google.genai import types
            with genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
                    http_options=types.HttpOptions(timeout=int(timeout * 1000),
                        retry_options=types.HttpRetryOptions(attempts=1))) as client:
                response = client.models.generate_content(model=model, contents=prompt["user"],
                    config=types.GenerateContentConfig(system_instruction=prompt["system"],
                                                        temperature=0, max_output_tokens=max_tokens))
                return Reply(response.text or "", response.model_dump(mode="json"),
                             getattr(response, "model_version", None))
        if provider == "llama_cpp":
            payload = {"model": model, "messages": [{"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]}], "temperature": 0,
                       "seed": 365, "max_tokens": max_tokens, "stream": False, "cache_prompt": False}
            req = urllib.request.Request("http://127.0.0.1:18080/v1/chat/completions",
                data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
            data = json.loads(raw)
            data["raw_http_response"] = raw
            return Reply(data["choices"][0]["message"].get("content") or "", data, data.get("model"))
        payload = {"model": model, "system": prompt["system"], "prompt": prompt["user"],
                   "stream": False, "options": {"temperature": 0, "seed": 365, "num_predict": max_tokens}}
        req = urllib.request.Request(ollama_url() + "/api/generate", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.load(response)
        return Reply(data.get("response", ""), data, data.get("model"))
    except ProviderError:
        raise
    except Exception as exc:
        raise classify_exception(exc) from exc
