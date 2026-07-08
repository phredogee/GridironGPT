# GridironGPT - Project Overview

## Mission

GridironGPT is a fantasy football intelligence platform that ingests NFL news, extracts player-relevant signals, propagates downstream impacts through player relationships, and generates actionable fantasy football recommendations.

## Current Objectives

* Automate NFL news ingestion.
* Detect fantasy-relevant player signals.
* Propagate impacts through team relationships.
* Persist all intelligence in a cloud database.
* Build historical signal and scoring analytics.
* Deliver recommendations through CLI and Streamlit dashboards.

## Current Version

V4 Foundation

## Major Components

### Data Ingestion

* RSS News Fetcher
* ESPN/NFL data ingestion
* Player catalog and matching

### Intelligence Layer

* Signal extraction
* Signal scoring
* Entity relationship engine
* Impact propagation

### Persistence Layer

* Supabase/PostgreSQL
* Raw article storage
* Signal storage
* Propagated signal storage
* Ingestion run tracking

### Presentation Layer

* CLI tools
* Streamlit dashboard
* Recommendation reports

## Current Status

The platform has successfully transitioned from local JSON-only storage toward a cloud-backed event intelligence architecture using Supabase.
