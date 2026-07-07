IGNORE_TERMS = [
    "super bowl rings",
    "kelce-swift",
    "world cup",
    "fans",
    "celebrity",
    "celebrities bring style",
    "ceremony",
    "marry",
    "murder",
    "guilty",
    "ice bucket challenge",
    "mother dead",
    "city",
    "history",
    "parole",
]

DRAFT_TERMS = [
    "draft rankings",
    "nfl draft",
    "mock draft",
    "rookie progress",
]

ROSTER_TERMS = [
    "clears waivers",
    "free agent",
    "to sign with",
    "sign with",
    "signs with",
    "released",
    "waived",
    "claimed",
]

FANTASY_TERMS = [
    "best ball",
    "fantasy football",
    "value picks",
    "draft guide",
    "sleepers",
    "waiver wire",
]

TEAM_CONTEXT_TERMS = [
    "qb battles",
    "best nfl offenses",
    "team",
    "personnel",
    "depth chart",
    "trades",
    "playoff run",
    "sean payton",
    "fake punt",
    "rosters",
    "trade fireworks",
    "cap casualties",
]

LEAGUE_CONTEXT_TERMS = [
    "nfl season",
    "fpi projections",
    "100 things to know",
    "league",
    "best cornerbacks",
    "best running backs",
    "execs",
    "coaches and scouts",
    "discipline",
]

def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)

def classify_article_relevance(
    headline: str,
    summary: str = "",
    player: str = "Unknown",
) -> str:
    text = f"{headline} {summary}".lower()

    if player != "Unknown":
        return "player_signal"

    if _contains_any(text, IGNORE_TERMS):
        return "ignore"

    if _contains_any(text, ROSTER_TERMS):
        return "roster_context"

    if _contains_any(text, FANTASY_TERMS):
        return "fantasy_context"

    if _contains_any(text, DRAFT_TERMS):
        return "draft_context"

    if _contains_any(text, TEAM_CONTEXT_TERMS):
        return "team_context"

    if _contains_any(text, LEAGUE_CONTEXT_TERMS):
        return "league_context"

    return "unknown_context"
