# gridiron_gpt/provider_banner.py

def get_banner(provider: str) -> str:
    provider = provider.lower()

    if provider == "openai":
        return "🤖 OpenAI Diagnostics\n─────────────────────"

    return (
        f"❓ {provider.title()} Diagnostics\n"
        "──────────────────────────────"
    )
