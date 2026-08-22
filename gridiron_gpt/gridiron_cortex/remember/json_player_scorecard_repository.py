import json
from dataclasses import asdict
from pathlib import Path

from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.remember.player_scorecard_repository import (
    PlayerScorecardRepository,
)


class JsonPlayerScorecardRepository(PlayerScorecardRepository):
    """
    Append-only JSONL repository for player scorecard history.

    Each line represents one immutable scorecard snapshot.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def get_latest(self, player_id: str) -> PlayerScorecard | None:
        history = self.get_history(player_id)

        if not history:
            return None

        return history[-1]

    def get_history(self, player_id: str) -> list[PlayerScorecard]:
        scorecards = []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if record.get("player_id") != player_id:
                        continue

                    try:
                        scorecards.append(PlayerScorecard(**record))
                    except TypeError:
                        continue

        except OSError as exc:
            raise RuntimeError(
                f"Unable to read scorecard repository: {self.file_path}"
            ) from exc

        return scorecards

    def save(self, scorecard: PlayerScorecard) -> None:
        record = asdict(scorecard)

        try:
            with self.file_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record) + "\n")
        except OSError as exc:
            raise RuntimeError(
                f"Unable to save scorecard to: {self.file_path}"
            ) from exc

    def get_all_latest(self) -> list[PlayerScorecard]:
        latest_by_player: dict[str, PlayerScorecard] = {}

        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        scorecard = PlayerScorecard(**record)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    current = latest_by_player.get(scorecard.player_id)

                    if current is None:
                        latest_by_player[scorecard.player_id] = scorecard
                        continue

                    if (scorecard.last_updated or "") > (
                        current.last_updated or ""
                    ):
                        latest_by_player[scorecard.player_id] = scorecard

        except OSError as exc:
            raise RuntimeError(
                f"Unable to read scorecard repository: {self.file_path}"
            ) from exc

        return list(latest_by_player.values())
