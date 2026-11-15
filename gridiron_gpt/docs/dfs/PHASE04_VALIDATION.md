# Phase 04 prototype validation

## Scope and result

Focused tests executed November 15 2026: **13 passed**. Includes the existing three observed-scoring tests and ten new integration/UI cases (six parametrized invalid-lineup scenarios). The tested synthetic workflow requires no real dataset/model. No live deployment, profitability result, or full-core regression result is claimed.

## Automated checks

- Reproducible fixture bytes; importer-to-solver integration.
- Nine unique players, valid slot positions, salary within cap.
- Requested QB lock retained and excluded WR omitted.
- No-QB, over-cap, conflicting constraints, wrong-slot, started-game, and unknown-kickoff rejection.
- Invalid salary and duplicate player ID rejection.
- Streamlit navigation, synthetic disclosure, automatic completion, approval-gated export visibility, and roster clearing.

## Demonstration script

1. Start the application with the README command.
2. Select DraftKings and Lineup Lab. Show the synthetic-data disclosure and download source CSV.
3. Select Synthetic QB 01 in QB; exclude Synthetic WR 12.
4. Complete the lineup. Show the retained QB, absent excluded player, nine unique selections, and salary cap summary.
5. Review the result and check approval. Export the lineup CSV and open it to show the nine rows.
6. Clear the roster. Explain that export is unavailable until a new complete roster is reviewed.
7. Explain that fictional points validate software behavior, while historical model evaluation is separate evidence.

## Before submission

Run this demonstration in Fred's local environment, record screenshots/video if desired, record environment and observed response time, and package the repository commit with a concise Phase 04 progress report. The assignment instructions supplied do not prescribe public hosting. The downloadable CSV is a research export, not guaranteed site-upload format.
