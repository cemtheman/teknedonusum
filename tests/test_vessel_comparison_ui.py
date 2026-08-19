from unittest.mock import MagicMock

import pytest

from calculations.vessel_comparison import VesselTechnicalComparisonRow
from ui import vessel_comparison as vessel_comparison_ui


def comparison_rows():
  shared = {
      "hull_type": "catamaran",
      "selected_cruise_speed_knots": 6.0,
      "calculated_cruise_power_kw": 7.452997,
      "daily_propulsion_energy_kwh": 43.475817,
      "solar_energy_contribution_kwh": 54.432,
      "net_grid_energy_requirement_kwh": 0.0,
      "estimated_navigation_range_nm": None,
      "commission_compliance_status": None,
      "estimate_basis": "calibrated_preliminary",
  }
  return (
      VesselTechnicalComparisonRow(
          vessel_id="v1",
          vessel_name="Tip 1",
          hull_type="monohull",
          passenger_capacity=24,
          selected_cruise_speed_knots=10.0,
          battery_capacity_kwh=80.0,
          calculated_cruise_power_kw=23.728117,
          daily_propulsion_energy_kwh=83.048409,
          solar_energy_contribution_kwh=25.17768,
          net_grid_energy_requirement_kwh=63.120729,
          estimated_navigation_range_nm=22.831668,
          commission_compliance_status=None,
          estimate_basis="preliminary_technical_scenario",
      ),
      VesselTechnicalComparisonRow(
          vessel_id="v2",
          vessel_name="Tip 2",
          passenger_capacity=32,
          battery_capacity_kwh=100.0,
          **shared,
      ),
      VesselTechnicalComparisonRow(
          vessel_id="v3",
          vessel_name="Tip 3",
          passenger_capacity=54,
          battery_capacity_kwh=140.0,
          **shared,
      ),
  )


def test_table_formats_three_rows_statuses_basis_and_unavailable_values():
  table = vessel_comparison_ui.build_vessel_comparison_table(comparison_rows())

  assert len(table) == 3
  assert list(table["Teknik uygunluk"]) == [
      "Henüz değerlendirilmedi",
      "Henüz değerlendirilmedi",
      "Henüz değerlendirilmedi",
  ]
  assert list(table["Tahmin dayanağı"]) == [
      "Ön teknik senaryo",
      "Kalibre ön tahmin",
      "Kalibre ön tahmin",
  ]
  assert table.loc[1, "Tahmini menzil (NM)"] == "Mevcut değil"
  assert table.loc[2, "Tahmini menzil (NM)"] == "Mevcut değil"


def test_table_numeric_formatting_is_compact_and_turkish():
  table = vessel_comparison_ui.build_vessel_comparison_table(comparison_rows())

  assert table.loc[0, "Seçilen hız (knot)"] == "10,0"
  assert table.loc[0, "Batarya kapasitesi (kWh)"] == "80,0"
  assert table.loc[0, "Seyir gücü (kW)"] == "23,7"
  assert table.loc[0, "Günlük sevk enerjisi (kWh)"] == "83,0"
  assert table.loc[0, "Güneş katkısı (kWh/gün)"] == "25,2"
  assert table.loc[0, "Net şebeke ihtiyacı (kWh/gün)"] == "63,1"
  assert table.loc[0, "Tahmini menzil (NM)"] == "22,8"


def test_renderer_displays_exactly_three_rows(monkeypatch):
  streamlit = MagicMock()
  monkeypatch.setattr(vessel_comparison_ui, "st", streamlit)

  vessel_comparison_ui.render_vessel_technical_comparison(comparison_rows())

  rendered_table = streamlit.dataframe.call_args.args[0]
  assert len(rendered_table) == 3
  streamlit.dataframe.assert_called_once_with(
      rendered_table,
      hide_index=True,
      use_container_width=True,
  )
  streamlit.subheader.assert_called_once_with(
      "📋 Tekne Tipleri Teknik Karşılaştırması"
  )
  streamlit.caption.assert_called_once_with(
      "v1 ile v2/v3 şu aşamada aynı teknik hesap derinliğini kullanmaz. "
      "Tablo ön karşılaştırma içindir; doğrulanmış tekne performansı değildir. "
      "Tam teknik uygunluk, doğrulanmış tekne hız kabiliyeti dahil tüm "
      "kriterler değerlendirildiğinde belirlenebilir."
  )


def test_table_rejects_wrong_row_type():
  with pytest.raises(
      TypeError,
      match="rows must contain VesselTechnicalComparisonRow values",
  ):
    vessel_comparison_ui.build_vessel_comparison_table([object()])
