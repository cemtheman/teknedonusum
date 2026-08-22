from pathlib import Path


SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_sidebar_geometry_is_left_to_streamlit():
  assert "width: 330px !important" not in SOURCE
  assert "min-width: 330px !important" not in SOURCE
  assert "max-width: 330px !important" not in SOURCE

  assert "width: 300px !important" not in SOURCE
  assert "min-width: 300px !important" not in SOURCE
  assert "max-width: 300px !important" not in SOURCE


def test_sidebar_does_not_override_mobile_width():
  assert "width: initial !important" not in SOURCE
  assert "min-width: initial !important" not in SOURCE
  assert "max-width: initial !important" not in SOURCE


def test_mobile_horizontal_overflow_guard_remains():
  assert "@media (max-width: 768px)" in SOURCE
  assert '[data-testid="stAppViewContainer"]' in SOURCE
  assert "max-width: 100vw" in SOURCE
  assert "overflow-x: hidden" in SOURCE


def test_sidebar_contract_documents_native_geometry():
  assert (
      "Sidebar geometry is intentionally left to Streamlit."
      in SOURCE
  )
