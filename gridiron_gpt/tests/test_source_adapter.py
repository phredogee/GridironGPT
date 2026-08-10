from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class FakeSourceAdapter(SourceAdapter):

    @property
    def source_name(self) -> str:
        return "Test Source"

    def fetch(self) -> list[SourceRecord]:
        return [
            SourceRecord(
                source=self.source_name,
                headline="Test Player returns to practice.",
                player="Test Player",
                team="TST",
            )
        ]


def test_source_adapter_contract():
    adapter = FakeSourceAdapter()

    assert adapter.source_name == "Test Source"

    records = adapter.fetch()

    assert len(records) == 1
    assert isinstance(records[0], SourceRecord)
    assert records[0].source == "Test Source"


def test_source_adapter_cannot_be_instantiated():
    try:
        SourceAdapter()
    except TypeError:
        return

    raise AssertionError(
        "SourceAdapter should not be directly instantiable."
    )
