# Phase E — Intelligence Calibration

## Purpose

Phase E measures whether Cortex predictions are useful, whether confidence values are honest, and which evidence paths improve or degrade decision quality.

```text
Historical evidence
    ↓
Leakage-safe replay
    ↓
Prediction records
    ↓
Observed outcomes
    ↓
Evaluation / calibration
    ↓
Signal, source, and relationship quality
    ↓
Candidate parameter tuning
```

## E1 — Prediction and Outcome Ledger

`PredictionRecord` captures player, horizon, direction, confidence, signal type, contributing sources, relationship types, and metadata.

`OutcomeRecord` attaches a later observed direction and optional measured value to the original prediction ID.

`JsonlCalibrationRepository` stores both streams append-only and suppresses duplicate prediction/outcome IDs. Only paired predictions and outcomes enter evaluation.

## E2 — Historical Replay

`HistoricalReplayRunner` sorts evidence chronologically and invokes the predictor with only the records visible before the current item. The current event and future records are never included in historical context.

Timezone-aware timestamps are required to avoid ambiguous ordering.

## E3 — Prediction Evaluation

`PredictionEvaluator` calculates:

- directional correctness
- aggregate accuracy
- Brier score for confidence-sensitive error
- mean Brier score
- confidence-bin accuracy
- per-bin calibration error

A confident incorrect prediction receives a much larger penalty than an uncertain incorrect prediction.

## E4 — Signal and Source Quality

Quality reports include independent breakdowns by:

- signal type
- evidence source
- relationship type

Each group reports sample count, accuracy, and mean Brier score. These measurements expose which evidence paths are useful without changing live weights automatically.

## E5 — Outcome Classification

`OutcomeDirectionService` converts measured deltas into positive, neutral, or negative outcomes using a configurable neutral band. This prevents tiny statistical changes from being treated as meaningful success or failure.

## E6 — Parameter Calibration

`GridParameterTuner` evaluates explicit candidate parameter sets against a caller-supplied historical objective. It supports minimizing error metrics such as Brier score or maximizing metrics such as accuracy.

The tuner never mutates production configuration. Selected parameters remain reviewable candidates until intentionally adopted.

## Guardrails

- No future evidence during historical replay
- Append-only prediction/outcome history
- Duplicate-ID suppression
- Timezone-aware chronology
- Confidence constrained to 0–1
- Empty and incomplete datasets handled explicitly
- Source and relationship quality include sample counts
- Parameter tuning is deterministic and non-mutating
- Calibration measurements do not silently rewrite production rules

## Validation

Run the focused Phase E suite:

```bash
pytest \
  tests/test_calibration.py \
  tests/test_calibration_tuning.py \
  -v
```

Then run the complete repository regression suite:

```bash
pytest -v
```

Phase E is complete only after both gates pass.
