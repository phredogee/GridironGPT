class RosterAdvisor:
    def __init__(
        self,
        ranked_players,
        recommendation_from_score,
        confidence_from_signals,
    ):
        self.ranked_players = ranked_players
        self.recommendation_from_score = recommendation_from_score
        self.confidence_from_signals = confidence_from_signals

    @staticmethod
    def _score(data: dict) -> float:
        return data.get(
            "adjusted_score",
            data.get("score", 0.0),
        )

    def answer(self, question: str) -> dict:
        normalized = question.strip().lower()

        if not normalized:
            return {
                "answer": "Enter a roster question.",
                "confidence": 0,
                "details": [],
            }

        if "top buy" in normalized or "best buy" in normalized:
            return self._top_recommendation("BUY")

        if "highest score" in normalized or "top player" in normalized:
            return self._highest_scoring_player()

        matched_player = self._find_player(normalized)

        if matched_player is not None:
            return self._explain_player(*matched_player)

        return {
            "answer": (
                "I could not identify a supported player or question yet."
            ),
            "confidence": 0,
            "details": [
                "Try: Why is Tank Dell a WATCH?",
                "Try: Who is my top BUY candidate?",
                "Try: Which player has the highest score?",
            ],
        }

    def _find_player(self, question: str):
        for (player, team), data in self.ranked_players:
            if player.lower() in question:
                return player, team, data

        return None

    def _highest_scoring_player(self) -> dict:
        if not self.ranked_players:
            return {
                "answer": "No ranked players are currently available.",
                "confidence": 0,
                "details": [],
            }

        (player, team), data = self.ranked_players[0]
        score = self._score(data)
        signals = data.get("signals", [])

        confidence = self.confidence_from_signals(signals)

        if confidence == 0:
            confidence = 60

        return {
            "answer": (
                f"{player} ({team}) currently has the highest "
                f"adjusted score at {score:+.1f}."
            ),
            "confidence": confidence,
            "details": [
                f"Recommendation: "
                f"{self.recommendation_from_score(score)}",
                f"Signals evaluated: {len(data.get('signals', []))}",
            ],
        }

    def _top_recommendation(self, action: str) -> dict:
        for (player, team), data in self.ranked_players:
            score = self._score(data)
            recommendation = self.recommendation_from_score(score)

            if recommendation == action:
                signals = data.get("signals", [])
                confidence = self.confidence_from_signals(signals)

                if confidence == 0:
                    confidence = 60

                return {
                    "answer": (
                        f"{player} ({team}) is the top "
                        f"{action} candidate."
                    ),
                    "confidence": confidence,
                    "details": [
                        f"Adjusted score: {score:+.1f}",
                        f"Signals evaluated: "
                        f"{len(data.get('signals', []))}",
                    ],
                }

        if self.ranked_players:
            (player, team), data = self.ranked_players[0]

            score = self._score(data)
            recommendation = self.recommendation_from_score(score)

            signals = data.get("signals", [])
            confidence = self.confidence_from_signals(signals)

            if confidence == 0:
                confidence = 60

            return {
                "answer": (
                    f"No {action} candidates are currently available. "
                    f"The highest-ranked option is {player} ({team}), "
                    f"currently rated {recommendation}."
                ),
                "confidence": confidence,
                "details": [
                    f"Adjusted score: {score:+.1f}",
                    f"Current recommendation: {recommendation}",
                    f"Signals evaluated: {len(signals)}",
                ],
            }

        return {
            "answer": "No ranked players are currently available.",
            "confidence": 0,
            "details": [],
        }

    def _explain_player(
        self,
        player: str,
        team: str,
        data: dict,
    ) -> dict:
        score = self._score(data)
        recommendation = self.recommendation_from_score(score)
        signals = data.get("signals", [])

        confidence = self.confidence_from_signals(signals)

        if confidence == 0:
            confidence = 60

        details = [
            f"Adjusted score: {score:+.1f}",
            f"Recommendation: {recommendation}",
            f"Signals evaluated: {len(data.get('signals', []))}",
        ]

        propagated = data.get("propagated_impacts", [])

        if propagated:
            details.append(
                f"Propagation impacts: {len(propagated)}"
            )

        return {
            "answer": (
                f"{player} ({team}) is currently rated "
                f"{recommendation} with {confidence}% confidence."
            ),
            "confidence": confidence,
            "details": details,
        }
