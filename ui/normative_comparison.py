"""Compact same-speed comparison of the three active vessel types."""

import pandas as pd
import streamlit as st

from calculations.normative_vessel_comparison import (
    build_normative_vessel_comparison,
)
from models.normative_vessel_comparison import NormativeVesselComparisonResult
from ui.formatting import format_integer_tr


VESSEL_LABELS = {
    "v1": "Tip 1 — 12 m Tek Gövdeli",
    "v2": "Tip 2 — 13,5 m Katamaran",
    "v3": "Tip 3 — 14 m Katamaran",
}


def _format_decimal_tr(value):
  return f"{value:.1f}".replace(".", ",")


def build_normative_comparison_table(comparison, vessel_specs):
  if not isinstance(comparison, NormativeVesselComparisonResult):
    raise TypeError("comparison must be a NormativeVesselComparisonResult")

  return pd.DataFrame([
      {
          "Tekne tipi": VESSEL_LABELS[row.vessel_id],
          "Yolcu kapasitesi": row.passenger_capacity,
          "Toplam kurulu motor gücü": (
              f"{_format_decimal_tr(row.reference_installed_mechanical_power_kw)} kW"
          ),
          "Günlük tahrik enerjisi": (
              f"{_format_decimal_tr(row.reference_daily_propulsion_energy_kwh)} "
              "kWh/gün"
          ),
          "Gerekli nominal batarya": (
              f"{_format_decimal_tr(row.reference_nominal_battery_capacity_kwh)} kWh"
          ),
          "Anahtar teslim piyasa bedeli": (
              f"€{format_integer_tr(vessel_specs[row.vessel_id]['totalCostEur'])}"
          ),
      }
      for row in comparison.rows
  ])


def render_normative_comparison_section(
    vessel_specs,
    selected_speed_knots,
    daily_distance_nm=35.0,
):
  st.divider()
  st.subheader("⚖️ Tekne Tiplerinin Karşılaştırılması")
  st.caption(
      "Üç tekne tipi aynı hizmet hızı ve günlük rota koşullarında "
      "karşılaştırılmıştır. Piyasa bedelleri %8 ÖTV ve %20 KDV hariçtir."
  )

  try:
    comparison = build_normative_vessel_comparison(
        selected_speed_knots,
        daily_distance_nm,
    )
  except (TypeError, ValueError):
    st.error(
        "Tekne karşılaştırması hazırlanamadı. Hizmet hızı 5–10 knot "
        "aralığında olmalıdır."
    )
    return None

  st.dataframe(
      build_normative_comparison_table(comparison, vessel_specs),
      hide_index=True,
      width="stretch",
  )
  return comparison
