from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_gpt.intelligence.relationship_refresh_service import (
    RelationshipRefreshService,
)


def make_relationship(
    source: str = "player_a",
    target: str = "player_b",
    relationship_type: str = "backs_up",
    strength: float = 0.75,
    confidence: float = 0.90,
    active: bool = True,
) -> EntityRelationship:
    return EntityRelationship(
        source_entity_id=source,
        source_entity_name=source.replace("_", " ").title(),
        source_entity_type="player",
        target_entity_id=target,
        target_entity_name=target.replace("_", " ").title(),
        target_entity_type="player",
        relationship_type=relationship_type,
        strength=strength,
        confidence=confidence,
        reason="Test relationship.",
        source_team="TST",
        target_team="TST",
        active=active,
    )


def build_service(
    tmp_path: Path,
) -> tuple[CortexFacade, RelationshipRefreshService]:
    cortex = CortexFacade(data_directory=tmp_path)

    service = RelationshipRefreshService(
        knowledge_service=cortex.knowledge
    )

    return cortex, service


def test_refresh_adds_new_relationship(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    relationship = make_relationship()

    result = service.refresh([relationship])

    assert result.proposed == 1
    assert result.current == 0
    assert result.new == 1
    assert result.changed == 0
    assert result.unchanged == 0
    assert result.stale == 0
    assert result.written == 1

    current = cortex.knowledge.get_current_relationships()

    assert len(current) == 1
    assert current[0].active is True
    assert current[0].first_seen is not None
    assert current[0].last_updated is not None


def test_refresh_does_not_rewrite_unchanged_relationship(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    relationship = make_relationship()

    first = service.refresh([relationship])
    second = service.refresh([relationship])

    assert first.written == 1

    assert second.new == 0
    assert second.changed == 0
    assert second.unchanged == 1
    assert second.stale == 0
    assert second.written == 0

    relationship_file = tmp_path / "relationships.jsonl"

    lines = relationship_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 1


def test_refresh_writes_changed_relationship(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    original = make_relationship(
        strength=0.75,
    )

    service.refresh([original])

    changed = make_relationship(
        strength=0.55,
    )

    result = service.refresh([changed])

    assert result.new == 0
    assert result.changed == 1
    assert result.unchanged == 0
    assert result.stale == 0
    assert result.written == 1

    current = cortex.knowledge.get_current_relationships()

    assert len(current) == 1
    assert current[0].strength == 0.55

    relationship_file = tmp_path / "relationships.jsonl"

    lines = relationship_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 2


def test_refresh_marks_missing_relationship_stale(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    relationship = make_relationship()

    service.refresh([relationship])

    result = service.refresh([])

    assert result.new == 0
    assert result.changed == 0
    assert result.unchanged == 0
    assert result.stale == 1
    assert result.written == 1

    active = cortex.knowledge.get_current_relationships()

    assert active == []

    all_current = (
        cortex.knowledge.get_current_relationships(
            active_only=False
        )
    )

    assert len(all_current) == 1
    assert all_current[0].active is False


def test_refresh_preserves_first_seen_when_relationship_changes(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    original = make_relationship(
        strength=0.75,
    )

    service.refresh([original])

    first_snapshot = (
        cortex.knowledge.get_current_relationships()[0]
    )

    changed = make_relationship(
        strength=0.60,
    )

    service.refresh([changed])

    latest = (
        cortex.knowledge.get_current_relationships()[0]
    )

    assert latest.first_seen == first_snapshot.first_seen
    assert latest.strength == 0.60


def test_refresh_handles_mixed_graph_changes(
    tmp_path: Path,
):
    _, service = build_service(tmp_path)

    unchanged = make_relationship(
        source="player_a",
        target="player_b",
    )

    changed = make_relationship(
        source="player_c",
        target="player_d",
        strength=0.80,
    )

    stale = make_relationship(
        source="player_e",
        target="player_f",
    )

    service.refresh(
        [
            unchanged,
            changed,
            stale,
        ]
    )

    changed_update = make_relationship(
        source="player_c",
        target="player_d",
        strength=0.50,
    )

    new_relationship = make_relationship(
        source="player_g",
        target="player_h",
    )

    result = service.refresh(
        [
            unchanged,
            changed_update,
            new_relationship,
        ]
    )

    assert result.proposed == 3
    assert result.current == 3

    assert result.new == 1
    assert result.changed == 1
    assert result.unchanged == 1
    assert result.stale == 1

    assert result.written == 3

def test_preview_does_not_write_relationships(
    tmp_path: Path,
):
    cortex, service = build_service(tmp_path)

    relationship = make_relationship()

    result = service.preview([relationship])

    assert result.proposed == 1
    assert result.current == 0
    assert result.new == 1
    assert result.changed == 0
    assert result.unchanged == 0
    assert result.stale == 0
    assert result.written == 0

    relationship_file = tmp_path / "relationships.jsonl"

    lines = relationship_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert lines == []
