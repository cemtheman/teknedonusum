import ast
from pathlib import Path


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
APP_TREE = ast.parse(APP_SOURCE)


def calls_named(name):
  return [
      node for node in ast.walk(APP_TREE)
      if isinstance(node, ast.Call)
      and isinstance(node.func, ast.Name)
      and node.func.id == name
  ]


def keyword_source(call, keyword_name):
  keyword = next(item for item in call.keywords if item.arg == keyword_name)
  return ast.unparse(keyword.value)


def test_technical_scenario_imports_are_present():
  required_imports = {
      "from calculations.presentation import build_technical_scenario_presentation",
      "from calculations.technical_scenario import evaluate_preliminary_technical_scenario",
      "from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS",
      "from config.geometry import PRELIMINARY_VESSEL_GEOMETRY",
      "from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS",
      "from ui.technical_scenario import render_technical_scenario",
  }
  assert all(import_line in APP_SOURCE for import_line in required_imports)


def test_technical_scenario_is_wired_once_for_v1_only():
  assert APP_SOURCE.count('PRELIMINARY_VESSEL_GEOMETRY["v1"]') == 1
  assert 'PRELIMINARY_VESSEL_GEOMETRY["v2"]' not in APP_SOURCE
  assert 'PRELIMINARY_VESSEL_GEOMETRY["v3"]' not in APP_SOURCE
  assert len(calls_named("evaluate_preliminary_technical_scenario")) == 1
  assert len(calls_named("build_technical_scenario_presentation")) == 1
  assert len(calls_named("render_technical_scenario")) == 1


def test_scenario_uses_required_dynamic_sources_and_assumptions():
  scenario_call = calls_named("evaluate_preliminary_technical_scenario")[0]

  assert keyword_source(scenario_call, "geometry") == "geometry"
  assert keyword_source(scenario_call, "constraints") == (
      "DALYAN_COMMISSION_CONSTRAINTS"
  )
  assert keyword_source(scenario_call, "passenger_capacity") == (
      "VESSEL_SPECS['v1']['capacity']"
  )
  assert keyword_source(scenario_call, "speed_knots") == (
      "DALYAN_COMMISSION_CONSTRAINTS.minimum_required_speed_knots"
  )
  assert keyword_source(scenario_call, "daily_distance_nm") == "inputs.daily_miles"
  assert keyword_source(scenario_call, "battery_capacity_kwh") == (
      "VESSEL_SPECS['v1']['batCapacity']"
  )

  assumption_keywords = {
      "form_factor",
      "residual_resistance_n",
      "appendage_resistance_n",
      "propulsive_efficiency",
      "motor_efficiency",
      "design_margin_fraction",
      "usable_energy_fraction",
      "operational_reserve_fraction",
      "hotel_load_kw",
      "roof_length_fraction_of_loa",
      "usable_roof_width_m",
      "panel_coverage_fraction",
      "panel_efficiency",
      "peak_sun_hours",
      "solar_derating_factor",
  }
  assert all(
      keyword_source(scenario_call, keyword) == f"assumptions.{keyword}"
      for keyword in assumption_keywords
  )


def test_render_order_preserves_legacy_flow():
  fleet_position = APP_SOURCE.index("render_fleet_dashboard(")
  scenario_position = APP_SOURCE.index("render_technical_scenario(")
  details_position = APP_SOURCE.index("render_vessel_details(")

  assert fleet_position < scenario_position < details_position
