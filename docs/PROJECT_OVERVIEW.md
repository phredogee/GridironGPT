# GridironGPT Project Overview

GridironGPT is a fantasy-football intelligence platform powered by the reusable Gridiron Cortex decision engine. The application ingests NFL news, resolves players, converts evidence into Cortex events, updates persistent score state, produces recommendations and explanations, and exposes operational/intelligence views through Streamlit.

## Current State

- Stable v1.0 runtime architecture is tagged and released.
- v1.1 development is focused on continuous ingestion, observability, performance, and history accumulation.
- Automated ingestion currently uses ESPN NFL and RotoWire NFL RSS providers.
- Cortex persists event history, scorecards, recommendations, and replayable decision trails.
- Ingestion records provider health, normalized events, Cortex-accepted events, duplicate events, and processor failures.
- Current regression baseline: 709 passing tests as of 2026-08-10.

## Runtime Flow

NFL providers -> ingestion adapters -> player resolution -> normalized RawEvents -> Gridiron Cortex -> deduplication -> signal/impact/scoring/recommendation -> persistent history and scorecards -> Streamlit.

## Operational Goal

Allow GridironGPT to continuously accumulate trustworthy historical evidence without duplicate inflation while keeping provider failures observable and isolated.