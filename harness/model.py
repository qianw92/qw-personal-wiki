"""Thin client for the local Gemma model served by Ollama."""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3n:e2b"


def generate(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": temperature},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except OSError as e:
        raise RuntimeError(
            "Could not reach the local Gemma model at "
            f"{OLLAMA_URL}. Start it with `ollama serve` "
            f"(and make sure `ollama pull {MODEL_NAME}` has been run)."
        ) from e
    return body.get("response", "").strip()
