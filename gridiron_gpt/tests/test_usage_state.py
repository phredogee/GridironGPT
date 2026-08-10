from datetime import datetime, timezone

import pytest

from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState


NOW = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)


def usage(**overrides):
    values = {
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "season": 2026,
        "week": 3,
        "team": "ATL",
        "position": "RB",
        "snaps": 52,
        "snap_share": 0.76,
        "routes": 24,
        "route_participation": 0.72,
        "carries": 18,
        "targets": 8,
        "carry_share": 18 / 22,
        "target_share": 8 / 14,
        "red_zone_carries": 4,
        "red_zone_targets": 2,
        "red_zone_opportunities": 6,
        "observed_at": NOW,
        "source": "nflverse",
    }
    values.update(overrides)
    return CanonicalUsageState(**values)


def test_usage_state_captures_observed_workload():
    state = usage()

    assert state.snaps == 52
    assert state.routes == 24
    assert state.carries == 18
    assert state.targets == 8
    assert state.touches == 26


def test_usage_state_preserves_exact_share_precision():
    state = usage()

    assert state.carry_share == 18 / 22
    assert state.target_share == 8 / 14
    assert state.opportunity_concentration == ((18 / 22) + (8 / 14)) / 2


def test_usage_state_allows_partial_provider_coverage():
    state = usage(
        snaps=None,
        snap_share=None,
        routes=None,
        route_participation=None,
    )

    assert state.snaps is None
    assert state.routes is None
    assert state.touches == 26
    assert state.opportunity_concentration is not None


def test_usage_state_returns_none_when_opportunity_is_unknown():
    state = usage(carries=None, targets=None, carry_share=None, target_share=None)

    assert state.touches is None
    assert state.opportunity_concentration is None


def test_usage_state_round_trips():
    original = usage(evidence={"game_id": "2026_03_ATL_TB"})

    restored = CanonicalUsageState.from_dict(original.to_dict())

    assert restored == original
    assert restored.observed_at == NOW


def test_invalid_share_is_rejected():
    with pytest.raises(ValueError, match="snap_share"):
        usage(snap_share=1.1)


def test_negative_count_is_rejected():
    with pytest.raises(ValueError, match="targets"):
        usage(targets=-1)


def test_player_identity_is_required():
    with pytest.raises(ValueError, match="player_id"):
        usage(player_id="")
