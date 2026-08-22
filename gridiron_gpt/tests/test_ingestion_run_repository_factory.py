import pytest

from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.ingestion_run_repository_factory import (
    PERSISTENCE_ENV,
    build_ingestion_run_repository,
)
from gridiron_gpt.ingestion.services.supabase_ingestion_run_repository import SupabaseIngestionRunRepository


def test_local_default_uses_jsonl():
    repository = build_ingestion_run_repository(environ={})

    assert isinstance(repository, JsonlIngestionRunRepository)


def test_explicit_jsonl_mode_uses_local_repository():
    repository = build_ingestion_run_repository(environ={PERSISTENCE_ENV: "jsonl"})

    assert isinstance(repository, JsonlIngestionRunRepository)


def test_supabase_mode_requires_and_uses_durable_client():
    client = object()
    calls = []

    def factory():
        calls.append(True)
        return client

    repository = build_ingestion_run_repository(
        environ={PERSISTENCE_ENV: "supabase"},
        supabase_client_factory=factory,
    )

    assert isinstance(repository, SupabaseIngestionRunRepository)
    assert repository._client is client
    assert calls == [True]


def test_mode_is_case_and_whitespace_tolerant():
    repository = build_ingestion_run_repository(
        environ={PERSISTENCE_ENV: "  JSONL  "},
    )

    assert isinstance(repository, JsonlIngestionRunRepository)


def test_unknown_mode_fails_instead_of_silently_falling_back():
    with pytest.raises(ValueError, match="expected 'jsonl' or 'supabase'"):
        build_ingestion_run_repository(environ={PERSISTENCE_ENV: "temporary"})
