# gridiron_gpt/provider_guard.py

from importlib.metadata import PackageNotFoundError, version


def detect_installed_providers():
    providers = []

    try:
        version("openai")
        providers.append("openai")
    except PackageNotFoundError:
        pass

    return providers
