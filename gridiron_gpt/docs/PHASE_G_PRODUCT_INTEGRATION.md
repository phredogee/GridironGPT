# Phase G — Product & API Integration

## Purpose

Phase G exposes the intelligence built in Phases A–F through stable product interfaces. The product layer orchestrates Cortex and the Fantasy Decision Engine without moving business logic into Streamlit or HTTP route handlers.

```text
Gridiron Cortex + Football Context + Calibration
                    ↓
          Fantasy Decision Engine
                    ↓
          GridironProductService
             ↙               ↘
       FastAPI API       Streamlit Product App
```

## G1 — Product Service and REST API

`GridironProductService` is the application-facing boundary shared by API and UI clients.

FastAPI endpoints:

- `GET /health`
- `GET /leagues`
- `POST /leagues`
- `GET /leagues/{league_id}`
- `DELETE /leagues/{league_id}`
- `POST /decisions/draft/{league_id}`
- `POST /decisions/start-sit`
- `POST /decisions/waivers`
- `POST /decisions/trade`
- `POST /decisions/roster`

Run locally:

```bash
uvicorn gridiron_gpt.api.app:app --reload
```

OpenAPI documentation is available at `/docs`.

## G2 — Persistent League Management

`LeagueProfile` and `JsonLeagueProfileRepository` support multiple editable league configurations.

Configurable fields include:

- league name and ID
- number of teams
- total roster size
- arbitrary starting lineup slots
- bench slots
- IR slots
- FAAB budget
- standard, half-PPR, or PPR scoring

Profiles are stored as readable JSON files under `data/leagues/` by default.

## G3 — Streamlit Product Application

`product_app.py` provides a dedicated product-facing entrypoint while preserving the existing Cortex operations dashboard.

Run locally:

```bash
streamlit run product_app.py
```

The product app includes:

- League Settings
- Draft rankings
- Start/sit builder
- Waiver and FAAB center
- Trade evaluator
- Roster construction analysis
- API launch documentation

The existing `streamlit_app.py` remains available for Cortex inspection, player intelligence, trends, ingestion status, and operational dashboards.

## G4 — Design Boundary

Streamlit pages and FastAPI routes do not calculate fantasy recommendations directly. Both delegate to `GridironProductService` and `FantasyDecisionEngine`, keeping interfaces replaceable and testable.

## Validation

Phase G validation includes:

- persistent league profile CRUD and update behavior
- customizable team and roster limits
- configurable lineup slots
- API health and league CRUD
- draft rankings over HTTP
- start/sit over HTTP
- waiver, trade, and roster decisions over HTTP
- full repository regression testing
