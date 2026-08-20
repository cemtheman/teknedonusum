import streamlit as st

from calculations.assumptions_transparency import build_assumptions_transparency
from calculations.decision_summary import build_vessel_decision_summary
from calculations.economic_comparison import build_vessel_economic_comparison
from calculations.fleet import calculate_fleet
from calculations.vessel_comparison import build_vessel_technical_comparison
from config.vessel_factory import build_vessel_specs
from services.market_data import fetch_aytemiz_diesel, fetch_tcmb_eur
from ui.assumptions_transparency import render_assumptions_transparency
from ui.decision_summary import render_vessel_decision_summary
from ui.fleet_dashboard import render_fleet_dashboard
from ui.inputs import render_sidebar
from ui.vessel_detail import render_vessel_details


def main():
  # Page Configuration
  st.set_page_config(
      page_title="Sessiz Akım — Quiet Current",
      page_icon="⚓",
      layout="wide",
      initial_sidebar_state="expanded",
  )

  # Header Section
  st.markdown(
      '<p style="font-size: 1.8rem; font-weight: 700; color: #1E3A8A;'
      ' margin-bottom: 2px;">⚓ Sessiz Akım — Köyceğiz & Dalyan Elektrikli Filo'
      " Simülasyon Portalı</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 1.05rem; font-weight: 600; color: #2563EB;'
      ' margin-bottom: 6px;">Quiet Current — Köyceğiz & Dalyan e-Fleet Simulation'
      " Portal</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 20px;">Yönetmelik'
      " ve Kurul Kararlarıyla Uyumlu İnteraktif Fizibilite ve Hibe"
      " Simülatörü</p>",
      unsafe_allow_html=True,
  )

  # Fetch Online Live Data
  live_eur, eur_is_live = fetch_tcmb_eur()
  live_diesel, diesel_is_live = fetch_aytemiz_diesel()

  # Sidebar Controls
  inputs = render_sidebar(live_eur, eur_is_live, live_diesel, diesel_is_live)

  # Dynamic Vessel Data Specs Construction
  VESSEL_SPECS = build_vessel_specs(
      inputs.cost_eur_v1,
      inputs.cost_eur_v2,
      inputs.cost_eur_v3,
      inputs.eur_rate,
  )

  # --- Fleet Aggregate Calculations ---
  counts = {
      "v1": inputs.count_v1,
      "v2": inputs.count_v2,
      "v3": inputs.count_v3,
      "v4_24": inputs.count_v4_24,
      "v4_32": inputs.count_v4_32,
  }

  fleet = calculate_fleet(
      VESSEL_SPECS,
      counts,
      inputs.cruise_speed,
      inputs.daily_miles,
      inputs.sun_hours,
      inputs.operating_days,
  )

  render_fleet_dashboard(VESSEL_SPECS, inputs, fleet)

  comparison = build_vessel_technical_comparison(
      vessel_specs=VESSEL_SPECS,
      cruise_speed=inputs.cruise_speed,
      daily_miles=inputs.daily_miles,
      sun_hours=inputs.sun_hours,
  )
  economic_comparison = build_vessel_economic_comparison(
      vessel_specs=VESSEL_SPECS,
      cruise_speed=inputs.cruise_speed,
      daily_miles=inputs.daily_miles,
      sun_hours=inputs.sun_hours,
      season_days=inputs.operating_days,
      electricity_price=inputs.elec_price,
      diesel_price=inputs.diesel_price,
      exchange_rate=inputs.eur_rate,
  )
  decision_summary = build_vessel_decision_summary(
      comparison,
      economic_comparison,
  )
  assumptions_transparency = build_assumptions_transparency(
      inputs=inputs,
      vessel_specs=VESSEL_SPECS,
      eur_is_live=eur_is_live,
      diesel_is_live=diesel_is_live,
  )
  render_vessel_decision_summary(
      decision_summary,
      assumptions_transparency,
  )
  render_assumptions_transparency(assumptions_transparency)

  render_vessel_details(VESSEL_SPECS, inputs)


if __name__ == "__main__":
  main()
