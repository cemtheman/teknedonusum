import streamlit as st

from calculations.fleet import calculate_fleet
from config.vessel_factory import build_vessel_specs
from services.market_data import fetch_aytemiz_diesel, fetch_tcmb_eur
from ui.fleet_dashboard import render_fleet_dashboard
from ui.inputs import render_sidebar
from ui.normative_comparison import render_normative_comparison_section
from ui.normative_sizing import render_normative_sizing_section
from ui.vessel_detail import render_vessel_details


def main():
  st.set_page_config(
      page_title="Sessiz Akım",
      page_icon="⚓",
      layout="wide",
      initial_sidebar_state="expanded",
  )

  st.markdown(
      '<p style="font-size: 1.8rem; font-weight: 700; color: #1E3A8A;'
      ' margin-bottom: 4px;">⚓ Sessiz Akım — Köyceğiz & Dalyan Elektrikli Filo '
      "Simülasyon Portalı</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 20px;">'
      "Yönetmelik ve Kurul Kararlarıyla Uyumlu İnteraktif Fizibilite ve Hibe "
      "Simülatörü</p>",
      unsafe_allow_html=True,
  )

  live_eur, eur_is_live = fetch_tcmb_eur()
  live_diesel, diesel_is_live = fetch_aytemiz_diesel()

  inputs = render_sidebar(live_eur, eur_is_live, live_diesel, diesel_is_live)

  vessel_specs = build_vessel_specs(
      inputs.cost_eur_v1,
      inputs.cost_eur_v2,
      inputs.cost_eur_v3,
      inputs.eur_rate,
  )

  counts = {
      "v1": inputs.count_v1,
      "v2": inputs.count_v2,
      "v3": inputs.count_v3,
      "v4_24": inputs.count_v4_24,
      "v4_32": inputs.count_v4_32,
  }

  fleet = calculate_fleet(
      vessel_specs,
      counts,
      inputs.cruise_speed,
      inputs.daily_miles,
      inputs.sun_hours,
      inputs.operating_days,
  )

  render_fleet_dashboard(vessel_specs, inputs, fleet)

  render_normative_sizing_section(
      vessel_specs,
      inputs.cruise_speed,
      inputs.daily_miles,
  )

  render_normative_comparison_section(
      vessel_specs,
      inputs.cruise_speed,
      inputs.daily_miles,
  )

  render_vessel_details(vessel_specs, inputs)


if __name__ == "__main__":
  main()
