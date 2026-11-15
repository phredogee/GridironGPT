"""Integration and UI tests for the explicitly synthetic Phase 04 workflow."""
from io import BytesIO
from pathlib import Path
import time
import pandas as pd
import pytest
from synthetic_slate import synthetic_salary_csv, DEMO_NOW
from slate_import import import_draftkings_classic, SlateValidationError
from lineup_optimizer import prepare_slate, optimize, SLOTS, CAP, fits


def slate():
    data, _ = import_draftkings_classic(synthetic_salary_csv())
    return prepare_slate(data, now=DEMO_NOW)


def test_reproducible_source_and_legal_lineup():
    assert synthetic_salary_csv() == synthetic_salary_csv()
    pool = slate()
    start = time.perf_counter()
    result, err = optimize(pool)
    assert err is None
    assert result.Slot.tolist() == SLOTS
    assert result.Key.nunique() == 9
    assert result.Salary.sum() <= CAP
    assert all(fits(r.Position, r.Slot) for r in result.itertuples())
    print(f'Synthetic solve seconds: {time.perf_counter()-start:.4f}')


def test_locks_and_exclusions():
    pool = slate()
    result, err = optimize(pool, {'QB': 'SYN-QB-01'}, {'SYN-WR-12'})
    assert err is None
    assert result.set_index('Slot').loc['QB', 'Key'] == 'SYN-QB-01'
    assert 'SYN-WR-12' not in set(result.Key)


@pytest.mark.parametrize('case', ['no_qb', 'over_cap', 'conflict', 'wrong_slot', 'started', 'unknown'])
def test_rejects_invalid_lineups(case):
    pool = slate(); fixed = {}; excluded = set()
    if case == 'no_qb': excluded = set(pool.loc[pool.Position == 'QB', 'Key'])
    if case == 'over_cap': pool['Salary'] = 10000
    if case == 'conflict': fixed = {'QB': 'SYN-QB-01'}; excluded = {'SYN-QB-01'}
    if case == 'wrong_slot': fixed = {'QB': 'SYN-RB-01'}
    if case == 'started': pool['Eligible'] = False; pool['Status'] = 'GAME STARTED'
    if case == 'unknown':
        pool['Game'] = 'unknown'; pool = prepare_slate(pool, now=DEMO_NOW)
    result, err = optimize(pool, fixed, excluded)
    assert result is None and err


def test_import_rejects_corrupt_salary_and_duplicate_id():
    raw = pd.read_csv(BytesIO(synthetic_salary_csv()))
    for field, value in [('Salary', -1), ('ID', raw.loc[1, 'ID'])]:
        bad = raw.copy(); bad.loc[0, field] = value
        with pytest.raises(SlateValidationError): import_draftkings_classic(bad.to_csv(index=False).encode())


def test_streamlit_end_to_end_and_approval_reset():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=60).run()
    at.sidebar.radio[0].set_value('Lineup Lab').run()
    assert not at.exception
    assert any('SYNTHETIC TEST DATA' in w.value for w in at.warning)
    next(b for b in at.button if b.label == 'Complete My Lineup').click().run()
    assert not at.exception
    assert len(at.session_state['dk_picks']) == 9
    approval = next(c for c in at.checkbox if c.label.startswith('I reviewed'))
    approval.check().run()
    assert not at.exception
    assert len(at.get('download_button')) == 2
    exported = at.session_state['dk_picks'].copy()
    next(b for b in at.button if b.label == 'Clear roster').click().run()
    assert not at.exception
    assert at.session_state['dk_picks'] == {}
    assert len(at.get('download_button')) == 1
