import streamlit as st

from calculations.fleet import calculate_fleet
from config.operational_profile import (
    PVGIS_HOURLY_END_YEAR,
    PVGIS_HOURLY_START_YEAR,
)
from config.vessel_factory import build_vessel_specs
from services.market_data import fetch_aytemiz_diesel, fetch_tcmb_eur
from services.solar_hourly import (
    build_typical_hourly_profile,
    fetch_pvgis_hourly_specific_pv,
)
from ui.branding import (
    FAVICON_PATH,
    render_brand_footer,
)
from ui.fleet_dashboard import render_fleet_dashboard
from ui.fleet_inventory_dashboard import render_fleet_inventory_dashboard
from ui.grant_program import render_grant_program
from ui.inputs import render_sidebar
from ui.normative_comparison import render_normative_comparison_section
from ui.scenario_overview import render_scenario_overview
from ui.vessel_detail import render_vessel_details


def main():
  st.set_page_config(
      page_title="Sessiz Akım",
      page_icon=str(FAVICON_PATH),
      layout="wide",
      initial_sidebar_state="expanded",
  )

  live_eur, eur_is_live = fetch_tcmb_eur()
  live_diesel, diesel_is_live = fetch_aytemiz_diesel()

  inputs = render_sidebar(live_eur, eur_is_live, live_diesel, diesel_is_live)

  # Render the first main-pane content before the remote PVGIS request.
  render_scenario_overview(inputs)

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

  try:
    hourly_points = fetch_pvgis_hourly_specific_pv(
        inputs.latitude,
        inputs.longitude,
        PVGIS_HOURLY_START_YEAR,
        PVGIS_HOURLY_END_YEAR,
    )
    typical_hourly_specific_pv = build_typical_hourly_profile(hourly_points)
  except Exception as exc:
    st.error(
        "PVGIS saatlik solar profili alınamadı; sezonluk batarya/şebeke "
        f"dengesi hesaplanamıyor. Ayrıntı: {exc}"
    )
    st.stop()

  fleet = calculate_fleet(
      vessel_specs,
      counts,
      inputs.cruise_speed,
      inputs.daily_miles,
      None,
      inputs.operating_days,
      average_daily_specific_yield_kwh_per_kwp=(
          inputs.average_daily_specific_yield_kwh_per_kwp
      ),
      season_start=inputs.season_start,
      season_end=inputs.season_end,
      typical_hourly_specific_pv=typical_hourly_specific_pv,
  )

  render_fleet_inventory_dashboard(
      st.session_state.get("fleet_inventory_analysis"),
      allocation=st.session_state.get("fleet_inventory_allocation"),
      plan_active=st.session_state.get(
          "fleet_inventory_plan_active",
          False,
      ),
      vessel_specs=vessel_specs,
      inputs=inputs,
      fleet=fleet,
  )

  render_fleet_dashboard(vessel_specs, inputs, fleet)

  render_grant_program(vessel_specs, inputs, fleet)

  render_normative_comparison_section(
      vessel_specs,
      inputs.cruise_speed,
      inputs.daily_miles,
  )

  render_vessel_details(
      vessel_specs,
      inputs,
      typical_hourly_specific_pv=typical_hourly_specific_pv,
  )

  render_brand_footer()


if __name__ == "__main__":
  main()
