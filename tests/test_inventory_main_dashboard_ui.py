from pathlib import Path

from calculations.fleet_inventory_analysis import (
    InventoryVessel,
    analyze_inventory,
)
from ui.fleet_inventory_dashboard import build_inventory_decision_table


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
INPUTS_SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")
DASHBOARD_SOURCE = Path(
    "ui/fleet_inventory_dashboard.py"
).read_text(encoding="utf-8")


def _analysis():
  return analyze_inventory([
      InventoryVessel(
          1,
          "Martı",
          "Ali",
          "Yolcu Motoru",
          11.5,
          3.5,
      ),
      InventoryVessel(
          2,
          "Ada",
          "Ayşe",
          "Özel Tekne",
          7.0,
          2.4,
      ),
  ])


def test_sidebar_persists_inventory_analysis_in_session_state():
  assert (
      'st.session_state["fleet_inventory_analysis"] = inventory_analysis'
      in INPUTS_SOURCE
  )
  assert (
      'st.session_state["fleet_inventory_plan_active"]'
      in INPUTS_SOURCE
  )


def test_sidebar_clears_stale_inventory_when_file_is_removed():
  assert 'if inventory_file is None:' in INPUTS_SOURCE
  assert (
      'st.session_state["fleet_inventory_analysis"] = None'
      in INPUTS_SOURCE
  )


def test_app_renders_inventory_dashboard_before_fleet_dashboard():
  inventory_pos = APP_SOURCE.index(
      "render_fleet_inventory_dashboard("
  )
  fleet_pos = APP_SOURCE.index(
      "render_fleet_dashboard("
  )

  assert inventory_pos < fleet_pos


def test_inventory_dashboard_contains_expected_sections():
  for label in (
      "📊 Envanter Dönüşüm Analizi",
      "Faz 1 Hedef Filo Dağılımı",
      "Faz 1 Finansman İhtiyacı",
      "Tekne Bazlı Dönüşüm Kararları",
      "Toplam Hedef Yatırım",
      "Toplam Hibe İhtiyacı",
      "Toplam Özkaynak İhtiyacı",
  ):
    assert label in DASHBOARD_SOURCE


def test_inventory_dashboard_financing_scope_is_explicit():
  assert (
      "Bu finansman özeti yalnız Faz 1 hedef filosunu kapsar."
      in DASHBOARD_SOURCE
  )
  assert (
      "Faz 2 hibrit tekneler ile Faz 3 özel tekneler"
      in DASHBOARD_SOURCE
  )


def test_decision_table_exposes_vessel_level_recommendation():
  table = build_inventory_decision_table(_analysis())

  assert list(table.columns) == [
      "Tekne Adı",
      "Donatanı",
      "Tekne Cinsi",
      "Boyu (m)",
      "Eni (m)",
      "Dönüşüm Fazı",
      "Önerilen Tahrik",
      "Karar Durumu",
      "Hibe Yaklaşımı",
      "Karar Gerekçesi",
  ]

  assert table.loc[0, "Tekne Adı"] == "Martı"
  assert table.loc[0, "Dönüşüm Fazı"] == "Faz 1"
  assert table.loc[1, "Dönüşüm Fazı"] == "Faz 3"


def test_inventory_dashboard_has_phase_and_type_filters():
  assert 'st.selectbox(' in DASHBOARD_SOURCE
  assert '"Dönüşüm fazı"' in DASHBOARD_SOURCE
  assert 'st.multiselect(' in DASHBOARD_SOURCE
  assert '"Tekne cinsi"' in DASHBOARD_SOURCE
