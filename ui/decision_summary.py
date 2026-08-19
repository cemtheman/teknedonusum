"""Management-facing Streamlit table for integrated vessel decisions."""

import pandas as pd
import streamlit as st

from calculations.decision_summary import VesselDecisionSummaryRow
from ui.vessel_comparison import STATUS_LABELS


def _format_decimal(value):
  if value is None:
    return "Mevcut değil"
  return f"{value:.1f}".replace(".", ",")


def _format_tl(value):
  grouped = f"{value:,.0f}"
  return "₺" + grouped.replace(",", ".")


def build_decision_summary_table(rows):
  rows = tuple(rows)
  if any(not isinstance(row, VesselDecisionSummaryRow) for row in rows):
    raise TypeError("rows must contain VesselDecisionSummaryRow values")

  return pd.DataFrame([
      {
          "Tekne tipi": (
              f"{row.vessel_id.upper()} — {row.vessel_name.split(' (', 1)[0]}"
          ),
          "Yolcu kapasitesi": row.passenger_capacity,
          "Seçilen hız (knot)": _format_decimal(
              row.selected_cruise_speed_knots
          ),
          "Batarya (kWh)": _format_decimal(row.battery_capacity_kwh),
          "Günlük enerji (kWh/gün)": _format_decimal(
              row.daily_energy_requirement_kwh
          ),
          "Güneş katkısı (kWh/gün)": _format_decimal(
              row.solar_energy_contribution_kwh
          ),
          "Net şebeke (kWh/gün)": _format_decimal(
              row.net_grid_energy_requirement_kwh
          ),
          "Tahmini menzil (NM)": _format_decimal(
              row.estimated_navigation_range_nm
          ),
          "Teknik uygunluk": STATUS_LABELS[
              row.commission_compliance_status
          ],
          "Yatırım maliyeti": _format_tl(row.investment_cost_tl),
          "Hibe": _format_tl(row.grant_amount_tl),
          "Net yatırım": _format_tl(row.net_investment_tl),
          "Yıllık işletme tasarrufu": _format_tl(
              row.annual_operating_saving_tl
          ),
          "Geri ödeme (sezon)": _format_decimal(
              row.simple_payback_seasons
          ),
          "CO₂ azaltımı (ton/yıl)": _format_decimal(
              row.annual_co2_reduction_t
          ),
      }
      for row in rows
  ])


def render_vessel_decision_summary(rows) -> None:
  table = build_decision_summary_table(rows)

  st.divider()
  st.subheader("📊 Tekne Alternatifleri Karar Özeti")
  st.caption(
      "Sonuçlar ön karar-destek tahminleridir; v1 ile v2/v3 şu aşamada "
      "farklı teknik hesap derinliği kullanır."
  )
  st.dataframe(table, hide_index=True, use_container_width=True)
