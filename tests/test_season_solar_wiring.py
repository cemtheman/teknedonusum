from pathlib import Path


INPUTS_SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")
APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
DASHBOARD_SOURCE = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")


def test_sidebar_uses_location_and_date_defined_solar_season():
  assert '"Lokasyon"' in INPUTS_SOURCE
  assert '"Enlem"' in INPUTS_SOURCE
  assert '"Boylam"' in INPUTS_SOURCE
  assert '"Sezon Başlangıcı"' in INPUTS_SOURCE
  assert '"Sezon Bitişi"' in INPUTS_SOURCE
  assert "build_season_solar_resource(" in INPUTS_SOURCE


def test_sidebar_no_longer_exposes_manual_sun_hours_or_season_length():
  assert '"Günlük Güneşlenme Süresi (Saat/Gün)"' not in INPUTS_SOURCE
  assert '"Sezon Operasyon Gün Sayısı"' not in INPUTS_SOURCE
  assert '"Sezonluk planlanan operasyon / rota günü"' not in INPUTS_SOURCE
  assert '"Sezon Süresi (gün)"' in INPUTS_SOURCE
  assert "operating_days = season_days" in INPUTS_SOURCE


def test_primary_app_passes_pvgis_specific_yield_to_fleet():
  assert "average_daily_specific_yield_kwh_per_kwp=(" in APP_SOURCE
  assert "inputs.average_daily_specific_yield_kwh_per_kwp" in APP_SOURCE


def test_dashboard_reports_location_dates_and_pvgis_yield():
  assert "inputs.location_name" in DASHBOARD_SOURCE
  assert "inputs.season_start" in DASHBOARD_SOURCE
  assert "inputs.season_end" in DASHBOARD_SOURCE
  assert "inputs.average_daily_specific_yield_kwh_per_kwp" in DASHBOARD_SOURCE
  assert "Saat/Gün Güneşlenme" not in DASHBOARD_SOURCE
