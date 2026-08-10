from __future__ import annotations

from gridiron_gpt.football_state.models.availability_report import AvailabilityReport
from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    CanonicalAvailabilityState,
    PracticeParticipation,
)


class AvailabilityReconciler:
    """Reconcile multiple availability observations into one canonical state."""

    def reconcile(self, reports: list[AvailabilityReport]) -> CanonicalAvailabilityState:
        if not reports:
            raise ValueError("reports must contain at least one availability observation")

        player_ids = {report.player_id for report in reports}
        if len(player_ids) != 1:
            raise ValueError("all availability reports must describe the same player")

        ordered = sorted(reports, key=lambda report: report.observed_at)
        latest = ordered[-1]

        designation_report = self._latest_preferred(
            [report for report in ordered if report.designation is not None]
        )
        practice_report = self._latest_preferred(
            [report for report in ordered if report.practice_participation is not None]
        )
        injury_report = self._latest_preferred(
            [report for report in ordered if report.injury]
        )

        designation = (
            designation_report.designation
            if designation_report and designation_report.designation is not None
            else AvailabilityDesignation.UNKNOWN
        )
        practice = (
            practice_report.practice_participation
            if practice_report and practice_report.practice_participation is not None
            else PracticeParticipation.NOT_REPORTED
        )

        contributing = []
        for report in ordered:
            contributing.append({
                "source": report.source,
                "observed_at": report.observed_at.isoformat(),
                "official": report.official,
                "designation": report.designation.value if report.designation else None,
                "practice_participation": (
                    report.practice_participation.value
                    if report.practice_participation
                    else None
                ),
                "injury": report.injury,
            })

        return CanonicalAvailabilityState(
            player_id=latest.player_id,
            player_name=latest.player_name,
            team=self._latest_value(ordered, "team"),
            designation=designation,
            practice_participation=practice,
            injury=injury_report.injury if injury_report else None,
            effective_at=max(report.observed_at for report in ordered),
            source="availability reconciliation",
            evidence={"reports": contributing},
        )

    @staticmethod
    def _latest_preferred(reports: list[AvailabilityReport]) -> AvailabilityReport | None:
        if not reports:
            return None
        official = [report for report in reports if report.official]
        candidates = official or reports
        return max(candidates, key=lambda report: report.observed_at)

    @staticmethod
    def _latest_value(reports: list[AvailabilityReport], field_name: str):
        for report in reversed(reports):
            value = getattr(report, field_name)
            if value is not None:
                return value
        return None
