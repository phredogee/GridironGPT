from __future__ import annotations


class ByeWeekService:
    """Derive team bye weeks from the published regular-season schedule."""

    REGULAR_SEASON_WEEKS = range(1, 19)

    def load(self, *, season: int) -> dict[str, int]:
        try:
            import nflreadpy as nfl

            frame = nfl.load_schedules(seasons=[season])
            if hasattr(frame, "to_pandas"):
                frame = frame.to_pandas()
        except Exception:
            return {}

        if frame is None or getattr(frame, "empty", True):
            return {}

        required = {"week", "home_team", "away_team"}
        if not required.issubset(frame.columns):
            return {}

        work = frame.copy()
        if "game_type" in work.columns:
            work = work[work["game_type"].astype(str).str.upper().eq("REG")]
        work = work[work["week"].isin(self.REGULAR_SEASON_WEEKS)]
        if work.empty:
            return {}

        teams = sorted(
            {
                str(team).strip().upper()
                for column in ("home_team", "away_team")
                for team in work[column].dropna().tolist()
                if str(team).strip()
            }
        )

        bye_weeks: dict[str, int] = {}
        for team in teams:
            played = set(
                int(week)
                for week in work.loc[
                    work["home_team"].astype(str).str.upper().eq(team)
                    | work["away_team"].astype(str).str.upper().eq(team),
                    "week",
                ].tolist()
            )
            missing = [week for week in self.REGULAR_SEASON_WEEKS if week not in played]
            if len(missing) == 1:
                bye_weeks[team] = missing[0]

        return bye_weeks
