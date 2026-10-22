"""Validate user-provided DraftKings NFL Classic salary CSVs. No network calls."""
from io import BytesIO
import pandas as pd

class SlateValidationError(ValueError):
    pass


def import_draftkings_classic(upload):
    try:
        raw = pd.read_csv(BytesIO(upload), encoding='utf-8-sig', dtype=str, on_bad_lines='error')
    except Exception as exc:
        raise SlateValidationError(f'Unable to read CSV: {exc}') from exc
    raw.columns = raw.columns.str.strip()
    needed = {'Position', 'Salary', 'TeamAbbrev'}
    missing = needed - set(raw.columns)
    if missing:
        raise SlateValidationError(f'Missing DraftKings columns: {", ".join(sorted(missing))}. Upload the original NFL Classic salary export.')
    name_field = next((c for c in ['Name', 'Name + ID'] if c in raw.columns), None)
    if name_field is None:
        raise SlateValidationError('Missing player Name or Name + ID column.')
    if raw.empty:
        raise SlateValidationError('The salary file has no rows.')
    df = raw.copy()
    if name_field == 'Name + ID':
        df['Player'] = df[name_field].fillna('').str.replace(r'\s*\(\d+\)\s*$', '', regex=True).str.strip()
    else:
        df['Player'] = df[name_field].fillna('').str.strip()
    df['Position'] = df['Position'].fillna('').str.upper().str.strip()
    df['Team'] = df['TeamAbbrev'].fillna('').str.strip().str.upper()
    df['Salary'] = pd.to_numeric(df['Salary'].str.replace(r'[$,]', '', regex=True), errors='coerce')
    if df['Salary'].isna().any() or (df['Salary'] <= 0).any():
        raise SlateValidationError('Salary must be a positive number for every row.')
    if (df['Player'] == '').any() or (df['Team'] == '').any():
        raise SlateValidationError('Some rows are missing player or team names.')
    supported = {'QB', 'RB', 'WR', 'TE', 'DST', 'D/ST'}
    unexpected = sorted(set(df['Position']) - supported)
    if unexpected:
        raise SlateValidationError(f'Unexpected positions {unexpected}. This importer supports NFL Classic, not Showdown.')
    df['Position'] = df['Position'].replace({'D/ST': 'DST'})
    if 'ID' in df.columns:
        df['Slate ID'] = df['ID'].fillna('').str.strip()
    else:
        df['Slate ID'] = ''
    if 'Game Info' in df.columns:
        df['Game'] = df['Game Info'].fillna('').str.strip()
    else:
        df['Game'] = ''
    if 'AvgPointsPerGame' in df.columns:
        df['DK Avg Pts'] = pd.to_numeric(df['AvgPointsPerGame'], errors='coerce')
    else:
        df['DK Avg Pts'] = float('nan')
    if df['Slate ID'].ne('').any():
        duplicate_count = int(df.loc[df['Slate ID'].ne(''), 'Slate ID'].duplicated().sum())
        if duplicate_count:
            raise SlateValidationError(f'{duplicate_count} duplicate player IDs found.')
    output = df[['Player', 'Position', 'Team', 'Salary', 'Game', 'Slate ID', 'DK Avg Pts']].copy()
    return output, {'rows': len(output), 'teams': output['Team'].nunique(), 'dst': int((output['Position']=='DST').sum())}
