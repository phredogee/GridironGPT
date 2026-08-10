from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _validate_share(name: str, value: float | None) -> None:
    if value is not None and not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _validate_count(name: str, value: int | None) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True)
class CanonicalUsageState:
    """Canonical snapshot of observed player opportunity and participation."""

    player_id: str
    player_name: str
    season: int
    week: int
    team: str | None = None
    position: str | None = None

    snaps: int | None = None
    snap_share: float | None = None
    routes: int | None = None
    route_participation: float | None = None

    carries: int | None = None
    targets: int | None = None
    carry_share: float | None = None
    target_share: float | None = None

    red_zone_carries: int | None = None
    red_zone_targets: int | None = None
    red_zone_opportunities: int | None = None

    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "canonical usage state"
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.player_id.strip():
            raise ValueError("player_id is required")
        if not self.player_name.strip():
            raise ValueError("player_name is required")
        if self.season <= 0:
            raise ValueError("season must be positive")
        if self.week <= 0:
            raise ValueError("week must be positive")

        for name in (
            "snaps",
            "routes",
            "carries",
            "targets",
            "red_zone_carries",
            "red_zone_targets",
            "red_zone_opportunities",
        ):
            _validate_count(name, getattr(self, name))

        for name in (
            "snap_share",
            "route_participation",
            "carry_share",
            "target_share",
        ):
            _validate_share(name, getattr(self, name))

    @property
    def touches(self) -> int | None:
        if self.carries is None and self.targets is None:
            return None
        return (self.carries or 0) + (self.targets or 0)

    @property
    def opportunity_concentration(self) -> float | None:
        """Simple observed workload concentration when rush/target shares exist."""
        shares = [
            share
            for share in (self.carry_share, self.target_share)
            if share is not None
        ]
        if not shares:
            return None
        return sum(shares) / len(shares)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observed_at"] = self.observed_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalUsageState":
        values = dict(payload)
        observed_at = values.get("observed_at")
        if isinstance(observed_at, str):
            values["observed_at"] = datetime.fromisoformat(observed_at)
        return cls(**values)
