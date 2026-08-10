from gridiron_gpt.data_ingest.rss_news_fetcher import (
    _extract_searchable_url_text,
)


def test_extracts_player_name_from_url_path():
    url = (
        "https://www.espn.com/nfl/story/_/id/49351981/"
        "rams-alaric-jackson-face-felony-charge-june-arrest"
    )

    result = _extract_searchable_url_text(url)

    assert "alaric jackson" in result


def test_removes_numeric_url_segments():
    url = (
        "https://www.espn.com/nfl/story/_/id/49352279/"
        "packers-sign-lb-isaiah-mcduffie-one-year-extension"
    )

    result = _extract_searchable_url_text(url)

    assert "isaiah mcduffie" in result
    assert "49352279" not in result
