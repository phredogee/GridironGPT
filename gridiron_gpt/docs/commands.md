# Useful Commands

## Test Supabase

PYTHONPATH=. python -c "
from gridiron_gpt.storage.supabase_client import get_supabase_client
print(get_supabase_client())
"

## Run RSS Ingestion

PYTHONPATH=. python - <<'PY'
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))

from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_persist_from_env

print(fetch_and_persist_from_env())
PY

## Run Recommendation Engine

PYTHONPATH=. python -c "
from gridiron_gpt.data_ingest.player_scores import build_recommendations_report
print(build_recommendations_report())
"

## Launch Dashboard

PYTHONPATH=. streamlit run streamlit_app.py
