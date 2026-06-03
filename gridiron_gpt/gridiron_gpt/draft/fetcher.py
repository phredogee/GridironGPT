# gridiron_gpt/draft/fetcher.py

import requests
from typing import Dict

_FFC_URL = "https://fantasyfootballcalculator.com/api/v1/adp/{scoring}?teams={teams}&year={year}"
_ESPN_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"

# Current NFL season year — update each year
_CURRENT_YEAR = 2026
_FALLBACK_YEAR = 2024  # last year with confirmed ADP data

INJURY_PENALTIES = {
    "IR": -30.0,
    "Out": -20.0,
    "Doubtful": -10.0,
    "Questionable": -5.0,
    "Probable": -1.0,
}


def _fetch_adp_for_year(scoring: str, teams: int, year: int) -> list:
    ffc_scoring = "ppr" if scoring == "ppr" else ("half-ppr" if scoring == "half_ppr" else "standard")
    url = _FFC_URL.format(scoring=ffc_scoring, teams=teams, year=year)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("players", [])


def fetch_adp(scoring: str = "ppr", teams: int = 12) -> Dict[str, dict]:
    """
    Fetch ADP from Fantasy Football Calculator.
    Tries the current pre-season year first; falls back to the previous year
    if the current year has no data yet (published ~July/August each year).
    Returns {player_name: {...}}.
    """
    players = []
    year_used = None

    for year in (_CURRENT_YEAR, _FALLBACK_YEAR):
        try:
            players = _fetch_adp_for_year(scoring, teams, year)
            if players:
                year_used = year
                break
        except Exception as e:
            print(f"⚠️ ADP fetch failed for {year}: {e}")

    if not players:
        print("⚠️ No ADP data available — rankings will use historical stats only.")
        return {}

    if year_used != _CURRENT_YEAR:
        print(f"ℹ️  Using {year_used} ADP (current year not yet published).")

    return {
        p["name"]: {
            "adp": float(p.get("adp", 9999)),
            "position": p.get("position", "UNK"),
            "team": p.get("team", "UNK"),
            "bye": p.get("bye"),
            "stdev": float(p.get("stdev", 0)),
            "times_drafted": int(p.get("times_drafted", 0)),
        }
        for p in players
        if p.get("name")
    }


def fetch_injuries() -> Dict[str, str]:
    """Fetch current ESPN injury reports. Returns {player_name: status_string}."""
    try:
        resp = requests.get(_ESPN_INJURIES_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        injuries = {}
        for team_entry in data.get("injuries", []):
            for inj in team_entry.get("injuries", []):
                name = inj.get("athlete", {}).get("displayName", "")
                status = inj.get("status", "")
                if name:
                    injuries[name] = status
        return injuries
    except Exception as e:
        print(f"⚠️ Injury data unavailable ({e}), continuing without it.")
        return {}
