# app/core/ai_client.py
import json
import httpx
from app.core import config


def generate_completion(
    system_prompt: str,
    user_prompt: str,
    response_format: str | None = "json",
    temperature: float = 0.2
) -> dict:
    """
    Unified chat completion function.
    Automatically routes to Ollama or Gemini based on config.AI_PROVIDER.
    Returns:
        {"success": bool, "content": dict | str, "provider": str, "model": str, "error": str | None}
    """
    provider = config.AI_PROVIDER.lower()

    if provider == "ollama":
        return _ollama_chat_completion(system_prompt, user_prompt, response_format, temperature)
    elif provider == "gemini":
        return _gemini_chat_completion(system_prompt, user_prompt, response_format, temperature)
    else:
        return {
            "success": False,
            "content": None,
            "provider": provider,
            "model": "unknown",
            "error": f"Unsupported AI_PROVIDER: '{provider}'. Supported: 'ollama', 'gemini'."
        }


def generate_embedding(text: str) -> list[float]:
    """
    Unified text embedding function.
    Routes to Ollama (nomic-embed-text) or Gemini (text-embedding-004).
    Returns list of floats (vector).
    """
    provider = config.AI_PROVIDER.lower()

    if provider == "ollama":
        return _ollama_embedding(text)
    elif provider == "gemini":
        return _gemini_embedding(text)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: '{provider}'")


# ==============================================================================
# Internal Provider Adapters
# ==============================================================================

def _ollama_chat_completion(system_prompt: str, user_prompt: str, response_format: str | None, temperature: float) -> dict:
    url = f"{config.OLLAMA_BASE_URL}/api/chat"
    model = config.OLLAMA_CHAT_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {"temperature": temperature}
    }
    if response_format == "json":
        payload["format"] = "json"

    try:
        with httpx.Client(timeout=45.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            raw_text = res.json().get("message", {}).get("content", "")

            content = json.loads(raw_text) if response_format == "json" else raw_text
            return {
                "success": True,
                "content": content,
                "provider": "ollama",
                "model": model,
                "error": None
            }
    except Exception as err:
        return {
            "success": False,
            "content": None,
            "provider": "ollama",
            "model": model,
            "error": str(err)
        }


def _ollama_embedding(text: str) -> list[float]:
    url = f"{config.OLLAMA_BASE_URL}/api/embeddings"
    model = config.OLLAMA_EMBED_MODEL

    payload = {"model": model, "prompt": text}
    with httpx.Client(timeout=30.0) as client:
        res = client.post(url, json=payload)
        res.raise_for_status()
        return res.json()["embedding"]


def _gemini_chat_completion(system_prompt: str, user_prompt: str, response_format: str | None, temperature: float) -> dict:
    """Gemini API Adapter using standard REST."""
    if not config.GEMINI_API_KEY:
        return {
            "success": False,
            "content": None,
            "provider": "gemini",
            "model": config.GEMINI_CHAT_MODEL,
            "error": "GEMINI_API_KEY is not set in environment."
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_CHAT_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"System Instruction:\n{system_prompt}\n\nTask:\n{user_prompt}"}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json" if response_format == "json" else "text/plain"
        }
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            content = json.loads(raw_text) if response_format == "json" else raw_text
            return {
                "success": True,
                "content": content,
                "provider": "gemini",
                "model": config.GEMINI_CHAT_MODEL,
                "error": None
            }
    except Exception as err:
        return {
            "success": False,
            "content": None,
            "provider": "gemini",
            "model": config.GEMINI_CHAT_MODEL,
            "error": str(err)
        }


def _gemini_embedding(text: str) -> list[float]:
    """Gemini Embeddings Adapter using standard REST."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_EMBED_MODEL}:embedContent?key={config.GEMINI_API_KEY}"
    payload = {
        "model": f"models/{config.GEMINI_EMBED_MODEL}",
        "content": {"parts": [{"text": text}]}
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.post(url, json=payload)
        res.raise_for_status()
        return res.json()["embedding"]["values"]