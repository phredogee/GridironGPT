from __future__ import annotations


class ProviderRateLimitError(RuntimeError):
    """Signal that a provider explicitly requested slower retry behavior."""

    def __init__(
        self,
        message: str = "Provider rate limit exceeded",
        *,
        retry_after_seconds: float | None = None,
    ) -> None:
        if retry_after_seconds is not None and retry_after_seconds < 0:
            raise ValueError("retry_after_seconds cannot be negative")
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds
