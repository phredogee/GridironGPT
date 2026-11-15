# GridironGPT DFS Phase 04 prototype

A separate local Streamlit demonstration; season-long modules are unchanged.

## Start

From the Git repository root:

```bash
cd gridiron_gpt
python -m pip install -r gridiron_streamlit_demo/requirements.txt
python -m streamlit run gridiron_streamlit_demo/app.py
```

Use Python 3.11 or 3.12. Select Lineup Lab, DraftKings, and Built-in synthetic slate. No API credentials, database service, historical dataset, or model file is needed for this path.

## Implemented

- Deterministic fictional player/salary/point fixture and downloadable source CSV.
- CSV validation, salary value display, kickoff eligibility, and roster completion.
- Manual picks act as locks; player exclusions constrain completion.
- Human review before lineup export; approval tied to roster and source.
- Separate historical-model explorer when real dataset/model artifacts are installed.

Synthetic points are test inputs, not model outputs. Uploaded-average mode and historical PPR replay are research proxies, not validated live DFS forecasts. FanDuel is not implemented.

## Tests

```bash
python -m pip install pytest
python -m pytest gridiron_streamlit_demo/test_phase4.py gridiron_streamlit_demo/test_dk_scoring.py -q
```

See `../docs/dfs/PHASE04_VALIDATION.md` for evidence and demonstration steps.
