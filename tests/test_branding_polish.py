from pathlib import Path


SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_main_brand_titles_have_equal_visual_weight():
  assert "font-size:2rem;font-weight:750;color:#0A2B55" in SOURCE
  assert "font-size:2rem;font-weight:750;color:#2E7D57" in SOURCE
  assert "Quiet Current" in SOURCE


def test_sidebar_logo_is_centered_with_columns():
  assert "left, logo_col, right = st.columns([1, 2, 1])" in SOURCE
  assert "with logo_col:" in SOURCE
  assert "use_container_width=True" in SOURCE
