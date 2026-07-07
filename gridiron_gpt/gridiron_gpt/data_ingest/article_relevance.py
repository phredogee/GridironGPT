def classify_article_relevance(
    headline: str,
    summary: str = "",
    player: str = "Unknown",
) -> str:
    text = f"{headline} {summary}".lower()

    if player != "Unknown":
        return "player_signal"

    ignore_terms = [
        "super bowl rings",
        "kelce-swift",
        "world cup",
        "fans",
        "celebrity",
        "ceremony",
        "marry",
        "murder",
        "guilty",
        "ice bucket challenge",
        "mother dead",
        "city",
        "celebrities bring style",
        "history",
        "parole",
    ]

    draft_terms = [
        "draft rankings",
        "nfl draft",
        "mock draft",
        "rookie progress",
    ]

    roster_terms = [
        "clears waivers",
        "free agent",
        "to sign with",
        "sign with",
        "signs with",
        "released",
        "waived",
        "claimed",
    ]

    fantasy_terms = [
        "best ball",
        "fantasy football",
        "value picks",
        "draft guide",
        "sleepers",
        "waiver wire",
    ]
    if any(term in text for term in roster_terms):
        return "roster_context"

    if any(term in text for term in fantasy_terms):
        return "fantasy_context"

    team_context_terms = [
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

    league_context_terms = [
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

    if any(term in text for term in ignore_terms):
        return "ignore"

    if any(term in text for term in draft_terms):
        return "draft_context"

    if any(term in text for term in team_context_terms):
        return "team_context"

    if any(term in text for term in league_context_terms):
        return "league_context"

    return "unknown_context"
