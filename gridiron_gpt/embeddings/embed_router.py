# embeddings/embed_router.py
from gridiron_gpt.embeddings.openai_embed import embed_with_openai
from gridiron_gpt.provider_guard import detect_installed_providers


def embed(
    text: str,
    provider: str = "auto",
    dry_run: bool = False,
):
    if provider == "auto":
        providers = detect_installed_providers()

        if not providers:
            raise RuntimeError(
                "No supported embedding provider is installed."
            )

        provider = providers[0]

    print(f"📦 Embedding with provider: {provider}")

    if dry_run:
        print("🧪 Dry-run mode: no actual API calls\n")

    if provider == "openai":
        return embed_with_openai(
            text,
            dry_run=dry_run,
        )

    raise ValueError(f"❌ Unknown provider: {provider}")
