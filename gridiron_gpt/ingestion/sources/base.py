from __future__ import annotations

from abc import ABC, abstractmethod

from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)


class SourceAdapter(ABC):
    """
    Contract for external GridironGPT ingestion sources.

    Adapters retrieve evidence from an external provider and convert
    provider-specific data into source-neutral SourceRecords.

    Adapters must not perform Cortex interpretation such as sentiment
    scoring, fantasy impact scoring, or recommendation generation.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the human-readable source name."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self) -> list[SourceRecord]:
        """
        Retrieve records from the external source.

        Returned records must contain source evidence only.
        """
        raise NotImplementedError
