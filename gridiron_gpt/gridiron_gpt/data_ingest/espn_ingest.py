# gpt/data_ingest/espn_ingest.py

import os
import json
import argparse
import requests
from gridiron_gpt.validators.profile_validator import validate_profile_schema

RAW_DIR = "data/raw/espn"
CLEAN_DIR = "data/clean/espn"

# Home stadium surface and environment for all 32 NFL teams (2025 season).
# surface: "natural grass" | "artificial turf"
# environment: "outdoor" | "indoor" | "retractable roof"
STADIUM_INFO = {
    "ARI": {"surface": "artificial turf",  "environment": "retractable roof"},
    "ATL": {"surface": "artificial turf",  "environment": "indoor"},
    "BAL": {"surface": "natural grass",    "environment": "outdoor"},
    "BUF": {"surface": "natural grass",    "environment": "outdoor"},
    "CAR": {"surface": "natural grass",    "environment": "outdoor"},
    "CHI": {"surface": "natural grass",    "environment": "outdoor"},
    "CIN": {"surface": "artificial turf",  "environment": "outdoor"},
    "CLE": {"surface": "natural grass",    "environment": "outdoor"},
    "DAL": {"surface": "artificial turf",  "environment": "retractable roof"},
    "DEN": {"surface": "natural grass",    "environment": "outdoor"},
    "DET": {"surface": "artificial turf",  "environment": "indoor"},
    "GB":  {"surface": "natural grass",    "environment": "outdoor"},
    "HOU": {"surface": "artificial turf",  "environment": "retractable roof"},
    "IND": {"surface": "artificial turf",  "environment": "retractable roof"},
    "JAX": {"surface": "natural grass",    "environment": "outdoor"},
    "KC":  {"surface": "natural grass",    "environment": "outdoor"},
    "LAC": {"surface": "natural grass",    "environment": "outdoor"},
    "LAR": {"surface": "natural grass",    "environment": "outdoor"},
    "LV":  {"surface": "artificial turf",  "environment": "indoor"},
    "MIA": {"surface": "natural grass",    "environment": "outdoor"},
    "MIN": {"surface": "artificial turf",  "environment": "indoor"},
    "NE":  {"surface": "artificial turf",  "environment": "outdoor"},
    "NO":  {"surface": "artificial turf",  "environment": "indoor"},
    "NYG": {"surface": "artificial turf",  "environment": "outdoor"},
    "NYJ": {"surface": "artificial turf",  "environment": "outdoor"},
    "PHI": {"surface": "natural grass",    "environment": "outdoor"},
    "PIT": {"surface": "natural grass",    "environment": "outdoor"},
    "SEA": {"surface": "artificial turf",  "environment": "outdoor"},
    "SF":  {"surface": "natural grass",    "environment": "outdoor"},
    "TB":  {"surface": "natural grass",    "environment": "outdoor"},
    "TEN": {"surface": "natural grass",    "environment": "outdoor"},
    "WAS": {"surface": "natural grass",    "environment": "outdoor"},
}


def fetch_espn_data(week: int) -> list:
    """Fetch raw ESPN scoreboard data for a given NFL week."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={week}&seasontype=2"
    print(f"📡 Fetching ESPN data for week {week}...")
    response = requests.get(url)
    data = response.json()

    players = []
    for event in data.get("events", []):
        competition = event["competitions"][0]

        # Identify home team to determine stadium surface/environment
        home_abbr = next(
            (c["team"]["abbreviation"] for c in competition["competitors"]
             if c.get("homeAway") == "home"),
            None
        )
        stadium = STADIUM_INFO.get(home_abbr, {})
        surface = stadium.get("surface", "unknown surface")
        environment = stadium.get("environment", "outdoor")

        # ESPN venue object may override indoor flag
        if competition.get("venue", {}).get("indoor") and environment == "outdoor":
            environment = "indoor"

        for competitor in competition["competitors"]:
            team = competitor["team"]["abbreviation"]
            for athlete in competitor.get("athletes", []):
                players.append({
                    "player_name": athlete["displayName"],
                    "team": team,
                    "week": week,
                    "fantasy_points": athlete.get("stats", [{}])[0].get("value", 0),
                    "position": athlete.get("position", {}).get("abbreviation", "UNK"),
                    "surface": surface,
                    "environment": environment,
                })
    return players


def clean_espn_data(raw_data: list) -> list:
    """Transform raw ESPN data into validated profile format."""
    print("🧼 Cleaning ESPN data...")
    cleaned = []
    for entry in raw_data:
        cleaned.append({
            "profile_id": f"{entry['team']}_{entry['player_name'].replace(' ', '_')}",
            "player_name": entry["player_name"],
            "team": entry["team"],
            "week": entry["week"],
            "fantasy_points": float(entry["fantasy_points"]),
            "position": entry.get("position", "unknown"),
            "surface": entry.get("surface", "unknown surface"),
            "environment": entry.get("environment", "outdoor"),
        })
    print(f"✅ Cleaned {len(cleaned)} player entries")
    return cleaned

def save_cleaned_data(cleaned_data: list, week: int, output_path: str = None):
    """Save cleaned data to disk."""
    os.makedirs(CLEAN_DIR, exist_ok=True)
    path = output_path or os.path.join(CLEAN_DIR, f"week_{week}.json")
    with open(path, "w") as f:
        json.dump(cleaned_data, f, indent=2)
    print(f"💾 Saved cleaned data to {path}")

def banner_feedback(valid: bool, issues: list):
    """Display validation results with expressive feedback."""
    if valid:
        print("✅ ESPN data validated successfully! 🎉")
    else:
        print("🚨 Validation failed:")
        for issue in issues:
            print(f"   ❌ {issue}")

def main():
    parser = argparse.ArgumentParser(description="ESPN NFL Data Ingest Pipeline")
    parser.add_argument("--week", type=int, required=True, help="NFL week number")
    parser.add_argument("--dry-run", action="store_true", help="Preview cleaned data without saving")
    parser.add_argument("--banner", action="store_true", help="Show validation feedback banner")
    parser.add_argument("--output-path", type=str, help="Custom output path for cleaned data")
    args = parser.parse_args()

    raw_data = fetch_espn_data(args.week)
    cleaned_data = clean_espn_data(raw_data)
    valid, issues = validate_profile_schema(cleaned_data)

    if args.banner:
        banner_feedback(valid, issues)

    if args.dry_run:
        print("🧪 Dry-run mode: cleaned data preview")
        print(json.dumps(cleaned_data, indent=2))
    elif valid:
        save_cleaned_data(cleaned_data, args.week, args.output_path)
    else:
        print("⚠️ Data invalid—skipping save")

if __name__ == "__main__":
    main()
