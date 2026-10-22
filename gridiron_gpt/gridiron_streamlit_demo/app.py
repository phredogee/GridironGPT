import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from dfs_agents import CoordinatorAgent, AgentWorkflowError
from slate_import import import_draftkings_classic, SlateValidationError

st.set_page_config(page_title='GridironGPT | DFS Intelligence', page_icon='🏈', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp {background:#0b1220;color:#e5eaf2} [data-testid="stSidebar"]{background:#111d30}
.hero {padding:24px 30px;border:1px solid #2d405a;border-radius:16px;background:linear-gradient(110deg,#152b42,#102038);margin-bottom:20px}
.kicker{color:#62d5bb;font-size:12px;font-weight:700;letter-spacing:2px}.hero h1{margin:6px 0;font-size:36px}.sub{color:#b8c8d8}
.card{padding:18px;border:1px solid #2b405b;border-radius:12px;background:#142237;margin-bottom:12px}.tag{color:#70e0c2;font-weight:700}
</style>''', unsafe_allow_html=True)
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
MODEL_PATH = REPO/'data/dfs/models/phase3/tuning/random_forest_tuned.joblib'
DATA_PATH = REPO/'data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet'
METRICS_PATH = REPO/'data/dfs/models/phase3/final_evaluation/test_metrics_2025.csv'

@st.cache_data

def load_data():
    if DATA_PATH.exists():
        df=pd.read_parquet(DATA_PATH)
        return df[df['position'].isin(['QB','RB','WR','TE'])].copy(), 'Repository dataset'
    rng=np.random.default_rng(42)
    names=['Quarterback A','Quarterback B','Running Back A','Running Back B','Running Back C','Wide Receiver A','Wide Receiver B','Wide Receiver C','Wide Receiver D','Tight End A','Tight End B']
    positions=['QB','QB','RB','RB','RB','WR','WR','WR','WR','TE','TE']
    rows=[]
    for w in range(1,19):
        for n,p in zip(names,positions):
            pts=max(0,float(rng.normal({'QB':19,'RB':12,'WR':11,'TE':8}[p],4)))
            rows.append({'player_name':n,'position':p,'season':2025,'week':w,'fantasy_points_ppr':pts,'fantasy_points_ppr_roll3':pts*0.8+2,'fantasy_points_ppr_roll5':pts*0.85+1})
    return pd.DataFrame(rows),'Illustrative demo data (no repository dataset found)'

def player_col(df):
    for name in ('player_display_name','player_name'):
        if name in df.columns: return name
    return None

st.sidebar.markdown('## 🏈 GRIDIRONGPT')
st.sidebar.caption('DFS INTELLIGENCE • CAPSTONE DEMO')
page=st.sidebar.radio('Explore', ['Overview','Player Projections','Agent Workflow','Lineup Lab','Model Evaluation'])
st.sidebar.divider()
platform=st.sidebar.selectbox('DFS platform', ['DraftKings','FanDuel'])
st.sidebar.info('**Prototype status:** Historical agents work locally. DraftKings Classic demo optimization is available using uploaded DK historical averages. Live DFS projections are not connected.')

st.markdown('''<div class="hero"><div class="kicker">AI-POWERED NFL DAILY FANTASY</div><h1>GridironGPT <span style="color:#6ce0c4">DFS Intelligence</span></h1><div class="sub">Player forecasting • Agent orchestration • Lineup research • Human review</div></div>''', unsafe_allow_html=True)
df,source=load_data()
model_available=MODEL_PATH.exists()
col1,col2,col3,col4=st.columns(4)
col1.metric('Model', 'Tuned Random Forest' if model_available else 'Demo mode')
col2.metric('2025 Test MAE','4.55')
col3.metric('2025 Test RMSE','6.18')
col4.metric('Baseline MAE gain','3.82%')
st.caption(f'Data: {source} • Platform selected: {platform} • 2025 evaluation metrics are verified project results, not live contest projections.')

if page=='Overview':
    st.subheader('From historical data to informed lineup decisions')
    a,b=st.columns([2,1])
    with a:
        st.markdown('''<div class="card"><span class="tag">PHASE 3 COMPLETE</span><h3>Forecasting foundation validated</h3>Our locked model was evaluated on 6,037 held-out player-week records from the 2025 NFL season. The model reduced MAE by 3.82% compared with a three-game rolling baseline on matched observations.</div>''',unsafe_allow_html=True)
        st.markdown('''<div class="card"><span class="tag">NEXT BUILD</span><h3>Agents + slate-aware optimization</h3>Integrate salary feeds, site-specific scoring, eligibility rules, projection adjustments, and constrained lineup generation. Every recommended lineup will require user review before export.</div>''',unsafe_allow_html=True)
    with b:
        st.markdown('### Pipeline readiness')
        for label,ready in [('Historical dataset',DATA_PATH.exists()),('Trained model',model_available),('2025 evaluation',METRICS_PATH.exists()),('Imported DFS salaries',False),('Lineup optimizer',True)]:
            st.write(('✅' if ready else '◻️')+' '+label)
    st.info('Demo tip: Open **Player Projections** to inspect historical player-week data, then **Agent Workflow** to demonstrate the planned handoffs.')

elif page=='Player Projections':
    st.subheader('Player projection explorer')
    st.caption('Historical backtest viewer. This is not a live upcoming-week forecast.')
    seasons=sorted(df['season'].dropna().unique().tolist())
    season=st.selectbox('Historical season',seasons,index=len(seasons)-1)
    weeks=sorted(df.loc[df.season==season,'week'].dropna().unique().tolist())
    week=st.selectbox('NFL week',weeks,index=min(7,len(weeks)-1))
    positions=st.multiselect('Positions',['QB','RB','WR','TE'],default=['QB','RB','WR','TE'])
    subset=df[(df.season==season)&(df.week==week)&df.position.isin(positions)].copy()
    name=player_col(subset)
    if name is None: subset['player']='Unknown'; name='player'
    columns=[name,'position','fantasy_points_ppr']
    for col in ['fantasy_points_ppr_roll3','fantasy_points_ppr_roll5']:
        if col in subset.columns: columns.append(col)
    view=subset[columns].rename(columns={name:'Player','position':'Pos','fantasy_points_ppr':'Actual PPR','fantasy_points_ppr_roll3':'3-game historical avg','fantasy_points_ppr_roll5':'5-game historical avg'})
    st.dataframe(view.sort_values('Actual PPR',ascending=False).style.format(precision=2),use_container_width=True,hide_index=True)
    st.caption('Historical averages are pregame features. Actual PPR is displayed only for retrospective comparison.')
    st.markdown('### Run the historical agent pipeline')
    st.caption('Coordinator → Data Agent → Projection Agent. Runs a locked model; never retrains or retrieves live DFS salaries.')
    if not (model_available and DATA_PATH.exists()):
        st.warning('The real dataset and trained model must both exist to run agents. Demo data cannot be used for model inference.')
    elif st.button('Run Data + Projection Agents', type='primary'):
        coordinator = CoordinatorAgent(DATA_PATH, MODEL_PATH)
        try:
            result, events = coordinator.run(int(season), int(week), positions)
            st.session_state['last_agent_events'] = [e.__dict__ for e in events]
            st.session_state['last_agent_run'] = (int(season), int(week), len(result))
            st.session_state['last_agent_results'] = result
        except AgentWorkflowError as exc:
            st.session_state['last_agent_events'] = [e.__dict__ for e in exc.events]
            st.session_state.pop('last_agent_results', None)
            st.error(f'Agent workflow failed: {exc}')
    last = st.session_state.get('last_agent_run')
    if last and last[:2] == (int(season), int(week)) and 'last_agent_results' in st.session_state:
        result = st.session_state['last_agent_results']
        display_cols = [name, 'position', 'projected_ppr', 'fantasy_points_ppr', 'absolute_error']
        result_view = result[display_cols].rename(columns={name:'Player','position':'Pos','projected_ppr':'Projected PPR',
                  'fantasy_points_ppr':'Actual PPR','absolute_error':'Absolute error'})
        st.dataframe(result_view.sort_values('Projected PPR', ascending=False).style.format(precision=2), use_container_width=True, hide_index=True)
        mae = float(result['absolute_error'].mean())
        rmse = float(np.sqrt(np.mean((result['projected_ppr']-result['fantasy_points_ppr'])**2)))
        m1,m2,m3 = st.columns(3)
        m1.metric('Player-weeks',len(result))
        m2.metric('Selected-week MAE',f'{mae:.2f}')
        m3.metric('Selected-week RMSE',f'{rmse:.2f}')
        st.caption('Historical retrospective only. 2020–2023 are training years (in-sample); 2024 validation; 2025 held-out test. This week-level view is descriptive, not a new independent evaluation.')
        st.download_button('Export historical projections (CSV)', result_view.round(2).to_csv(index=False).encode('utf-8'),
                           file_name=f'gridirongpt_historical_{season}_week{week}.csv', mime='text/csv')
    if st.session_state.get('last_agent_events'):
        with st.expander('Agent execution log', expanded=True):
            st.dataframe(pd.DataFrame(st.session_state['last_agent_events']), use_container_width=True, hide_index=True)

elif page=='Agent Workflow':
    st.subheader('Multi-agent orchestration')
    st.success('Implemented: Coordinator, Data, and Projection Agents for historical inference. Open Player Projections and click Run Data + Projection Agents to execute them.')
    st.caption('Context, Value, Optimization, and Evaluation Agents are design previews, not active integrations.')
    steps=[('Coordinator Agent — ACTIVE','Orchestrates the historical Data → Projection workflow and records handoffs.'),('Data Agent — ACTIVE','Validates historical player-week records. Live slate salaries are not connected.'),('Projection Agent — ACTIVE','Loads the locked Random Forest to estimate historical PPR points.'),('Context Agent','Adds injury, matchup, and availability checks when connected.'),('Value Agent','Converts site-specific projected points into salary-adjusted value.'),('Optimization Agent','Solves roster and salary constraints for the selected contest.'),('Evaluation Agent','Checks output consistency, warnings, and audit trail.'),('Human Review','Users review historical results; future lineup exports will require approval.')]
    for idx,(agent,description) in enumerate(steps,1):
        with st.expander(f'{idx:02d}  {agent}',expanded=idx<=2): st.write(description)
    st.divider()
    st.checkbox('Require human approval before exporting lineup',value=True,disabled=True)
    if st.session_state.get('last_agent_events'):
        st.markdown('#### Last real agent execution')
        st.dataframe(pd.DataFrame(st.session_state['last_agent_events']), hide_index=True, use_container_width=True)
    st.info('Salary-dependent agents remain inactive until real slate data and lineup rules are implemented.')

elif page=='Lineup Lab':
    from lineup_ui import render_lineup_lab
    render_lineup_lab(platform, import_draftkings_classic, SlateValidationError, DATA_PATH, MODEL_PATH)

elif page=='Model Evaluation':
    st.subheader('Locked 2025 test evaluation')
    st.markdown('The following are **measured**, held-out 2025 results, not simulated metrics.')
    metrics=pd.DataFrame([
        {'Cohort':'All 2025','Model':'Tuned Random Forest','Rows':6037,'MAE':4.5537,'RMSE':6.1822,'Bias':0.2390},
        {'Cohort':'Baseline-eligible','Model':'Tuned Random Forest','Rows':5427,'MAE':4.5394,'RMSE':6.2103,'Bias':0.1836},
        {'Cohort':'Baseline-eligible','Model':'Rolling baseline','Rows':5427,'MAE':4.7195,'RMSE':6.7683,'Bias':-0.0808},
        {'Cohort':'Cold start','Model':'Tuned Random Forest','Rows':610,'MAE':4.6814,'RMSE':5.9262,'Bias':0.7315},
    ])
    if METRICS_PATH.exists():
        try: metrics=pd.read_csv(METRICS_PATH)
        except Exception: pass
    st.dataframe(metrics.style.format(precision=2),use_container_width=True,hide_index=True)
    st.markdown('#### Interpretation')
    st.write('The model generalizes to an unseen season and beats the rolling baseline on matched records. Cold-start observations show positive prediction bias. The current evaluation concerns PPR prediction, not DraftKings/FanDuel contest profitability.')
