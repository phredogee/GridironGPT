"""DraftKings Classic illustrative lineup solver; no network or contest submission."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

SLOTS = ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 'TE', 'FLEX', 'DST']
CAP = 50000
ET = ZoneInfo('America/New_York')
GAME_RE = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s*(AM|PM)\s*(ET|EST|EDT)?', re.I)


def kickoff_utc(value):
    """Parse DK 'Game Info' ET kickoff; unknown dates are ineligible."""
    m = GAME_RE.search(str(value))
    if not m:
        return pd.NaT
    try:
        dt = datetime.strptime(f'{m.group(1)} {m.group(2)} {m.group(3).upper()}', '%m/%d/%Y %I:%M %p')
        return pd.Timestamp(dt.replace(tzinfo=ET)).tz_convert('UTC')
    except (ValueError, OverflowError):
        return pd.NaT


def prepare_slate(slate, now=None):
    now = pd.Timestamp.now(tz='UTC') if now is None else pd.Timestamp(now)
    now = now.tz_localize('UTC') if now.tzinfo is None else now.tz_convert('UTC')
    out = slate.copy().reset_index(drop=True)
    out['Key'] = [str(v).strip() if str(v).strip() else f'row_{i}' for i,v in enumerate(out['Slate ID'].fillna(''))]
    out['Kickoff UTC'] = out['Game'].map(kickoff_utc)
    out['Status'] = out['Kickoff UTC'].map(lambda x: 'UNKNOWN KICKOFF' if pd.isna(x) else ('GAME STARTED' if x <= now else ('STARTING SOON' if x - now <= pd.Timedelta(minutes=30) else 'UPCOMING')))
    out['Eligible'] = out['Status'].isin(['UPCOMING','STARTING SOON'])
    # DK average is a demo-only proxy, never a pregame model projection.
    out['Demo Points'] = pd.to_numeric(out['Optimization Points'], errors='coerce') if 'Optimization Points' in out.columns else pd.to_numeric(out['DK Avg Pts'], errors='coerce')
    out['Value'] = out['Demo Points'] / (out['Salary'] / 1000)
    return out


def fits(position, slot):
    return position == slot.rstrip('123') or (slot == 'FLEX' and position in ('RB','WR','TE'))


def optimize(slate, fixed=None, excluded=None, score_col='Demo Points', candidate=None):
    """Maximize total points with binary player-to-slot assignment, locks and cap.

    fixed: mapping {slot: player Key}. Excluded/started/unknown games are forbidden.
    Returns (lineup_df, error_message). Does not alter inputs.
    """
    fixed = dict(fixed or {})
    excluded = set(excluded or ())
    if candidate is not None:
        # Candidate is required in *some* legal open slot; no duplicate assignments.
        if candidate in excluded or candidate in fixed.values():
            return None, 'Candidate unavailable or already selected.'
    if len(set(fixed.values())) != len(fixed):
        return None, 'A player is assigned to multiple slots.'
    if any(slot not in SLOTS for slot in fixed):
        return None, 'Unknown roster slot.'
    if not fixed and candidate is None and slate.empty:
        return None, 'Slate is empty.'
    bykey = slate.set_index('Key', drop=False)
    for slot,key in fixed.items():
        if key not in bykey.index:
            return None, f'Selected player missing from slate: {key}'
        row = bykey.loc[key]
        if not bool(row['Eligible']):
            return None, f'{row["Player"]} is not eligible: {row["Status"]}.'
        if not fits(row['Position'],slot):
            return None, f'{row["Player"]} cannot fill {slot}.'
        if key in excluded:
            return None, f'{row["Player"]} is excluded.'
    if candidate is not None and (candidate not in bykey.index or not bool(bykey.loc[candidate,'Eligible'])):
        return None, 'Candidate is not eligible.'
    pool = slate.loc[slate['Eligible'] & slate[score_col].notna() & ~slate['Key'].isin(excluded)].copy()
    # Limit combinatorial size without dropping already-selected players.
    keep = set(fixed.values()) | ({candidate} if candidate else set())
    if len(pool) > 300:
        ranked = pool.sort_values(score_col, ascending=False)
        indices = set(ranked.groupby('Position', group_keys=False).head(65)['Key']) | keep
        pool = pool.loc[pool['Key'].isin(indices)]
    if len(pool) < 9:
        return None, 'Not enough eligible players with numeric point estimates to fill nine slots.'
    records = [(i,slot) for i,row in pool.iterrows() for slot in SLOTS if fits(row['Position'],slot)]
    if not records:
        return None, 'No compatible player/slot combinations.'
    # Explicit constraints: one per slot; at most one slot per player; cap; fixed picks; candidate.
    keys = list(pool.index)
    n = len(records)
    rowcount = len(SLOTS) + len(keys) + 1 + len(fixed) + (1 if candidate else 0)
    A = lil_matrix((rowcount,n), dtype=float)
    lb = np.zeros(rowcount)
    ub = np.ones(rowcount)
    ub[len(SLOTS):len(SLOTS)+len(keys)] = 1
    lb[:len(SLOTS)] = 1
    lb[len(SLOTS)+len(keys)] = 0
    ub[len(SLOTS)+len(keys)] = CAP
    pos = {idx:j for j,idx in enumerate(keys)}
    for j,(idx,slot) in enumerate(records):
        A[SLOTS.index(slot),j] = 1
        A[len(SLOTS)+pos[idx],j] = 1
        A[len(SLOTS)+len(keys),j] = float(pool.loc[idx,'Salary'])
    rowptr = len(SLOTS)+len(keys)+1
    for slot,key in fixed.items():
        for j,(idx,s) in enumerate(records):
            if s == slot and pool.loc[idx,'Key'] == key:
                A[rowptr,j] = 1
        lb[rowptr] = ub[rowptr] = 1
        rowptr += 1
    if candidate:
        for j,(idx,s) in enumerate(records):
            if pool.loc[idx,'Key'] == candidate:
                A[rowptr,j] = 1
        lb[rowptr] = ub[rowptr] = 1
    points = np.array([float(pool.loc[idx,score_col]) for idx,_ in records])
    result = milp(c=-points, integrality=np.ones(n), bounds=Bounds(np.zeros(n),np.ones(n)), constraints=LinearConstraint(A.tocsr(),lb,ub), options={'time_limit':12, 'mip_rel_gap':0.01})
    if result.x is None or result.status not in (0,1):
        return None, 'No feasible lineup within the salary cap and roster constraints.'
    if result.status == 1:
        return None, 'Optimizer time limit reached without confirmed optimality; please reduce slate size.'
    picked = []
    for j,(idx,slot) in enumerate(records):
        if result.x[j] > 0.5:
            picked.append({'Slot':slot, **pool.loc[idx, ['Key','Player','Position','Team','Salary',score_col,'Status']].to_dict()})
    answer = pd.DataFrame(picked)
    if len(answer) != 9 or answer['Key'].nunique() != 9 or answer['Salary'].sum() > CAP:
        return None, 'Internal lineup validation failed.'
    return answer.set_index('Slot').loc[SLOTS].reset_index(), None


def suggestions(slate, fixed, excluded, mode='Best Roster Fit', top_n=3):
    """Only suggest candidates that permit a complete feasible lineup."""
    used = set(fixed.values()) | set(excluded)
    open_slots = [s for s in SLOTS if s not in fixed]
    positions = [p for p in ['QB','RB','WR','TE','FLEX','DST'] if any(fits(p,s) if p != 'FLEX' else s == 'FLEX' for s in open_slots)]
    pool = slate.loc[slate['Eligible'] & slate['Demo Points'].notna() & ~slate['Key'].isin(used)].copy()
    if mode == 'Best Value':
        pool = pool.sort_values('Value',ascending=False)
    else:
        pool = pool.sort_values('Demo Points',ascending=False)
    rows=[]
    for pos in positions:
        subset = pool.loc[pool['Position'].isin(['RB','WR','TE'])] if pos == 'FLEX' else pool.loc[pool['Position']==pos]
        # Explore candidates and ensure every suggestion permits a legal completion.
        found=0
        for _,row in subset.iterrows():
            if found >= top_n: break
            if not any(fits(row['Position'],s) for s in open_slots): continue
            complete,err=optimize(slate,fixed,excluded,candidate=row['Key'])
            if err: continue
            rows.append({'Position':pos,'Player':row['Player'],'Salary':row['Salary'],'Demo Points':row['Demo Points'],'Value':row['Value'],'Key':row['Key']})
            found += 1
    return pd.DataFrame(rows)
