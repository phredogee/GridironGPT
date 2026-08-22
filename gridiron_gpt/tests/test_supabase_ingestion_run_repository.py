from types import SimpleNamespace

from gridiron_gpt.ingestion.services.supabase_ingestion_run_repository import (
    SupabaseIngestionRunRepository,
)


class FakeQuery:
    def __init__(self, *, data=None):
        self.data = data or []
        self.calls = []

    def upsert(self, payload, *, on_conflict=None):
        self.calls.append(("upsert", payload, on_conflict))
        return self

    def select(self, columns):
        self.calls.append(("select", columns))
        return self

    def order(self, column, *, desc=False):
        self.calls.append(("order", column, desc))
        return self

    def execute(self):
        self.calls.append(("execute",))
        return SimpleNamespace(data=self.data)


class FakeClient:
    def __init__(self, query):
        self.query = query
        self.tables = []

    def table(self, name):
        self.tables.append(name)
        return self.query


class Run:
    def to_dict(self):
        return {"run_id": "run-1", "success": True, "completed_at": "2026-08-22T17:16:26+00:00"}


def test_save_upserts_complete_run_payload_by_run_id():
    query = FakeQuery()
    client = FakeClient(query)
    repository = SupabaseIngestionRunRepository(client)

    repository.save(Run())

    assert client.tables == ["cortex_ingestion_runs"]
    assert query.calls == [
        (
            "upsert",
            {"run_id": "run-1", "success": True, "completed_at": "2026-08-22T17:16:26+00:00"},
            "run_id",
        ),
        ("execute",),
    ]


def test_load_all_returns_newest_runs_first():
    rows = [
        {"run_id": "new", "completed_at": "2026-08-22T17:00:00+00:00"},
        {"run_id": "old", "completed_at": "2026-08-21T17:00:00+00:00"},
    ]
    query = FakeQuery(data=rows)
    client = FakeClient(query)
    repository = SupabaseIngestionRunRepository(client)

    assert repository.load_all() == rows
    assert client.tables == ["cortex_ingestion_runs"]
    assert query.calls == [
        ("select", "*"),
        ("order", "completed_at", True),
        ("execute",),
    ]


def test_custom_table_name_is_supported_for_isolated_environments():
    query = FakeQuery()
    client = FakeClient(query)
    repository = SupabaseIngestionRunRepository(client, table_name="test_cortex_ingestion_runs")

    repository.save({"run_id": "run-2"})

    assert client.tables == ["test_cortex_ingestion_runs"]
