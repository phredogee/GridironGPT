from gridiron_gpt.data_ingest import news_persistence


def test_duplicate_article_is_skipped_without_failing_ingestion(monkeypatch):
    finished = {}
    processed = []

    monkeypatch.setattr(news_persistence, "start_ingestion_run", lambda source: "run-1")
    monkeypatch.setattr(
        news_persistence,
        "save_raw_article",
        lambda **kwargs: {"id": "article-1", "_created": False},
    )
    monkeypatch.setattr(
        news_persistence,
        "process_signal",
        lambda **kwargs: processed.append(kwargs),
    )
    monkeypatch.setattr(
        news_persistence,
        "finish_ingestion_run",
        lambda **kwargs: finished.update(kwargs),
    )

    result = news_persistence.persist_news_items(
        [
            {
                "headline": "Existing NFL story",
                "source": "Test Feed",
                "url": "https://example.test/story",
                "date": "2026-08-03",
                "player": "Test Player",
                "team": "TST",
                "fantasy_impact": "positive",
                "story_hash": "existing-hash",
            }
        ],
        source_name="test-feed",
    )

    assert result["status"] == "success"
    assert result["articles_saved"] == 0
    assert result["signals_saved"] == 0
    assert result["skipped"] == 1
    assert result["skipped_duplicate"] == 1
    assert processed == []
    assert finished["status"] == "success"
    assert finished["articles_new"] == 0
    assert finished["articles_skipped"] == 1
