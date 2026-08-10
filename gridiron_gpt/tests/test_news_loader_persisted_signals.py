from gridiron_gpt.data_ingest import news_loader


def test_load_news_merges_persisted_signals(monkeypatch, tmp_path):
    monkeypatch.setattr(news_loader, "NEWS_PATH", tmp_path)
    monkeypatch.setattr(
        news_loader,
        "get_scoring_signals",
        lambda: [
            {
                "player": "Test Player",
                "team": "TST",
                "position": "WR",
                "source": "Live Feed",
                "headline": "Test Player earns first-team reps",
                "impact": "positive",
                "event_date": "2026-08-03",
                "signal_event_hash": "signal-1",
                "confidence": 0.9,
            }
        ],
    )

    items = news_loader.load_news()

    assert len(items) == 1
    assert items[0]["player"] == "Test Player"
    assert items[0]["fantasy_impact"] == "positive"
    assert items[0]["source"] == "Live Feed"


def test_load_news_deduplicates_local_and_persisted_copy(monkeypatch, tmp_path):
    local_item = {
        "player": "Test Player",
        "team": "TST",
        "headline": "Duplicate headline",
        "fantasy_impact": "positive",
        "date": "2026-08-03",
    }
    (tmp_path / "news.json").write_text(
        __import__("json").dumps([local_item]),
        encoding="utf-8",
    )

    monkeypatch.setattr(news_loader, "NEWS_PATH", tmp_path)
    monkeypatch.setattr(
        news_loader,
        "get_scoring_signals",
        lambda: [
            {
                "player": "Test Player",
                "team": "TST",
                "headline": "Duplicate headline",
                "impact": "positive",
                "event_date": "2026-08-03",
            }
        ],
    )

    assert len(news_loader.load_news()) == 1


def test_load_news_falls_back_when_persistence_is_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(news_loader, "NEWS_PATH", tmp_path)

    def fail():
        raise RuntimeError("Supabase unavailable")

    monkeypatch.setattr(news_loader, "get_scoring_signals", fail)

    assert news_loader.load_news() == []
