import json
from dataclasses import asdict
from pathlib import Path

from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.storage.player_scorecard_repository import (
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
                        # Ignore malformed records for now so one bad line
                        # does not make the entire history unreadable.
                        continue

                    if record.get("player_id") != player_id:
                        continue

                    try:
                        scorecards.append(PlayerScorecard(**record))
                    except TypeError:
                        # Ignore records that do not match the current model.
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
