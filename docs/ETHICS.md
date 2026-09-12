# DFS Capstone Ethics and Responsible AI

## Purpose

GridironGPT DFS Intelligence is designed as a human-in-the-loop decision-support system for NFL Daily Fantasy Sports analysis. It is not designed to autonomously wager, enter contests, or guarantee financial outcomes.

## Human Authority

Human control is preserved at two explicit decision points:

1. **Pre-optimization review:** the user reviews projections, value signals, injuries or late information, and may lock or exclude players or set strategy constraints.
2. **Post-optimization decision:** the user reviews candidate lineups and may accept, modify, or reject them.

The optimizer proposes solutions within supplied constraints; it does not replace the user's final judgment.

## Prediction Uncertainty

NFL outcomes are uncertain. Model projections are estimates based on historical and pregame information and must not be represented as guarantees. Evaluation will document prediction error using appropriate regression metrics and comparison with a simple baseline.

Where practical, the system should expose uncertainty or confidence information and provide enough context for the user to understand why a player or lineup is being recommended.

## Data Integrity and Leakage

Only information available before the relevant game's kickoff may be used as predictive input. Post-game statistics or future information must not leak into historical training features. Chronological validation and testing are required to preserve realistic forecasting conditions.

## Data Access and Platform Boundaries

The project will use legitimate and permitted data-access methods. It will not depend on circumventing platform restrictions, prohibited scraping, or automated contest-entry behavior. DraftKings/FanDuel salary and slate data should be obtained through permitted sources, platform-provided files where available, or user-provided imports.

## Responsible DFS Framing

The application should describe outputs as projections, estimates, comparisons, or recommendations rather than guaranteed winning lineups. Historical backtests and successful past outcomes must not be presented as proof of future financial returns.

## Model Error and Bias

Model performance should be evaluated overall and by relevant groups such as player position. Significant systematic errors should be documented and investigated. Model complexity should be justified by measurable improvement rather than assumed to be superior to simpler methods.

## Existing-System Safety

The Capstone must remain additive to GridironGPT. DFS development must not silently alter authoritative season-long rankings, draft decisions, waiver behavior, or weekly lineup behavior. Shared functionality should be integrated through explicit interfaces and regression-tested.

## Ethical Success Condition

The project satisfies its responsible-AI objective when predictions are evaluated transparently, human authority is retained before and after optimization, platform/data boundaries are respected, uncertainty is not misrepresented, and no autonomous contest entry occurs.