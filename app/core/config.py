# app/core/config.py
import os

# AI Provider: "ollama" or "gemini"
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")

# Ollama Settings (Local)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Gemini Settings (Cloud fallback)
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-flash")
GEMINI_EMBED_MODEL: str = os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004")