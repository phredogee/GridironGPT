from apps.streamlit.components.app_shell import build_navigation_markup


def test_intelligence_section_contains_expected_children():
    markup = build_navigation_markup("Dashboard")

    assert ">Intelligence<" in markup
    assert "?page=Dashboard" in markup
    assert "?page=Players" in markup
    assert "?page=Trends" in markup
    assert "?page=Trajectory" in markup
    assert "?page=Inspector" in markup


def test_selected_page_marks_child_and_parent_active():
    markup = build_navigation_markup("Players")

    assert 'gridiron-nav-section active' in markup
    assert 'gridiron-nav-child active' in markup
    assert 'aria-current="page"' in markup


def test_navigation_uses_grouped_sections():
    markup = build_navigation_markup("Advisor")

    assert ">Fantasy<" in markup
    assert ">Operations<" in markup
    assert "?page=Advisor" in markup
    assert "?page=Ingestion" in markup


def test_child_navigation_stays_in_current_app_tab():
    markup = build_navigation_markup("Dashboard")

    assert 'target="_self"' in markup
    assert 'target="_blank"' not in markup
