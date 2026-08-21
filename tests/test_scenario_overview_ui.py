from datetime import date
from pathlib import Path

from models.inputs import SimulationInputs
from ui.scenario_overview import build_scenario_summary


SOURCE = Path("ui/scenario_overview.py").read_text(encoding="utf-8")


def inputs():
  return SimulationInputs(
      count_v1=50,
      count_v2=50,
      count_v3=40,
      count_v4_24=30,
      count_v4_32=20,
      cost_eur_v1=108100,
      cost_eur_v2=144140,
      cost_eur_v3=180180,
      eur_rate=56.12,
      diesel_price=84.60,
      elec_price=3.50,
      operating_days=183,
      daily_miles=35.0,
      cruise_speed=6.0,
      location_name="Dalyan, Ortaca, Muğla, Türkiye",
      latitude=36.8344,
      longitude=28.6439,
      season_start=date(2026, 4, 1),
      season_end=date(2026, 9, 30),
      season_days=183,
      average_daily_specific_yield_kwh_per_kwp=5.50,
      season_specific_yield_kwh_per_kwp=1006.5,
      solar_resource_source="PVGIS",
  )


def test_scenario_summary_preserves_core_values():
  summary = build_scenario_summary(inputs())

  assert summary["Hizmet hızı"] == "6,0 kn"
  assert summary["Günlük rota"] == "35,0 deniz mili"
  assert summary["Sezon"] == "183 gün"
  assert summary["Liman elektriği"] == "3,50 TL/kWh"
  assert summary["Dizel"] == "84,60 TL/L"
  assert summary["EUR / TRY"] == "56,12"


def test_scenario_overview_uses_compact_visual_cards():
  assert "def _scenario_metric_card(" in SOURCE
  assert "def _location_badge(" in SOURCE
  assert "border-radius:12px" in SOURCE
  assert "border-radius:999px" in SOURCE


def test_scenario_map_is_compact_and_summary_is_wider():
  assert 'st.columns(\n      [0.92, 1.08],' in SOURCE
  assert 'height=225' in SOURCE
  assert 'zoom=12' in SOURCE


def test_summary_uses_cards_instead_of_streamlit_metrics():
  assert "st.metric(" not in SOURCE
  assert "_scenario_metric_card(label, value)" in SOURCE
