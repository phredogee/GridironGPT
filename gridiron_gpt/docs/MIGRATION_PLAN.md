# GridironGPT to Gridiron Cortex Migration Plan

## Purpose

GridironGPT has evolved through several architectural generations.

The current goal is to consolidate football intelligence inside
`gridiron_cortex` while keeping GridironGPT focused on application,
ingestion, and presentation responsibilities.

This document tracks the retirement of legacy code and the migration of
active capabilities into the Cortex engine.

---

## Target Architecture

```text
Applications
├── Streamlit
├── CLI
└── Future REST API
        │
        ▼
CortexFacade
        │
        ├── CortexEngine
        │   ├── EntityResolver
        │   ├── SignalProcessor
        │   ├── RelationshipEngine
        │   ├── ScoreEngine
        │   ├── RecommendationEngine
        │   └── ExplanationEngine
        │
        └── KnowledgeService
            ├── EventRepository
            ├── PlayerScorecardRepository
            └── RelationshipRepository


Save it.

---

## 2. Confirm the retirement targets are tracked

```bash
git ls-files modules embeddings cli_modules | head -50

## Legacy but Active: `phred/`

The `phred/` package remains an active dependency for parts of the CLI,
semantic ingestion, ranking pipeline, ESPN fetchers, diagnostics, and tests.

It must not be removed until all consumers have migrated to supported
`gridiron_gpt` or `gridiron_cortex` packages.

Planned migration order:

1. Feedback utilities
2. CLI diagnostics
3. ESPN fetchers
4. Ranking pipeline
5. Semantic ingestion
6. Tests
7. Retire `phred/`
