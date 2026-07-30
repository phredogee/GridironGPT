from typing import TypedDict


class EventRule(TypedDict):
    category: str
    subtype: str
    polarity: str
    impact: float
    confidence: float
    phrases: list[str]


EVENT_RULES: list[EventRule] = [
    # Injury and recovery
    {
        "category": "injury",
        "subtype": "injured_reserve",
        "polarity": "negative",
        "impact": -1.0,
        "confidence": 0.98,
        "phrases": [
            "placed on injured reserve",
            "placed on ir",
            "headed to injured reserve",
            "lands on injured reserve",
        ],
    },
    {
        "category": "injury",
        "subtype": "activated",
        "polarity": "positive",
        "impact": 1.0,
        "confidence": 0.97,
        "phrases": [
            "activated from injured reserve",
            "activated from ir",
            "activated from pup",
            "removed from pup",
        ],
    },
    {
        "category": "injury",
        "subtype": "designated_to_return",
        "polarity": "positive",
        "impact": 0.70,
        "confidence": 0.96,
        "phrases": [
            "designated to return",
            "designated for return",
            "opened his practice window",
            "opened the practice window",
            "practice window opened",
        ],
    },
    {
        "category": "injury",
        "subtype": "placed_on_pup",
        "polarity": "negative",
        "impact": -0.80,
        "confidence": 0.97,
        "phrases": [
            "placed on the pup list",
            "placed on pup",
            "starts camp on pup",
            "will begin camp on pup",
            "physically unable to perform list",
        ],
    },
    {
        "category": "injury",
        "subtype": "placed_on_nfi",
        "polarity": "negative",
        "impact": -0.75,
        "confidence": 0.97,
        "phrases": [
            "placed on the nfi list",
            "placed on nfi",
            "non-football injury list",
            "non-football illness list",
        ],
    },
    {
        "category": "injury",
        "subtype": "returned_to_practice",
        "polarity": "positive",
        "impact": 0.8,
        "confidence": 0.95,
        "phrases": [
            "returned to practice",
            "returns to practice",
            "back at practice",
            "cleared for practice",
            "cleared for training camp",
        ],
    },
    {
        "category": "injury",
        "subtype": "full_practice",
        "polarity": "positive",
        "impact": 0.60,
        "confidence": 0.94,
        "phrases": [
            "full participant",
            "full practice",
            "practiced in full",
        ],
    },
    {
        "category": "injury",
        "subtype": "limited_practice",
        "polarity": "monitor",
        "impact": -0.40,
        "confidence": 0.90,
        "phrases": [
            "limited participant",
            "limited practice",
            "practiced on a limited basis",
        ],
    },
    {
        "category": "injury",
        "subtype": "did_not_practice",
        "polarity": "negative",
        "impact": -0.65,
        "confidence": 0.94,
        "phrases": [
            "did not practice",
            "didn't practice",
            "held out of practice",
            "did not participate in practice",
            "non-participant in practice",
        ],
    },
    {
        "category": "injury",
        "subtype": "questionable",
        "polarity": "negative",
        "impact": -0.45,
        "confidence": 0.92,
        "phrases": [
            "listed as questionable",
            "questionable for sunday",
            "questionable for monday",
            "questionable for thursday",
            "questionable to play",
        ],
    },
    {
        "category": "injury",
        "subtype": "doubtful",
        "polarity": "negative",
        "impact": -0.80,
        "confidence": 0.95,
        "phrases": [
            "listed as doubtful",
            "doubtful for sunday",
            "doubtful for monday",
            "doubtful for thursday",
            "unlikely to play",
        ],
    },
    {
        "category": "injury",
        "subtype": "ruled_out",
        "polarity": "negative",
        "impact": -1.0,
        "confidence": 0.99,
        "phrases": [
            "ruled out",
            "will not play",
            "won't play",
            "declared out",
            "inactive due to injury",
        ],
    },
    {
        "category": "injury",
        "subtype": "expected_to_play",
        "polarity": "positive",
        "impact": 0.65,
        "confidence": 0.91,
        "phrases": [
            "expected to play",
            "on track to play",
            "likely to play",
            "plans to play",
            "should be available",
        ],
    },
    {
        "category": "injury",
        "subtype": "expected_to_miss",
        "polarity": "negative",
        "impact": -0.90,
        "confidence": 0.94,
        "phrases": [
            "expected to miss",
            "likely to miss",
            "not expected to play",
            "expected to be sidelined",
        ],
    },
    {
        "category": "injury",
        "subtype": "game_time_decision",
        "polarity": "negative",
        "impact": -0.50,
        "confidence": 0.92,
        "phrases": [
            "game-time decision",
            "game time decision",
            "decision will be made before kickoff",
            "status will be determined before the game",
        ],
    },
    {
        "category": "injury",
        "subtype": "injured",
        "polarity": "negative",
        "impact": -0.80,
        "confidence": 0.88,
        "phrases": [
            "suffered an injury",
            "dealing with an injury",
            "left practice with",
            "will undergo surgery",
            "needs surgery",
        ],
    },

    # Depth chart
    {
        "category": "depth_chart",
        "subtype": "starter_named",
        "polarity": "positive",
        "impact": 0.90,
        "confidence": 0.96,
        "phrases": [
            "named the starter",
            "will start",
            "starting quarterback",
            "earned the starting job",
        ],
    },
    {
        "category": "depth_chart",
        "subtype": "first_team_reps",
        "polarity": "positive",
        "impact": 0.70,
        "confidence": 0.93,
        "phrases": [
            "first-team reps",
            "first team reps",
            "working with the starters",
            "running with the first team",
        ],
    },
    {
        "category": "depth_chart",
        "subtype": "promoted",
        "polarity": "positive",
        "impact": 0.60,
        "confidence": 0.90,
        "phrases": [
            "promoted to",
            "moved up the depth chart",
            "elevated to the active roster",
        ],
    },
    {
        "category": "depth_chart",
        "subtype": "demoted",
        "polarity": "negative",
        "impact": -0.70,
        "confidence": 0.90,
        "phrases": [
            "demoted",
            "moved down the depth chart",
            "replaced as starter",
            "lost the starting job",
        ],
    },

    # Transactions
    {
        "category": "transaction",
        "subtype": "traded",
        "polarity": "neutral",
        "impact": 0.0,
        "confidence": 0.98,
        "phrases": [
            "traded to",
            "acquired via trade",
            "trade sends",
        ],
    },
    {
        "category": "transaction",
        "subtype": "contract_extension",
        "polarity": "positive",
        "impact": 0.20,
        "confidence": 0.97,
        "phrases": [
            "contract extension",
            "agreed to an extension",
            "signed an extension",
            "reaches extension",
        ],
    },
    {
        "category": "transaction",
        "subtype": "released",
        "polarity": "negative",
        "confidence": 0.96,
        "phrases": [
            "released by",
            "has been released",
            "cut by",
        ],
    },
    {
        "category": "transaction",
        "subtype": "waived",
        "polarity": "negative",
        "impact": -0.80,
        "confidence": 0.96,
        "phrases": [
            "waived by",
            "has been waived",
            "placed on waivers",
        ],
    },
    {
        "category": "transaction",
        "subtype": "signed",
        "polarity": "positive",
        "impact": 0.30,
        "confidence": 0.92,
        "phrases": [
            "signed with",
            "agreed to terms",
            "signs with",
        ],
    },

    # Availability
    {
        "category": "availability",
        "subtype": "suspended",
        "polarity": "negative",
        "impact": -1.0,
        "confidence": 0.98,
        "phrases": [
            "suspended for",
            "has been suspended",
            "serving a suspension",
        ],
    },
    {
        "category": "availability",
        "subtype": "holdout",
        "polarity": "negative",
        "impact": -0.70,
        "confidence": 0.95,
        "phrases": [
            "holding out",
            "contract holdout",
            "skipping training camp",
        ],
    },
    {
        "category": "availability",
        "subtype": "retired",
        "polarity": "negative",
        "impact": -1.0,
        "confidence": 0.99,
        "phrases": [
            "announced his retirement",
            "announces retirement",
            "has retired",
            "retires from the nfl",
        ],
    },
    {
        "category": "availability",
        "subtype": "absent",
        "polarity": "negative",
        "impact": -0.40,
        "confidence": 0.88,
        "phrases": [
            "absent from practice",
            "missed  practice for personal reasons",
            "excused absense",
            "unexcused absense",
        ],
    },

    # Performance
    {
        "category": "performance",
        "subtype": "coach_praise",
        "polarity": "positive",
        "impact": 0.40,
        "confidence": 0.86,
        "phrases": [
            "coach praised",
            "impressed the coaching staff",
            "having a strong camp",
            "standing out in camp",
        ],
    },
    {
        "category": "performance",
        "subtype": "coach_concern",
        "polarity": "negative",
        "impact": -0.40,
        "confidence": 0.86,
        "phrases": [
            "coach expressed concern",
            "coaching staff concerned",
            "struggling in camp",
        ],
    },
    {
        "category": "performance",
        "subtype": "breakout",
        "polarity": "positive",
        "impact": 0.80,
        "confidence": 0.84,
        "phrases": [
            "breakout performance",
            "career-high",
            "dominant performance",
        ],
    },
    {
        "category": "performance",
        "subtype": "poor_performance",
        "polarity": "negative",
        "impact": -0.60,
        "confidence": 0.84,
        "phrases": [
            "poor performance",
            "struggled badly",
            "benched after",
        ],
    },

]
