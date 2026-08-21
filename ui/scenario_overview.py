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


def render_scenario_overview(inputs: SimulationInputs):
  st.subheader("🧭 Senaryo ve Lokasyon Özeti")

  map_col, summary_col = st.columns([1.15, 1.0])

  with map_col:
    st.markdown(f"**📍 {inputs.location_name}**")
    map_data = pd.DataFrame({
        "lat": [float(inputs.latitude)],
        "lon": [float(inputs.longitude)],
    })
    st.map(map_data, zoom=12, use_container_width=True)
    st.caption(
        f"Koordinatlar: {inputs.latitude:.4f}, {inputs.longitude:.4f} · "
        f"Solar kaynak: {inputs.solar_resource_source}"
    )

  summary = build_scenario_summary(inputs)
  with summary_col:
    st.markdown("**Anahtar Senaryo Girdileri**")
    left, right = st.columns(2)
    items = list(summary.items())

    for index, (label, value) in enumerate(items):
      target = left if index % 2 == 0 else right
      with target:
        st.metric(label, value)

    st.caption(
        f"Sezon: {inputs.season_start:%d.%m.%Y}–"
        f"{inputs.season_end:%d.%m.%Y}. "
        "Bu değerler soldaki simülasyon girdilerinin aktif özetidir."
    )

  st.divider()
