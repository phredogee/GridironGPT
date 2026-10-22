# GridironGPT DFS Streamlit demo

This is a separate capstone demonstration UI. It does not modify the existing season-long app.

## Installation
Copy the `gridiron_streamlit_demo` directory into the root of your GridironGPT repository, next to `scripts` and `data`.

From the repo root in WSL (with your Python environment activated):

```bash
python -m pip install -r gridiron_streamlit_demo/requirements.txt
python -m streamlit run gridiron_streamlit_demo/app.py
```

Streamlit usually opens at http://localhost:8501.

## What works
- A designed multi-page dashboard, navigation, platform selector, and project status.
- Historical dataset exploration from `data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet`.
- Optional predictions using `data/dfs/models/phase3/tuning/random_forest_tuned.joblib`.
- Actual reported 2025 held-out evaluation metrics.
- Agent architecture and lineup builder interface previews.
- If no repository dataset is found, clearly labeled synthetic data supports a UI demo.

## Not yet implemented
Live DraftKings/FanDuel salaries, scoring adjustments, injury feeds, executable autonomous agents, roster optimization, export, and actual DFS contest performance.

## Caution
The model predicts historical PPR points, not site-specific DFS points. The historical model explorer is for demonstration and diagnostics; do not use held-out test data for tuning.

## Version 8 changes (2026-10-22)
- Demo simulation uses a clock one minute before the earliest valid CSV kickoff; no CSV dates are rewritten. Unknown kickoffs remain blocked. **Never use Demo simulation for live contest eligibility.**
- Live clock uses actual current time and preserves automatic kickoff lockout.
- Switching clock or projection source clears the selected lineup and exclusions.
- Displays projection source and a roster/salary/eligibility validation summary.
- The points metric is labeled as a proxy. Uploaded averages and historical PPR predictions are **not validated live DraftKings projections**.
- No changes to season-long GridironGPT modules.
