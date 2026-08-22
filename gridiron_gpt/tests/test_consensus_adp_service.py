import math

from gridiron_gpt.draft.consensus_adp_service import ConsensusAdpService


def test_builds_median_consensus_and_spread_across_sources():
    service = ConsensusAdpService()

    result = service.build(
        {
            "ESPN": {"Bijan Robinson": 2.8},
            "NFL": {"Bijan Robinson": 3.3},
            "FFC": {"Bijan Robinson": 4.1},
        }
    )

    row = result[service.name_key("Bijan Robinson")]
    assert row.consensus_adp == 3.3
    assert row.source_count == 3
    assert row.adp_min == 2.8
    assert row.adp_max == 4.1
    assert row.adp_spread == 1.3
    assert row.source_values == {"ESPN": 2.8, "NFL": 3.3, "FFC": 4.1}


def test_two_source_consensus_uses_midpoint():
    service = ConsensusAdpService()

    result = service.build(
        {
            "ESPN": {"Puka Nacua": 5.0},
            "NFL": {"Puka Nacua": 7.0},
        }
    )

    assert result[service.name_key("Puka Nacua")].consensus_adp == 6.0


def test_normalizes_common_name_punctuation_between_sources():
    service = ConsensusAdpService()

    result = service.build(
        {
            "ESPN": {"A.J. Brown": 18.0},
            "NFL": {"AJ Brown": 20.0},
        }
    )

    row = result[service.name_key("A.J. Brown")]
    assert row.source_count == 2
    assert row.consensus_adp == 19.0


def test_ignores_invalid_and_non_finite_adp_values():
    service = ConsensusAdpService()

    result = service.build(
        {
            "ESPN": {
                "Good Player": 10,
                "Zero Player": 0,
                "NaN Player": math.nan,
            },
            "NFL": {"Good Player": 12, "Infinite Player": math.inf},
        }
    )

    assert set(result) == {service.name_key("Good Player")}


def test_minimum_sources_filters_single_source_players():
    service = ConsensusAdpService()

    result = service.build(
        {
            "ESPN": {"Player A": 10.0, "Player B": 20.0},
            "NFL": {"Player A": 12.0},
        },
        minimum_sources=2,
    )

    assert set(result) == {service.name_key("Player A")}
