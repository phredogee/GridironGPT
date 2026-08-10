from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone

from gridiron_gpt.product.schedule_generator import GeneratedSchedule


class LeagueExportService:
    def schedule_csv(self, schedule: GeneratedSchedule, names: dict[str, str]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Week", "Away Team", "Home Team", "Divisional"])
        for game in schedule.matchups:
            writer.writerow(
                [
                    game.week,
                    names.get(game.away_team_id, game.away_team_id),
                    names.get(game.home_team_id, game.home_team_id),
                    "Yes" if game.divisional else "No",
                ]
            )
        return output.getvalue()

    def schedule_ical(
        self,
        schedule: GeneratedSchedule,
        names: dict[str, str],
        *,
        season_start: datetime,
        kickoff_hour_utc: int = 17,
    ) -> str:
        if season_start.tzinfo is None:
            raise ValueError("season_start must be timezone-aware")
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//GridironGPT//League Schedule//EN",
            "CALSCALE:GREGORIAN",
        ]
        for game in schedule.matchups:
            start = season_start + timedelta(weeks=game.week - 1)
            start = start.astimezone(timezone.utc).replace(
                hour=kickoff_hour_utc,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = start + timedelta(hours=3)
            away = names.get(game.away_team_id, game.away_team_id)
            home = names.get(game.home_team_id, game.home_team_id)
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:gridiron-{game.week}-{game.away_team_id}-{game.home_team_id}@gridirongpt",
                    f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
                    f"SUMMARY:{away} at {home}",
                    f"DESCRIPTION:Week {game.week}{' divisional game' if game.divisional else ''}",
                    "END:VEVENT",
                ]
            )
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"
