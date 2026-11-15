# GridironGPT DFS Commands

This file tracks commands specific to DFS Capstone development. Do not add commands here unless they are specific to the DFS branch/workflow.

## Branch

```bash
git switch dfs-capstone
```

Return to the season-long core:

```bash
git switch main
```

## Current development rule

Before DFS work:

```bash
git status
```

Confirm that DFS development is occurring on `dfs-capstone` before making Capstone-specific changes.

## Testing

Use the existing GridironGPT test suite as the regression boundary while DFS-specific tests are added.

Exact DFS test commands will be documented here once the package/test paths are established.



## Phase 04 local demonstration

From the Git repository root:

```bash
cd gridiron_gpt
python -m pip install -r gridiron_streamlit_demo/requirements.txt
python -m streamlit run gridiron_streamlit_demo/app.py
```

Select Lineup Lab -> Built-in synthetic slate. Select a QB manually to lock it; exclude a player; click Complete My Lineup; review validation; approve; export CSV.

```bash
python -m pip install pytest
python -m pytest gridiron_streamlit_demo/test_phase4.py gridiron_streamlit_demo/test_dk_scoring.py -q
```
