import pandas as pd
import streamlit as st

from models.inputs import SimulationInputs


def _format_decimal_tr(value, digits=1):
  return f"{float(value):.{digits}f}".replace(".", ",")


def build_scenario_summary(inputs: SimulationInputs):
  return {
      "Hizmet hızı": f"{_format_decimal_tr(inputs.cruise_speed)} kn",
      "Günlük rota": f"{_format_decimal_tr(inputs.daily_miles)} NM",
      "Sezon": f"{inputs.season_days} gün",
      "PVGIS ort. özgül üretim": (
          f"{_format_decimal_tr(inputs.average_daily_specific_yield_kwh_per_kwp, 2)} "
          "kWh/kWp-gün"
      ),
      "Liman elektriği": f"{_format_decimal_tr(inputs.elec_price, 2)} TL/kWh",
      "Dizel": f"{_format_decimal_tr(inputs.diesel_price, 2)} TL/L",
      "EUR / TRY": _format_decimal_tr(inputs.eur_rate, 2),
  }


def _scenario_metric_card(label, value):
  return f"""
  <div style="
      border:1px solid #E2E8F0;
      border-radius:12px;
      background:#FFFFFF;
      padding:14px 15px;
      min-height:86px;
      margin-bottom:10px;">
    <div style="
        font-size:0.74rem;
        color:#64748B;
        font-weight:650;
        margin-bottom:6px;">
      {label}
    </div>
    <div style="
        font-size:1.18rem;
        line-height:1.15;
        color:#0F172A;
        font-weight:800;">
      {value}
    </div>
  </div>
  """


def _location_badge(inputs: SimulationInputs):
  return f"""
  <div style="
      display:inline-flex;
      align-items:center;
      gap:7px;
      padding:7px 11px;
      border-radius:999px;
      background:#F0FDF4;
      border:1px solid #BBF7D0;
      color:#166534;
      font-size:0.82rem;
      font-weight:750;
      margin-bottom:9px;">
    📍 {inputs.location_name}
  </div>
  """


def render_scenario_overview(inputs: SimulationInputs):
  st.subheader("🧭 Senaryo ve Lokasyon Özeti")

  map_col, summary_col = st.columns(
      [0.92, 1.08],
      vertical_alignment="top",
  )

  with map_col:
    st.markdown(_location_badge(inputs), unsafe_allow_html=True)

    map_data = pd.DataFrame({
        "lat": [float(inputs.latitude)],
        "lon": [float(inputs.longitude)],
    })
    st.map(
        map_data,
        zoom=12,
        width="stretch",
        height=225,
    )
    st.caption(
        f"{inputs.latitude:.4f}, {inputs.longitude:.4f} · "
        f"Solar kaynak: {inputs.solar_resource_source}"
    )

  summary = build_scenario_summary(inputs)

  with summary_col:
    st.markdown("**Anahtar Senaryo Girdileri**")
    left, right = st.columns(2, gap="small")
    items = list(summary.items())

    for index, (label, value) in enumerate(items):
      target = left if index % 2 == 0 else right
      with target:
        st.markdown(
            _scenario_metric_card(label, value),
            unsafe_allow_html=True,
        )

    st.caption(
        f"Aktif sezon: {inputs.season_start:%d.%m.%Y}–"
        f"{inputs.season_end:%d.%m.%Y} · "
        "Değerler soldaki simülasyon girdilerinin canlı özetidir."
    )

  st.divider()
