from datetime import datetime, timedelta, timezone

import pytest

from gridiron_gpt.football_state.models.availability_report import AvailabilityReport
from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    PracticeParticipation,
)
from gridiron_gpt.football_state.services.availability_reconciler import AvailabilityReconciler


BASE = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)


def report(hours=0, **overrides):
    values = {
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "team": "ATL",
        "source": "NFL injury report",
        "observed_at": BASE + timedelta(hours=hours),
    }
    values.update(overrides)
    return AvailabilityReport(**values)


def test_latest_official_designation_wins_over_newer_unofficial_report():
    state = AvailabilityReconciler().reconcile([
        report(
            hours=1,
            designation=AvailabilityDesignation.OUT,
            official=True,
        ),
        report(
            hours=2,
            source="news article",
            designation=AvailabilityDesignation.QUESTIONABLE,
            official=False,
        ),
    ])

    assert state.designation == AvailabilityDesignation.OUT
    assert state.available is False


def test_latest_official_report_supersedes_older_official_report():
    state = AvailabilityReconciler().reconcile([
        report(hours=1, designation=AvailabilityDesignation.QUESTIONABLE, official=True),
        report(hours=3, designation=AvailabilityDesignation.ACTIVE, official=True),
    ])

    assert state.designation == AvailabilityDesignation.ACTIVE
    assert state.available is True


def test_practice_and_designation_are_reconciled_independently():
    state = AvailabilityReconciler().reconcile([
        report(
            hours=1,
            designation=AvailabilityDesignation.QUESTIONABLE,
            official=True,
        ),
        report(
            hours=2,
            practice_participation=PracticeParticipation.LIMITED,
            injury="hamstring",
            official=True,
        ),
    ])

    assert state.designation == AvailabilityDesignation.QUESTIONABLE
    assert state.practice_participation == PracticeParticipation.LIMITED
    assert state.injury == "hamstring"


def test_unofficial_reports_are_used_when_no_official_evidence_exists():
    state = AvailabilityReconciler().reconcile([
        report(hours=1, source="beat reporter", practice_participation=PracticeParticipation.DNP),
        report(hours=2, source="team reporter", practice_participation=PracticeParticipation.LIMITED),
    ])

    assert state.practice_participation == PracticeParticipation.LIMITED


def test_reconciliation_preserves_contributing_evidence():
    reports = [
        report(hours=1, designation=AvailabilityDesignation.QUESTIONABLE, official=True),
        report(hours=2, practice_participation=PracticeParticipation.FULL, official=True),
    ]

    state = AvailabilityReconciler().reconcile(reports)

    assert len(state.evidence["reports"]) == 2
    assert state.effective_at == BASE + timedelta(hours=2)


def test_empty_reports_are_rejected():
    with pytest.raises(ValueError, match="at least one"):
        AvailabilityReconciler().reconcile([])


def test_reports_for_different_players_are_rejected():
    with pytest.raises(ValueError, match="same player"):
        AvailabilityReconciler().reconcile([
            report(),
            report(player_id="allgeier", player_name="Tyler Allgeier"),
        ])
