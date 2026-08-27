"""Dönemsel yolculuk talebi yükleme sonuçlarının ana ekran sunumu."""

from html import escape

import pandas as pd
import streamlit as st

from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)
from ui.formatting import format_integer_tr


INPUT_BASIS_LABELS = {
  InputBasis.MEASURED: "Ölçülen",
  InputBasis.DECLARED: "Beyan edilen",
  InputBasis.ASSUMED: "Varsayılan",
}

VERIFICATION_STATUS_LABELS = {
  VerificationStatus.SYNTHETIC: "Sentetik",
  VerificationStatus.REQUIRES_FIELD_VERIFICATION: (
    "Saha doğrulaması gerekli"
  ),
  VerificationStatus.FIELD_VERIFIED: "Saha doğrulandı",
}


def _format_decimal_tr(value, digits=2):
  rendered = f"{value:,.{digits}f}"
  return (
    rendered
    .replace(",", "_")
    .replace(".", ",")
    .replace("_", ".")
  )


def build_journey_demand_period_table(periods):
  """Dönem kayıtlarını kullanıcıya gösterilecek tabloya dönüştür."""

  rows = []

  for period in sorted(
    periods,
    key=lambda item: (
      item.route_id,
      item.period_start,
      item.period_end,
      item.journey_demand_id,
    ),
  ):
    rows.append({
      "Dönem ID": period.journey_demand_id,
      "Dönem": period.period_label,
      "Rota": period.route_name,
      "Başlangıç": period.period_start,
      "Bitiş": period.period_end,
      "Gün": period.service_days,
      "Gidiş-Dönüş Yolcu": (
        period.round_trip_passenger_demand
      ),
      "Tek Yön Yolcu Bacağı": period.passenger_leg_demand,
      "Günlük Ortalama": period.average_daily_round_trip,
      "Pik Katsayısı": period.peak_factor,
      "Pik Günlük Talep": period.peak_daily_round_trip,
      "Talep Dayanağı": INPUT_BASIS_LABELS[period.input_basis],
      "Veri Durumu": VERIFICATION_STATUS_LABELS[
        period.verification_status
      ],
    })

  return pd.DataFrame(
    rows,
    columns=[
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
    ],
  )


def build_journey_demand_chart_data(periods, route_id):
  """Seçilen rota için kronolojik aylık talep serisi oluştur."""

  rows = [
    {
      "Dönem": period.period_label,
      "Gidiş-Dönüş Yolcu": (
        period.round_trip_passenger_demand
      ),
    }
    for period in sorted(
      periods,
      key=lambda item: (
        item.period_start,
        item.period_end,
        item.journey_demand_id,
      ),
    )
    if period.route_id == route_id
  ]

  return pd.DataFrame(
    rows,
    columns=[
      "Dönem",
      "Gidiş-Dönüş Yolcu",
    ],
  )


def _demand_metric_card(label, value):
  st.markdown(
    f"""
    <div style="
      border:1px solid #dbe4ee;
      border-radius:12px;
      padding:0.9rem 1rem;
      min-height:88px;
      background:#ffffff;
    ">
      <div style="font-size:0.76rem;color:#64748b;font-weight:650;">
        {escape(str(label))}
      </div>
      <div style="font-size:1.28rem;color:#0f172a;font-weight:750;margin-top:0.3rem;">
        {escape(str(value))}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
  )


def _select_route_summary(summaries):
  if len(summaries) == 1:
    return summaries[0]

  labels = {
    f"{summary.route_name} · {summary.route_id}": summary
    for summary in summaries
  }
  selected_label = st.selectbox(
    "Rota",
    tuple(labels),
    key="journey_demand_dashboard_route",
  )
  return labels[selected_label]


def render_journey_demand_dashboard(periods, summaries):
  """Yüklenen dönemsel talebi karar üretmeden görselleştir."""

  if not periods or not summaries:
    return

  st.divider()
  st.subheader("🧭 Dönemsel Yolculuk Talebi")
  st.caption(
    "Yüklenen Excel, rota ve dönem bazında doğrulandı. "
    "Gösterilen değerler yolcu talebi özetidir."
  )

  summary = _select_route_summary(summaries)
  selected_periods = tuple(
    period
    for period in periods
    if period.route_id == summary.route_id
  )

  st.markdown(f"**{summary.route_name}**")

  season_col, period_col, demand_col = st.columns(3)

  with season_col:
    _demand_metric_card(
      "Sezon",
      (
        f"{summary.season_start:%d.%m.%Y}–"
        f"{summary.season_end:%d.%m.%Y}"
      ),
    )

  with period_col:
    _demand_metric_card(
      "Dönem / Hizmet Günü",
      f"{summary.period_count} / {summary.total_service_days}",
    )

  with demand_col:
    _demand_metric_card(
      "Gidiş-Dönüş Yolcu",
      format_integer_tr(
        summary.total_round_trip_passenger_demand
      ),
    )

  leg_col, average_col, peak_col = st.columns(3)

  with leg_col:
    _demand_metric_card(
      "Tek Yön Yolcu Bacağı",
      format_integer_tr(
        summary.total_passenger_leg_demand
      ),
    )

  with average_col:
    _demand_metric_card(
      "Günlük Ortalama",
      _format_decimal_tr(
        summary.average_daily_round_trip,
        2,
      ),
    )

  with peak_col:
    _demand_metric_card(
      "Pik Günlük Talep",
      format_integer_tr(summary.peak_daily_round_trip),
    )

  st.info(
    "En yüksek dönem: "
    f"{summary.highest_demand_period_label} · "
    f"{format_integer_tr(summary.highest_period_round_trip_passenger_demand)} "
    "gidiş-dönüş yolcu. "
    f"Pik günlük talep {summary.peak_daily_period_label} döneminde "
    f"{format_integer_tr(summary.peak_daily_round_trip)} yolcudur."
  )

  st.markdown("**Dönemsel Talep Dağılımı**")
  chart_data = build_journey_demand_chart_data(
    selected_periods,
    summary.route_id,
  )
  st.bar_chart(
    chart_data.set_index("Dönem"),
    use_container_width=True,
  )

  with st.expander("Dönem kayıtları", expanded=False):
    table = build_journey_demand_period_table(
      selected_periods
    )
    st.dataframe(
      table,
      hide_index=True,
      use_container_width=True,
      column_config={
        "Başlangıç": st.column_config.DateColumn(
          format="DD.MM.YYYY"
        ),
        "Bitiş": st.column_config.DateColumn(
          format="DD.MM.YYYY"
        ),
        "Gün": st.column_config.NumberColumn(
          format="%d"
        ),
        "Gidiş-Dönüş Yolcu": st.column_config.NumberColumn(
          format="%d"
        ),
        "Tek Yön Yolcu Bacağı": st.column_config.NumberColumn(
          format="%d"
        ),
        "Günlük Ortalama": st.column_config.NumberColumn(
          format="%.2f"
        ),
        "Pik Katsayısı": st.column_config.NumberColumn(
          format="%.2f"
        ),
        "Pik Günlük Talep": st.column_config.NumberColumn(
          format="%d"
        ),
      },
    )

  st.caption(
    "Bu analiz sefer sayısı, tekne kapasitesi, filo ataması, "
    "enerji ihtiyacı veya altyapı yeterliliği üretmez."
  )
