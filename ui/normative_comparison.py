"""Streamlit presentation for same-speed normative vessel comparison."""

import pandas as pd
import streamlit as st

from calculations.normative_comparison_export import (
    build_normative_comparison_csv,
    build_normative_comparison_xlsx,
)
from calculations.normative_vessel_comparison import (
    build_normative_vessel_comparison,
)
from models.normative_vessel_comparison import NormativeVesselComparisonResult
from ui.formatting import format_integer_tr


def _format_decimal_tr(value):
  return f"{value:.1f}".replace(".", ",")


def _speed_filename_token(selected_speed_knots):
  return f"{selected_speed_knots:g}".replace(".", "_")


def build_normative_comparison_table(comparison):
  """Format only the contract's reference values for on-screen display."""
  if not isinstance(comparison, NormativeVesselComparisonResult):
    raise TypeError("comparison must be a NormativeVesselComparisonResult")
  return pd.DataFrame([
      {
          "Tekne": f"{row.vessel_id.upper()} — {row.vessel_type}",
          "Yolcu kapasitesi": row.passenger_capacity,
          "Toplam kurulu mekanik güç": (
              f"{_format_decimal_tr(row.reference_installed_mechanical_power_kw)} "
              "kW"
          ),
          "Günlük enerji": (
              f"{_format_decimal_tr(row.reference_daily_propulsion_energy_kwh)} "
              "kWh/gün"
          ),
          "Nominal batarya": (
              f"{_format_decimal_tr(row.reference_nominal_battery_capacity_kwh)} "
              "kWh"
          ),
          "Motor + batarya maliyeti": (
              f"€{format_integer_tr(row.reference_propulsion_system_cost)}"
          ),
      }
      for row in comparison.rows
  ])


def render_normative_comparison_section(selected_speed_knots):
  """Render comparison and downloads from one immutable result."""
  st.divider()
  st.subheader("⚖️ Normatif Tekne Karşılaştırması")
  st.caption(
      "V1/V2/V3 aynı seçilmiş hizmet hızında ve aynı normatif semantik altında "
      "karşılaştırılır; sıralama veya tekne önerisi üretilmez."
  )
  try:
    comparison = build_normative_vessel_comparison(selected_speed_knots)
  except (TypeError, ValueError):
    st.error(
        "Normatif tekne karşılaştırması hazırlanamadı. Hizmet hızı 6–10 knot "
        "aralığında olmalıdır."
    )
    return None

  st.write(
      f"Ortak hizmet hızı: {_format_decimal_tr(selected_speed_knots)} kn"
  )
  st.dataframe(
      build_normative_comparison_table(comparison),
      hide_index=True,
      width="stretch",
  )

  speed_token = _speed_filename_token(selected_speed_knots)
  st.download_button(
      "📥 Normatif karşılaştırmayı XLSX indir",
      data=build_normative_comparison_xlsx(comparison),
      file_name=(
          f"sessiz_akim_normatif_karsilastirma_{speed_token}_kn.xlsx"
      ),
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
  st.download_button(
      "📥 Normatif karşılaştırmayı CSV indir",
      data=build_normative_comparison_csv(comparison),
      file_name=f"sessiz_akim_normatif_karsilastirma_{speed_token}_kn.csv",
      mime="text/csv",
  )
  return comparison
