from pathlib import Path


APP = Path("app.py").read_text(encoding="utf-8")


def test_app_fetches_and_builds_typical_hourly_pvgis_profile():
  assert "fetch_pvgis_hourly_specific_pv(" in APP
  assert "build_typical_hourly_profile(" in APP


def test_app_passes_season_and_hourly_profile_to_fleet():
  assert "season_start=inputs.season_start" in APP
  assert "season_end=inputs.season_end" in APP
  assert "typical_hourly_specific_pv=typical_hourly_specific_pv" in APP
