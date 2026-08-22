from pathlib import Path


SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_sidebar_has_compact_but_readable_width():
  assert 'section[data-testid="stSidebar"]' in SOURCE
  assert "width: 330px !important" in SOURCE
  assert "min-width: 330px !important" in SOURCE
  assert "max-width: 330px !important" in SOURCE


def test_sidebar_inner_container_matches_width():
  assert 'section[data-testid="stSidebar"] > div' in SOURCE
