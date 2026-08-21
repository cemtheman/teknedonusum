from pathlib import Path


SOURCE = Path("app.py").read_text(encoding="utf-8")


def test_app_passes_hourly_profile_to_vessel_details():
  assert "render_vessel_details(" in SOURCE
  assert "typical_hourly_specific_pv=typical_hourly_specific_pv" in SOURCE
