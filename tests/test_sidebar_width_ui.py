from pathlib import Path


SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_sidebar_has_explicit_compact_width():
  assert 'section[data-testid="stSidebar"]' in SOURCE
  assert "width: 300px !important" in SOURCE
  assert "min-width: 300px !important" in SOURCE
  assert "max-width: 300px !important" in SOURCE


def test_sidebar_inner_container_matches_width():
  assert 'section[data-testid="stSidebar"] > div' in SOURCE


def test_sidebar_css_is_rendered_from_sidebar_branding():
  assert "def render_sidebar_brand():" in SOURCE
  assert "unsafe_allow_html=True" in SOURCE
