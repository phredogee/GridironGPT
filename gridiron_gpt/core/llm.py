# gridiron_gpt/core/llm.py

import os
from typing import Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

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


def _call_ollama(query: str, context: str, model: str) -> str:
    model = os.environ.get("OLLAMA_MODEL", model)

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

    response = requests.post(_ollama_native_url(), json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    content = data.get("message", {}).get("content", "").strip()

    if not content:
        return f"[LLM error: empty response from Ollama; raw response keys={list(data.keys())}]"

    return content


def _call_deepseek(query: str, context: str) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        return "[LLM error: DEEPSEEK_API_KEY is missing from .env]"

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )

    response = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {query}\n\nPlayer data:\n{context}",
            },
        ],
        temperature=0.3,
        max_tokens=512,
    )

    content = response.choices[0].message.content

    if not content:
        return "[LLM error: empty response from DeepSeek]"

    return content.strip()


def generate_advice(
    query: str,
    context_docs: list,
    model: str = _DEFAULT_MODEL,
) -> Optional[str]:
    """
    Generate fantasy advice using either:
    - local Ollama/Qwen
    - DeepSeek API

    Controlled by .env:

    LLM_PROVIDER=ollama
    or
    LLM_PROVIDER=deepseek
    """
    provider = os.environ.get("LLM_PROVIDER", "ollama").lower().strip()

    context = "\n".join(f"- {doc['text']}" for doc in context_docs[:5])

    try:
        if provider == "deepseek":
            return _call_deepseek(query, context)

        if provider == "ollama":
            return _call_ollama(query, context, model)

        return f"[LLM error: unknown LLM_PROVIDER '{provider}'. Use 'ollama' or 'deepseek'.]"

    except Exception as e:
        return f"[LLM error: {e}]"
