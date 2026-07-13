"""Context manager for structured PHRED CLI feedback."""

import logging
from types import TracebackType
from typing import Self

from modules.utils import EMOJIS


class FeedbackContext:
    """Collect and render status-oriented CLI feedback."""

    def __init__(self, status: str, dry_run: bool = False) -> None:
        self.status = status
        self.dry_run = dry_run
        self.logs: list[str] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exc_value is not None:
            self.logs.append(f"Exception: {exc_value}")

        # False means exceptions are not suppressed.
        return False

    def log(self, message: str) -> None:
        """Add a message to the feedback log."""
        self.logs.append(message)

    def debug(self, message: str) -> None:
        """Record and emit a structured debugging message."""
        prefix = "DRY-RUN " if self.dry_run else ""
        log_message = f"{prefix}DEBUG: {message}"

        self.logs.append(log_message)
        print(log_message)
        logging.getLogger(__name__).debug(log_message)

    def render(self) -> str:
        """Return collected messages as newline-separated text."""
        return "\n".join(self.logs)

    def __str__(self) -> str:
        emoji = EMOJIS.get(self.status.casefold(), "❓")
        rendered_logs = " | ".join(self.logs)

        return f"{emoji} {rendered_logs}".rstrip()
