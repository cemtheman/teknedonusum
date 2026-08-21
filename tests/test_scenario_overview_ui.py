from datetime import date
from pathlib import Path

from models.inputs import SimulationInputs
from ui.scenario_overview import build_scenario_summary


def inputs():
  return SimulationInputs(
      count_v1=1,
      count_v2=2,
      count_v3=3,
      count_v4_24=4,
      count_v4_32=5,
      cost_eur_v1=100000,
      cost_eur_v2=120000,
      cost_eur_v3=140000,
      eur_rate=50.25,
      diesel_price=55.75,
      elec_price=4.25,
      operating_days=183,
      daily_miles=35.0,
      cruise_speed=5.5,
      location_name="Köyceğiz",
      latitude=36.97,
      longitude=28.69,
      season_start=date(2026, 4, 1),
      season_end=date(2026, 9, 30),
      season_days=183,
      average_daily_specific_yield_kwh_per_kwp=5.42,
      season_specific_yield_kwh_per_kwp=991.86,
      solar_resource_source="PVGIS",
  )


def test_scenario_summary_exposes_decision_inputs_without_fleet_counts():
  summary = build_scenario_summary(inputs())

  assert summary == {
      "Hizmet hızı": "5,5 kn",
      "Günlük rota": "35,0 NM",
      "Sezon": "183 gün",
      "PVGIS ort. özgül üretim": "5,42 kWh/kWp-gün",
      "Liman elektriği": "4,25 TL/kWh",
      "Dizel": "55,75 TL/L",
      "EUR / TRY": "50,25",
  }


def test_scenario_overview_contains_map_and_location_context():
  source = Path("ui/scenario_overview.py").read_text(encoding="utf-8")

  assert 'st.subheader("🧭 Senaryo ve Lokasyon Özeti")' in source
  assert "st.map(" in source
  assert '"lat": [float(inputs.latitude)]' in source
  assert '"lon": [float(inputs.longitude)]' in source
  assert "Anahtar Senaryo Girdileri" in source


def test_app_renders_scenario_overview_before_fleet_dashboard():
  source = Path("app.py").read_text(encoding="utf-8")

  overview_position = source.index("render_scenario_overview(inputs)")
  fleet_position = source.index("render_fleet_dashboard(vessel_specs, inputs, fleet)")

  assert overview_position < fleet_position
