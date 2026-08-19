"""Streamlit presentation for the preliminary vessel technical comparison."""

import pandas as pd
import streamlit as st

from calculations.vessel_comparison import VesselTechnicalComparisonRow
from models.compliance import ComplianceStatus


STATUS_LABELS = {
    ComplianceStatus.PASS: "Uygun",
    ComplianceStatus.FAIL: "Uygun değil",
    None: "Henüz değerlendirilmedi",
}

ESTIMATE_BASIS_LABELS = {
    "preliminary_technical_scenario": "Ön teknik senaryo",
    "calibrated_preliminary": "Kalibre ön tahmin",
}

HULL_TYPE_LABELS = {
    "monohull": "Tek gövdeli",
    "catamaran": "Katamaran",
}


def _format_decimal(value):
  if value is None:
    return "Mevcut değil"
  return f"{value:.1f}".replace(".", ",")


def build_vessel_comparison_table(rows):
  """Convert structured comparison rows into management-facing table data."""
  rows = tuple(rows)
  if any(not isinstance(row, VesselTechnicalComparisonRow) for row in rows):
    raise TypeError("rows must contain VesselTechnicalComparisonRow values")

  return pd.DataFrame([
      {
          "Tekne tipi": (
              f"{row.vessel_id.upper()} — {row.vessel_name.split(' (', 1)[0]}"
          ),
          "Gövde tipi": HULL_TYPE_LABELS.get(row.hull_type, row.hull_type),
          "Yolcu kapasitesi": row.passenger_capacity,
          "Seçilen hız (knot)": _format_decimal(
              row.selected_cruise_speed_knots
          ),
          "Batarya kapasitesi (kWh)": _format_decimal(
              row.battery_capacity_kwh
          ),
          "Seyir gücü (kW)": _format_decimal(
              row.calculated_cruise_power_kw
          ),
          "Günlük sevk enerjisi (kWh)": _format_decimal(
              row.daily_propulsion_energy_kwh
          ),
          "Güneş katkısı (kWh/gün)": _format_decimal(
              row.solar_energy_contribution_kwh
          ),
          "Net şebeke ihtiyacı (kWh/gün)": _format_decimal(
              row.net_grid_energy_requirement_kwh
          ),
          "Tahmini menzil (NM)": _format_decimal(
              row.estimated_navigation_range_nm
          ),
          "Teknik uygunluk": STATUS_LABELS[
              row.commission_compliance_status
          ],
          "Tahmin dayanağı": ESTIMATE_BASIS_LABELS[row.estimate_basis],
      }
      for row in rows
  ])


def render_vessel_technical_comparison(rows) -> None:
  """Render the existing comparison model without recalculating its values."""
  table = build_vessel_comparison_table(rows)

  st.divider()
  with st.expander(
      "📋 Teknik karşılaştırma detaylarını göster",
      expanded=False,
  ):
    st.caption(
        "v1 ile v2/v3 farklı teknik hesap derinliği kullanır. Tam teknik "
        "uygunluk, doğrulanmış hız kabiliyeti dahil tüm kriterler "
        "değerlendirildiğinde belirlenebilir."
    )
    st.dataframe(table, hide_index=True, use_container_width=True)
