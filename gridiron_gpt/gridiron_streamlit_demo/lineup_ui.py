"""Streamlit DraftKings Classic demo lineup builder."""
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from lineup_optimizer import CAP, SLOTS, prepare_slate, optimize, suggestions, fits, kickoff_utc
from model_slate import match_historical_slate
from dk_scoring import dst_demo_estimate, score_observed_offense


def render_lineup_lab(platform, importer, validation_error, data_path=None, model_path=None):
    st.subheader('Lineup Lab · DraftKings Classic')
    with st.expander('DraftKings scoring rules and DST methodology (Version 7)'):
        st.write('DraftKings Classic awards 1.00 point per reception, 0.04 per passing yard, 4.00 per passing TD, 0.10 per rushing/receiving yard, and 6.00 per rushing/receiving TD. It also includes 3.00-point bonuses at 300 passing yards and 100 rushing or receiving yards, plus turnover penalties.')
        st.warning('A PPR prediction alone cannot identify bonus probabilities or predict fumbles lost. Version 7 adds a verified scoring calculator for observed stats; it does NOT convert our PPR model into a validated DK forecast.')
        st.caption('DST in historical replay remains a labeled, bounded uploaded-average baseline (0.00–20.00), not a trained DST model. Live DK scoring projections remain future work.')
        st.markdown('**Historical scoring calculator (observed stats only)**')
        fields = [('passing_yards','Passing yards'),('passing_tds','Passing TDs'),('passing_interceptions','Interceptions'),
                  ('rushing_yards','Rushing yards'),('rushing_tds','Rushing TDs'),('receiving_yards','Receiving yards'),
                  ('receiving_tds','Receiving TDs'),('receptions','Receptions'),('fumbles_lost','Fumbles lost')]
        stat_cols = st.columns(3)
        entered = {}
        for i,(field,label) in enumerate(fields):
            entered[field] = stat_cols[i%3].number_input(label,min_value=0.0,value=0.0,step=1.0,key=f'v7_{field}')
        observed,missing = score_observed_offense(entered)
        if not missing:
            st.metric('Observed DraftKings offensive points',f'{observed:.2f}')
            st.caption('For explaining scoring on completed games; not a prediction and not sent to the optimizer.')
    st.caption('Demo lineup optimization and historical ML projection matching. No live contest predictions.')
    if platform != 'DraftKings':
        st.info('FanDuel support is planned. Select DraftKings in the sidebar.')
        return
    uploaded = st.file_uploader('Upload DraftKings NFL Classic salary CSV',type=['csv'],key='dk_csv')
    if uploaded is not None:
        try:
            slate,_ = importer(uploaded.getvalue())
            st.session_state['dk_slate'] = slate
            st.session_state['dk_slate_filename'] = uploaded.name
            if st.session_state.get('dk_upload_signature') != (uploaded.name, len(uploaded.getvalue()), hash(uploaded.getvalue())):
                st.session_state['dk_picks'] = {}
                st.session_state['dk_excluded'] = []
                st.session_state['dk_upload_signature'] = (uploaded.name, len(uploaded.getvalue()), hash(uploaded.getvalue()))
        except validation_error as exc:
            st.session_state.pop('dk_slate',None)
            st.error(str(exc))
    if 'dk_slate' not in st.session_state:
        st.info('Upload a DraftKings salary CSV to start building a lineup.')
        return
    st.markdown('#### Projection source')
    source = st.radio('Lineup scoring', ['Uploaded DK average (demo)', 'Historical locked-model PPR (retrospective)'],
                      horizontal=True, key='v5_source')
    base = st.session_state['dk_slate'].copy()
    # Only the uploaded-average demonstration can use a simulated clock.
    demo_clock = None
    if not source.startswith('Historical'):
        st.markdown('#### Slate clock · Version 8')
        demo_clock = st.radio(
            'Kickoff eligibility mode',
            ['Demo simulation (sample slates)', 'Live clock (actual kickoff lockout)'],
            horizontal=True, key='v8_clock_mode',
        )
        if demo_clock.startswith('Demo'):
            st.info('SIMULATED DEMO ONLY: eligibility is evaluated one minute before the earliest '
                    'valid kickoff in the uploaded CSV. This does not alter the CSV, predict live '
                    'contests, or permit a real-money lineup submission.')
        else:
            st.warning('LIVE CLOCK: the current system time is used. Verify uploaded kickoff '
                       'timestamps against the official contest. This app does not submit lineups.')
    if source.startswith('Historical'):
        st.warning('Historical research only: model predicts season-long PPR, NOT DraftKings scoring. '
                   'Select the historical season/week corresponding to the uploaded slate. '
                   'No live-week inference or automatic scoring conversion is performed.')
        c1,c2=st.columns(2)
        season=c1.selectbox('Historical season', list(range(2025, 2019, -1)), key='v5_season')
        week=c2.selectbox('Historical NFL week', list(range(1,19)), key='v5_week')
        if not data_path or not model_path:
            st.error('Historical data/model paths are not configured.')
            return
        try:
            base, audit = match_historical_slate(base, data_path, model_path, season, week)
        except Exception as exc:
            st.error(f'Model projection matching failed: {exc}')
            return
        st.info(f"Matched {audit['matched']} of {audit['total']} slate rows by player name + team + position. "
                f"{audit['unmatched']} unmatched (including DST). Unmatched players cannot be optimized in model mode.")
        with st.expander('Model matching audit'):
            st.dataframe(base[['Player','Position','Team','Model PPR']].style.format({'Model PPR':'{:.2f}'},na_rep='—'),hide_index=True)
            st.dataframe(pd.DataFrame(audit['events']),hide_index=True)
        base['Optimization Points'] = base['Model PPR']
    else:
        base['Optimization Points'] = base['DK Avg Pts']
    source_sig=(source, demo_clock, st.session_state.get('v5_season'), st.session_state.get('v5_week'))
    if st.session_state.get('v5_last_source_sig') != source_sig:
        st.session_state['dk_picks']={}
        st.session_state['dk_excluded']=[]
        st.session_state.pop('exclude_select',None)
        for slot in SLOTS: st.session_state.pop(f'roster_slot_{slot}',None)
        st.session_state['v5_last_source_sig']=source_sig
    if source.startswith('Historical'):
        st.warning('RETROSPECTIVE REPLAY ONLY — this is a PPR-proxy research demonstration, NOT a DraftKings-scored forecast. '
                   'DST uses uploaded DK average points as an explicitly disclosed fallback. '
                   'Unmatched offensive players cannot be selected. Historical kickoff times are used only for replay.')
        replay = st.checkbox('Enable historical replay lineup simulation (not for live contests)', value=False, key='v6_replay')
        if not replay:
            st.info('Review matching results above, then enable historical replay to try the optimizer.')
            return
        kickoffs = [kickoff_utc(g) for g in base['Game']]
        known = [k for k in kickoffs if pd.notna(k)]
        if not known:
            st.error('Historical replay requires valid kickoff timestamps in the uploaded salary CSV.')
            return
        replay_now = min(known) - pd.Timedelta(minutes=1)
        # Replays should not use the current system clock, which would lock every historical player.
        slate = prepare_slate(base, now=replay_now)
        st.info(f'Historical replay clock: {replay_now.tz_convert("America/New_York"):%b %d, %Y %I:%M %p %Z}. '
                'Replay mode is never valid for submitting a live lineup.')
    else:
        if demo_clock and demo_clock.startswith('Demo'):
            known = [kickoff_utc(g) for g in base['Game']]
            known = [k for k in known if pd.notna(k)]
            if not known:
                st.error('Demo simulation requires at least one valid kickoff timestamp. '
                         'Unknown kickoffs remain blocked.')
                return
            demo_now = min(known) - pd.Timedelta(minutes=1)
            slate = prepare_slate(base, now=demo_now)
            st.caption(f'Simulated eligibility clock: {demo_now.tz_convert("America/New_York"):%b %d, %Y %I:%M %p %Z}. '
                       'Actual kickoff dates are unchanged; this lineup is for demonstration only.')
        else:
            slate = prepare_slate(base)
    score_label = 'Historical PPR proxy' if source.startswith('Historical') else 'Uploaded DK average proxy'
    st.caption('**Projection source:** ' + ('Locked Random Forest · historical PPR (offense); uploaded-average DST fallback'
             if source.startswith('Historical') else 'Uploaded DraftKings AvgPointsPerGame · demo proxy, not an ML forecast'))
    if source.startswith('Historical'):
        # Explicit fallback for DST only; offensive rows MUST be model matched.
        slate.loc[slate['Position']=='DST','Demo Points'] = slate.loc[slate['Position']=='DST','DK Avg Pts'].map(dst_demo_estimate)
        slate['Value'] = slate['Demo Points'] / (slate['Salary'] / 1000)
        slate.loc[slate['Demo Points'].isna(),'Eligible'] = False
        slate.loc[slate['Demo Points'].isna(),'Status'] = 'NO MODEL MATCH'
        st.caption('DST points = bounded uploaded DK historical average (demo-only fallback); QB/RB/WR/TE = locked-model historical PPR predictions. Mixed scoring: research only.')
    picks = dict(st.session_state.get('dk_picks',{}))
    excluded = set(st.session_state.get('dk_excluded',[]))
    now_local = datetime.now().astimezone()
    if not source.startswith('Historical') and demo_clock and demo_clock.startswith('Live'):
        st.caption(f'System time: {now_local:%b %d, %Y %I:%M:%S %p %Z} · Game times interpreted in America/New_York · Refresh page to update eligibility.')
    if st.button('Refresh game eligibility',key='refresh_kickoffs'):
        st.rerun()
    if not source.startswith('Historical') and demo_clock and demo_clock.startswith('Live'):
        st.warning('Kickoff times come from the CSV and must be verified against the official slate. Unknown or already-started games are blocked. This is a new-lineup builder, not a late-swap tool.')
    counts = slate['Status'].value_counts()
    a,b,c,d=st.columns(4)
    a.metric('Players',len(slate))
    b.metric('Available',int(slate['Eligible'].sum()))
    c.metric('Game started',int(counts.get('GAME STARTED',0)))
    d.metric('Unknown kickoff',int(counts.get('UNKNOWN KICKOFF',0)))
    if picks:
        invalid = [(slot,key) for slot,key in picks.items() if key not in set(slate['Key']) or not bool(slate.set_index('Key').loc[key,'Eligible'])]
        if invalid:
            for slot,key in invalid: picks.pop(slot,None)
            st.session_state['dk_picks'] = picks
            st.error('Previously selected players whose games started or whose kickoff is unknown were removed. This builder does not support late swaps.')
    score = 'Demo Points'
    left,right=st.columns([1.1,1.5])
    with left:
        st.markdown('### Your roster')
        index=slate.set_index('Key')
        for slot in SLOTS:
            options=['']+[str(row['Key']) for _,row in slate.iterrows() if row['Eligible'] and fits(row['Position'],slot) and row['Key'] not in excluded and (row['Key'] not in picks.values() or picks.get(slot)==row['Key'])]
            current=picks.get(slot,'')
            if current not in options: current=''
            labels={key:f"{index.loc[key,'Player']} · ${index.loc[key,'Salary']:,.0f} · {index.loc[key,'Demo Points']:.2f} pts" for key in options if key and pd.notna(index.loc[key,'Demo Points'])}
            widget_key=f'roster_slot_{slot}'
            if widget_key not in st.session_state or st.session_state[widget_key] not in options:
                st.session_state[widget_key]=current
            selected=st.selectbox(slot,options,index=options.index(current),format_func=lambda x: labels.get(x,'— Empty —'),key=widget_key)
            if selected: picks[slot]=selected
            else: picks.pop(slot,None)
        st.session_state['dk_picks']=picks
        spent=sum(float(index.loc[key,'Salary']) for key in picks.values())
        remaining=CAP-spent
        p1,p2=st.columns(2)
        p1.metric('Salary remaining',f'${remaining:,.2f}')
        p2.metric('Slots filled',f'{len(picks)}/9')
        st.metric('Projected lineup points (proxy)',f"{sum(float(index.loc[key,score]) for key in picks.values() if pd.notna(index.loc[key,score])):.2f}")
        if remaining < 0: st.error('Over salary cap. Remove a player.')
        st.markdown('#### Exclude players')
        available=slate.loc[slate['Eligible'] & ~slate['Key'].isin(picks.values())].copy()
        keys=available['Key'].tolist()
        valid_old=[k for k in excluded if k in keys]
        exclude=st.multiselect('Players to exclude',keys,default=valid_old,format_func=lambda k:f"{index.loc[k,'Player']} ({index.loc[k,'Position']})",key='exclude_select')
        excluded=set(exclude)
        st.session_state['dk_excluded']=list(excluded)
        if st.button('Complete My Lineup',type='primary',use_container_width=True):
            result,err=optimize(slate,picks,excluded)
            if err: st.error(err)
            else:
                st.session_state['dk_picks']={row['Slot']:row['Key'] for _,row in result.iterrows()}
                for slot in SLOTS: st.session_state.pop(f'roster_slot_{slot}',None)
                st.session_state['dk_completed']=result
                st.rerun()
        if st.button('Clear roster',use_container_width=True):
            st.session_state['dk_picks']={}
            st.session_state.pop('dk_completed',None)
            for slot in SLOTS: st.session_state.pop(f'roster_slot_{slot}',None)
            st.rerun()
    with right:
        st.markdown('### Suggested roster picks')
        mode=st.radio('Ranking', ['Best Roster Fit','Best Projected','Best Value'],horizontal=True)
        st.caption('Top 3 per open position. Suggestions are checked for a feasible full nine-player lineup, not just individual affordability. "Best Projected" means highest uploaded DK Avg Pts (illustrative proxy).')
        # Display every position, including filled ones, to preserve a stable right-hand layout.
        position_slots = {'QB':['QB'], 'RB':['RB1','RB2'], 'WR':['WR1','WR2','WR3'],
                          'TE':['TE'], 'FLEX':['FLEX'], 'DST':['DST']}
        open_slots = [slot for slot in SLOTS if slot not in picks]
        if len(picks) == 9:
            st.success('All nine slots filled. Remove a player to see suggestions.')
            recs = pd.DataFrame()
        else:
            with st.spinner('Checking legal lineup completions...'):
                recs = suggestions(slate,picks,excluded,mode=mode)
            if recs.empty:
                st.warning('No feasible suggestions. Review locked selections, remaining budget, and kickoff times.')
        for position, slots in position_slots.items():
            open_count = sum(slot in open_slots for slot in slots)
            if not open_count:
                st.markdown(f'<div style="background:#292e38;color:#8b94a4;padding:11px 14px;border-radius:8px;opacity:.65;margin:8px 0"><b>{position} — POSITION FILLED</b><br><small>Suggestions disabled. Remove a player to reactivate.</small></div>',unsafe_allow_html=True)
                continue
            group = recs.loc[recs['Position']==position] if not recs.empty else pd.DataFrame()
            st.markdown(f'**{position} — {open_count} slot(s) open · Top {len(group)}**')
            if group.empty:
                st.caption('No feasible picks available for this position.')
                continue
            for _,row in group.iterrows():
                cols=st.columns([3,2,1])
                cols[0].write(str(row['Player']))
                cols[1].caption(f"${row['Salary']:,.2f} · {row['Demo Points']:.2f} pts · {row['Value']:.2f}x")
                if cols[2].button('Add',key=f"add_{position}_{row['Key']}"):
                    candidate=slate.set_index('Key').loc[row['Key']]
                    # A FLEX recommendation must go to FLEX, even if a dedicated slot is open.
                    compatible = (['FLEX'] if position == 'FLEX' else
                                  [slot for slot in slots if slot in open_slots and fits(candidate['Position'],slot)])
                    trial=dict(picks)
                    chosen=None
                    for slot in compatible:
                        trial[slot]=row['Key']
                        lineup,err=optimize(slate,trial,excluded)
                        if not err:
                            chosen=slot
                            break
                        trial.pop(slot,None)
                    if chosen:
                        st.session_state['dk_picks']=trial
                        st.session_state.pop(f'roster_slot_{chosen}',None)
                        st.rerun()
                    st.error('Could not place that player without making the roster infeasible.')
        st.divider()
        st.markdown('### Player pool')
        view=slate[['Player','Position','Team','Salary','Demo Points','Value','Status']].copy()
        view['Selection'] = view['Status'].map(lambda s:'LOCKED' if s in ('GAME STARTED','UNKNOWN KICKOFF','NO MODEL MATCH') else 'AVAILABLE')
        st.dataframe(view.style.format({'Salary':'${:,.2f}','Demo Points':'{:.2f}','Value':'{:.2f}'},na_rep='—').apply(lambda r:['background-color:#343944;color:#9aa0a6' if r['Selection']=='LOCKED' else '' for _ in r],axis=1),use_container_width=True,hide_index=True)
        st.caption('Gray rows cannot be selected. Historical mode uses mixed PPR-model and DST-average proxy points; demo mode uses uploaded DK averages.')
    st.divider()
    st.markdown('### Lineup validation summary · Version 8')
    filled = len(picks)
    total_salary = sum(float(index.loc[key, 'Salary']) for key in picks.values())
    total_points = sum(float(index.loc[key, score]) for key in picks.values() if pd.notna(index.loc[key, score]))
    unique_players = len(set(picks.values())) == filled
    valid_slots = all(fits(index.loc[key, 'Position'], slot) for slot, key in picks.items())
    eligible_picks = all(bool(index.loc[key, 'Eligible']) for key in picks.values())
    salary_ok = total_salary <= CAP
    c1, c2, c3 = st.columns(3)
    c1.metric('Roster slots', f'{filled}/{len(SLOTS)}')
    c2.metric('Salary cap', f'${total_salary:,.2f} / ${CAP:,.2f}')
    c3.metric('Projected points (proxy)', f'{total_points:.2f}')
    valid = filled == len(SLOTS) and unique_players and valid_slots and eligible_picks and salary_ok
    st.write('**Validation:** ' + ('PASS · Complete, unique, eligible, correct positions, under cap.'
                                  if valid else 'INCOMPLETE / INVALID · Check all nine slots, unique players, eligibility, positions, and cap.'))
    if demo_clock and demo_clock.startswith('Demo') and not source.startswith('Historical'):
        st.caption('SIMULATED DEMO: passing validation does not establish eligibility for an actual contest.')
    st.markdown('### Review proposed lineup')
    if len(picks)==9:
        lineup,err=optimize(slate,picks,excluded)
        if err: st.error(err)
        else:
            st.dataframe(lineup[['Slot','Player','Position','Team','Salary',score]].style.format({'Salary':'${:,.2f}',score:'{:.2f}'}),use_container_width=True,hide_index=True)
            st.success(f"Legal roster · ${lineup['Salary'].sum():,.2f} spent · {lineup[score].sum():.2f} {score_label.lower()}")
            approved=st.checkbox('I reviewed this research/demo lineup and understand it is not a validated live DraftKings projection.',value=False)
            if approved:
                st.download_button('Export approved lineup (CSV)',lineup[['Slot','Player','Position','Team','Salary',score]].round(2).to_csv(index=False).encode(),file_name='gridirongpt_dk_research_lineup.csv',mime='text/csv')
    else:
        st.info('Fill all nine slots manually or click Complete My Lineup to review a legal roster.')
