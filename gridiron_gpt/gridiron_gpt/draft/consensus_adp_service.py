from __future__ import annotations

from dataclasses import dataclass
from statistics import median
import math
import re
import unicodedata


@dataclass(frozen=True)
class ConsensusAdpRecord:
    player_name: str
    consensus_adp: float
    source_count: int
    adp_min: float
    adp_max: float
    adp_spread: float
    source_values: dict[str, float]


class ConsensusAdpService:
    """Combine independent ADP feeds into one robust market consensus.

    Consensus uses the median so one unusually aggressive or stale source does
    not dominate the market input. With two sources, Python's median is their
    arithmetic midpoint. Source values remain attached for UI/export provenance.
    """

    def build(
        self,
        sources: dict[str, dict[str, float]],
        *,
        minimum_sources: int = 1,
    ) -> dict[str, ConsensusAdpRecord]:
        if minimum_sources <= 0:
            raise ValueError("minimum_sources must be positive")

        buckets: dict[str, dict[str, object]] = {}
        for source_name, values in sources.items():
            source = str(source_name).strip()
            if not source:
                continue
            for player_name, raw_adp in (values or {}).items():
                adp = self._finite_positive(raw_adp)
                if adp is None:
                    continue
                display_name = str(player_name).strip()
                key = self.name_key(display_name)
                if not key:
                    continue
                bucket = buckets.setdefault(
                    key,
                    {"player_name": display_name, "source_values": {}},
                )
                source_values = bucket["source_values"]
                assert isinstance(source_values, dict)
                source_values[source] = adp

        consensus: dict[str, ConsensusAdpRecord] = {}
        for key, bucket in buckets.items():
            source_values = dict(bucket["source_values"])
            if len(source_values) < minimum_sources:
                continue
            values = sorted(source_values.values())
            center = float(median(values))
            low = float(values[0])
            high = float(values[-1])
            consensus[key] = ConsensusAdpRecord(
                player_name=str(bucket["player_name"]),
                consensus_adp=center,
                source_count=len(values),
                adp_min=low,
                adp_max=high,
                adp_spread=round(high - low, 3),
                source_values=source_values,
            )
        return consensus

    @staticmethod
    def name_key(name: str) -> str:
        value = unicodedata.normalize("NFKD", str(name))
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"[^a-z0-9]", "", value.casefold())

    @staticmethod
    def _finite_positive(value) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(numeric) or numeric <= 0:
            return None
        return numeric
