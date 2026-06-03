# validators/profile_validator.py

from gridiron_gpt.feedback import error

REQUIRED_FIELDS = ["profile_id", "team", "week", "fantasy_points"]

def validate_profile(profile):
    required_keys = ["source", "season", "league_id", "auth_token"]
    missing = [k for k in required_keys if k not in profile]
    if missing:
        error(f"Missing keys: {missing}")
        return None
    return profile

def validate_profile_schema(data):
    issues = []
    for i, entry in enumerate(data):
        missing = [field for field in REQUIRED_FIELDS if field not in entry]
        if missing:
            issues.append(f"Entry {i} missing fields: {', '.join(missing)}")
        elif not isinstance(entry["fantasy_points"], (int, float)):
            issues.append(f"Entry {i} has invalid fantasy_points type: {type(entry['fantasy_points'])}")

    valid = len(issues) == 0
    return valid, issues

