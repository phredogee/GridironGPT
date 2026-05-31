# gridiron_gpt/core/llm.py

import os
from typing import Optional

import requests

_DEFAULT_MODEL = "qwen3:8b"

SYSTEM_PROMPT = """You are a sharp fantasy football advisor. You have access to real player stats.

Rules:
- Answer using ONLY the player data provided — do not invent stats
- Be specific: name players, cite points, mention team/position
- Give a clear top recommendation with 1-2 sentences of reasoning
- If injury or surface notes are relevant to the question, mention them
- Keep it tight — no fluff, no disclaimers"""


def _ollama_native_url() -> str:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    base_url = base_url.rstrip("/")

    if base_url.endswith("/v1"):
        base_url = base_url[:-3]

    return f"{base_url}/api/chat"


def generate_advice(
    query: str,
    context_docs: list,
    model: str = _DEFAULT_MODEL,
) -> Optional[str]:
    """
    Generate fantasy advice using a local Ollama model.
    Uses Ollama's native /api/chat endpoint for reliable Qwen output.
    """
    model = os.environ.get("OLLAMA_MODEL", model)

    context = "\n".join(f"- {doc['text']}" for doc in context_docs[:5])

    payload = {
        "model": model,
        "stream": False,
        "think": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {query}\n\nPlayer data:\n{context}",
            },
        ],
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }

    try:
        response = requests.post(_ollama_native_url(), json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        content = data.get("message", {}).get("content", "")
        content = content.strip()

        if not content:
            return f"[LLM error: empty response from Ollama; raw response keys={list(data.keys())}]"

        return content

    except Exception as e:
        return f"[LLM error: {e}]"
