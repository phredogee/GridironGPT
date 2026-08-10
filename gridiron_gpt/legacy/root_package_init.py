# gridiron_gpt/__init__.py

__version__ = "0.1.0"

from .advisor import FantasyAdvisor
# from phred.slack_bot import SlackBot
# from .pipeline import SemanticPipeline
# from .core import hello

# gridiron_gpt/__init__.py

def align_embeddings(players, bios):
    """
    Merge player data with bios and embeddings.
    Returns a dict keyed by player name.
    """
    merged = {}
    for p in players:
        pid = p.get("playerId")
        bio_entry = next((b for b in bios if b.get("playerId") == pid), {})
        merged[p.get("name", f"Unknown-{pid}")] = {
            "playerId": pid,  # keep this for traceability
        "bio": {
            "bio": bio_entry.get("bio", f"Bio for {p.get('name', 'Unnamed')}"),
            "position": bio_entry.get("position", p.get("position", "Unknown Position")),
            "team": bio_entry.get("team", p.get("team", "Unknown Team"))
    },
    "embedding": {"embedding": f"vector-for-{pid}"},
    "position_match": p.get("position") == bio_entry.get("position")
}
    return merged
