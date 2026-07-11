# Known Issues

## Current

- RSS ingestion currently generates relatively few signals.
- Player catalog coverage is incomplete.
- Some valid players are not detected.
- Duplicate article handling exists but duplicate signal detection does not.
- Signal decay has not been implemented.
- Recency weighting has not been implemented.
- Score history persistence has not been implemented.
- Source reliability scoring has not been implemented.

## Metrics Snapshot

Latest RSS Run:

Articles Found: 27
Signals Saved: 5
Skipped: 22

Primary Bottleneck:
Player detection and impact classification.
