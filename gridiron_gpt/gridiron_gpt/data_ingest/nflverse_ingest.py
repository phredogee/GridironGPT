# /data_ingest/nflverse_ingest.py

import os
import json
import argparse
from nfl_data_py import import_weekly_data
from validators.profile_validator import validate_profile_schema

RAW_DIR = "data/raw/nflverse"
CLEAN_DIR = "data/clean/nflverse"

def fetch_nflverse_data(season):
    print(f"📡 Fetching nflverse weekly data for season {season}...")
    df = import_weekly_data([season])
    return df.to_dict(orient="records")

def clean_nflverse_data(raw_data):
    print("🧼 Cleaning nflverse data...")
    cleaned = []
    for entry in raw_data:
        if entry.get("player_name") and entry.get("team"):
            cleaned.append({
                "profile_id": f"{entry['team']}_{entry['player_name'].replace(' ', '_')}",
                "team": entry["team"],
                "week": entry["week"],
                "fantasy_points": float(entry.get("fantasy_points", 0)),
                "position": entry.get("position", "unknown")
            })
    return cleaned
    
def save_cleaned_data(cleaned_data, season):
    os.makedirs(CLEAN_DIR, exist_ok=True)
    path = os.path.join(CLEAN_DIR, f"season_{season}.json")
    with open(path, "w") as f:
        json.dump(cleaned_data, f, indent=2)
    print(f"💾 Saved cleaned data to {path}")

def banner_feedback(valid, issues):
    if valid:
        print("✅ nflverse data validated successfully! 🎉")
    else:
        print("🚨 Validation failed:")
        for issue in issues:
            print(f"   ❌ {issue}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--banner", action="store_true")
    args = parser.parse_args()

    raw_data = fetch_nflverse_data(args.season)
    cleaned_data = clean_nflverse_data(raw_data)

    valid, issues = validate_profile_schema(cleaned_data)

    if args.banner:
        banner_feedback(valid, issues)

    if not args.dry_run and valid:
        save_cleaned_data(cleaned_data, args.season)
    elif args.dry_run:
        print("🧪 Dry-run mode: cleaned data preview")
        print(json.dumps(cleaned_data[:5], indent=2))  # Preview first 5 entries

if __name__ == "__main__":
    main()
