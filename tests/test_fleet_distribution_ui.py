from datetime import date
from pathlib import Path

from models.inputs import SimulationInputs
from ui.fleet_dashboard import (
    build_fleet_distribution_chart_data,
    build_fleet_type_summary,
)


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
      eur_rate=50.0,
      diesel_price=55.0,
      elec_price=3.5,
      operating_days=183,
      daily_miles=35.0,
      cruise_speed=6.0,
      location_name="Köyceğiz",
      latitude=36.97,
      longitude=28.69,
      season_start=date(2026, 4, 1),
      season_end=date(2026, 9, 30),
      season_days=183,
      average_daily_specific_yield_kwh_per_kwp=5.4,
      season_specific_yield_kwh_per_kwp=988.2,
      solar_resource_source="PVGIS",
  )


def test_distribution_groups_and_colors():
  data = build_fleet_distribution_chart_data(inputs())
  assert list(data["Kod"]) == ["K1", "K2", "K3", "D1", "D2"]
  assert list(data["Adet"]) == [50, 50, 40, 30, 20]
  assert list(data["Renk"]) == [
      "#0F766E",
      "#22C55E",
      "#F59E0B",
      "#2563EB",
      "#7C3AED",
  ]


def test_type_summary_merges_matching_vessel_types():
  summary = build_fleet_type_summary(inputs())
  assert list(summary["Toplam"]) == [80, 70, 40]
  assert list(summary["Kooperatif"]) == [50, 50, 40]
  assert list(summary["Kooperatif Dışı"]) == [30, 20, 0]




def test_summary_table_html_is_renderable_not_markdown_code():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")
  assert 'return "".join(html)' in source
  assert '<table style=' in source



def test_donut_is_svg_with_center_total_and_stable_labels():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")
  assert "def _fleet_donut_svg(" in source
  assert "Toplam Tekne" in source
  assert "stroke-dasharray" in source
  assert "st.vega_lite_chart(" not in source


def test_summary_uses_distinct_svg_vessel_icons():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")
  assert 'kind == "monohull"' in source
  assert 'kind == "catamaran_32"' in source
  assert "catamaran_54" in source
  assert "<svg viewBox=" in source

def test_final_fleet_dashboard_visual_contract_svg():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")

  assert "_render_fleet_top_kpis" in source
  assert "_render_fleet_donut" in source
  assert "_render_fleet_legend" in source
  assert "_summary_table_html" in source
  assert "_render_membership_kpis" in source
  assert "Grafik Anahtarı" in source
  assert "Tekne Tiplerine Göre Özet" in source

  assert "def _fleet_donut_svg(" in source
  assert "stroke-dasharray" in source
  assert "Toplam Tekne" in source
  assert "st.vega_lite_chart(" not in source


def test_summary_table_uses_distinct_svg_vessel_icons():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")

  assert 'kind == "monohull"' in source
  assert 'kind == "catamaran_32"' in source
  assert "catamaran_54" in source
  assert "<svg viewBox=" in source
  assert "width:52px;height:38px;border-radius:9px" in source
