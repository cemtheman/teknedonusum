from datetime import date
from pathlib import Path

import pytest

from calculations.phase1_journey_demand_analysis import (
  summarize_phase1_journey_demand,
)
from models.phase1_journey_demand import JourneyDemandPeriod
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)
from ui.journey_demand_dashboard import (
  build_journey_demand_chart_data,
  build_journey_demand_period_table,
)


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
INPUTS_SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")
DASHBOARD_SOURCE = Path(
  "ui/journey_demand_dashboard.py"
).read_text(encoding="utf-8")


def _period(index, **overrides):
  values = {
    "journey_demand_id": f"YD-2025-{index:02d}",
    "period_label": f"Dönem {index}",
    "route_id": "ROTA-DALYAN-IZTUZU",
    "route_name": "Dalyan–İztuzu",
    "period_start": date(2025, index, 1),
    "period_end": date(2025, index, 10),
    "round_trip_passenger_demand": index * 1000,
    "peak_factor": 1.25,
    "input_basis": InputBasis.ASSUMED,
    "verification_status": (
      VerificationStatus.REQUIRES_FIELD_VERIFICATION
    ),
  }
  values.update(overrides)
  return JourneyDemandPeriod(**values)


def test_period_table_exposes_auditable_demand_columns():
  table = build_journey_demand_period_table((_period(4),))

  assert list(table.columns) == [
    "Dönem ID",
    "Dönem",
    "Rota",
    "Başlangıç",
    "Bitiş",
    "Gün",
    "Gidiş-Dönüş Yolcu",
    "Tek Yön Yolcu Bacağı",
    "Günlük Ortalama",
    "Pik Katsayısı",
    "Pik Günlük Talep",
    "Talep Dayanağı",
    "Veri Durumu",
  ]


def test_period_table_preserves_raw_and_derived_values():
  table = build_journey_demand_period_table((_period(4),))

  assert table.loc[0, "Dönem ID"] == "YD-2025-04"
  assert table.loc[0, "Gidiş-Dönüş Yolcu"] == 4000
  assert table.loc[0, "Tek Yön Yolcu Bacağı"] == 8000
  assert table.loc[0, "Gün"] == 10
  assert table.loc[0, "Günlük Ortalama"] == pytest.approx(400.0)
  assert table.loc[0, "Pik Günlük Talep"] == 500


def test_period_table_uses_turkish_basis_and_status_labels():
  table = build_journey_demand_period_table((_period(4),))

  assert table.loc[0, "Talep Dayanağı"] == "Varsayılan"
  assert (
    table.loc[0, "Veri Durumu"]
    == "Saha doğrulaması gerekli"
  )


def test_chart_data_filters_route_and_sorts_chronologically():
  periods = (
    _period(6),
    _period(
      4,
      journey_demand_id="YD-OTHER-04",
      route_id="ROTA-OTHER",
      route_name="Diğer Rota",
    ),
    _period(4),
    _period(5),
  )

  chart = build_journey_demand_chart_data(
    periods,
    "ROTA-DALYAN-IZTUZU",
  )

  assert chart["Dönem"].tolist() == [
    "Dönem 4",
    "Dönem 5",
    "Dönem 6",
  ]
  assert chart["Gidiş-Dönüş Yolcu"].tolist() == [
    4000,
    5000,
    6000,
  ]


def test_chart_data_keeps_schema_when_route_has_no_records():
  chart = build_journey_demand_chart_data(
    (_period(4),),
    "ROTA-UNKNOWN",
  )

  assert chart.empty
  assert list(chart.columns) == [
    "Dönem",
    "Gidiş-Dönüş Yolcu",
  ]


def test_sidebar_exposes_collapsed_journey_demand_uploader():
  assert "🧭 Dönemsel Yolculuk Talebi" in INPUTS_SOURCE
  assert 'expanded=False' in INPUTS_SOURCE
  assert '"Yolculuk Talebi (.xlsx)"' in INPUTS_SOURCE
  assert 'key="journey_demand_excel"' in INPUTS_SOURCE


def test_sidebar_clears_stale_journey_demand_state():
  assert "if journey_demand_file is None:" in INPUTS_SOURCE
  assert '"journey_demand_periods"' in INPUTS_SOURCE
  assert '"journey_demand_summaries"' in INPUTS_SOURCE
  assert '] = None' in INPUTS_SOURCE


def test_sidebar_loads_summarizes_and_persists_valid_workbook():
  assert (
    "load_phase1_mockup_journey_demand_excel("
    in INPUTS_SOURCE
  )
  assert "summarize_phase1_journey_demand(" in INPUTS_SOURCE
  assert (
    'st.session_state["journey_demand_periods"]'
    in INPUTS_SOURCE
  )
  assert (
    'st.session_state["journey_demand_summaries"]'
    in INPUTS_SOURCE
  )


def test_sidebar_reports_invalid_workbook_without_stopping_app():
  assert "Yolculuk talebi analiz edilemedi:" in INPUTS_SOURCE
  journey_block = INPUTS_SOURCE.split(
    '"🧭 Dönemsel Yolculuk Talebi"',
    1,
  )[1].split(
    'with st.expander("⚓ Operasyon Profili"',
    1,
  )[0]
  assert "st.error(" in journey_block
  assert "st.stop()" not in journey_block


def test_app_renders_journey_demand_before_remote_solar_fetch():
  dashboard_pos = APP_SOURCE.index(
    "render_journey_demand_dashboard("
  )
  solar_fetch_pos = APP_SOURCE.index(
    "fetch_pvgis_hourly_specific_pv("
  )

  assert dashboard_pos < solar_fetch_pos


def test_ui_change_does_not_restore_main_brand_header():
  assert "render_brand_header" not in APP_SOURCE
  assert 'page_title="Sessiz Akım"' in APP_SOURCE


def test_dashboard_contains_summary_chart_and_detail_sections():
  for label in (
    "🧭 Dönemsel Yolculuk Talebi",
    "Dönem / Hizmet Günü",
    "Gidiş-Dönüş Yolcu",
    "Tek Yön Yolcu Bacağı",
    "Günlük Ortalama",
    "Pik Günlük Talep",
    "Dönemsel Talep Dağılımı",
    "Dönem kayıtları",
  ):
    assert label in DASHBOARD_SOURCE


def test_dashboard_uses_compact_custom_cards():
  assert "def _demand_metric_card(" in DASHBOARD_SOURCE
  assert "border-radius:12px" in DASHBOARD_SOURCE
  assert "st.columns(3)" in DASHBOARD_SOURCE
  assert "st.metric(" not in DASHBOARD_SOURCE


def test_dashboard_is_independent_from_fleet_and_energy_calculation():
  for forbidden_import in (
    "calculate_fleet",
    "build_vessel_specs",
    "fleet_inventory_analysis",
    "phase1_dataset",
  ):
    assert forbidden_import not in DASHBOARD_SOURCE


def test_dashboard_states_non_decision_scope_explicitly():
  for phrase in (
    "sefer sayısı",
    "tekne kapasitesi",
    "filo ataması",
    "enerji ihtiyacı",
    "altyapı yeterliliği",
  ):
    assert phrase in DASHBOARD_SOURCE


def test_dashboard_uses_validated_summary_contract():
  periods = (_period(4), _period(5))
  summary = summarize_phase1_journey_demand(periods)[0]

  assert summary.total_round_trip_passenger_demand == 9000
  assert summary.total_passenger_leg_demand == 18000
  assert summary.total_service_days == 20
