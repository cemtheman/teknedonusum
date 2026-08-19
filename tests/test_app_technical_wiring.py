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
      "from calculations.assumptions_transparency import build_assumptions_transparency",
      "from calculations.decision_summary import build_vessel_decision_summary",
      "from calculations.economic_comparison import build_vessel_economic_comparison",
      "from calculations.presentation import build_technical_scenario_presentation",
      "from calculations.technical_scenario import evaluate_preliminary_technical_scenario",
      "from calculations.vessel_comparison import build_vessel_technical_comparison",
      "from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS",
      "from config.geometry import PRELIMINARY_VESSEL_GEOMETRY",
      "from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS",
      "from ui.assumptions_transparency import render_assumptions_transparency",
      "from ui.technical_scenario import render_technical_scenario",
      "from ui.decision_summary import render_vessel_decision_summary",
      "from ui.vessel_comparison import render_vessel_technical_comparison",
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
  assert keyword_source(scenario_call, "speed_knots") == "inputs.cruise_speed"
  assert keyword_source(scenario_call, "daily_distance_nm") == "inputs.daily_miles"
  assert keyword_source(scenario_call, "peak_sun_hours") == "inputs.sun_hours"
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
      "solar_derating_factor",
  }
  assert all(
      keyword_source(scenario_call, keyword) == f"assumptions.{keyword}"
      for keyword in assumption_keywords
  )


def test_render_order_preserves_legacy_flow():
  fleet_position = APP_SOURCE.index("render_fleet_dashboard(")
  decision_position = APP_SOURCE.index("render_vessel_decision_summary(")
  scenario_position = APP_SOURCE.index("render_technical_scenario(")
  comparison_position = APP_SOURCE.index("render_vessel_technical_comparison(")
  details_position = APP_SOURCE.index("render_vessel_details(")

  assert (
      fleet_position
      < decision_position
      < scenario_position
      < comparison_position
      < details_position
  )


def test_comparison_uses_current_sidebar_operational_inputs():
  comparison_call = calls_named("build_vessel_technical_comparison")[0]

  assert len(calls_named("build_vessel_technical_comparison")) == 1
  assert len(calls_named("render_vessel_technical_comparison")) == 1
  assert keyword_source(comparison_call, "vessel_specs") == "VESSEL_SPECS"
  assert keyword_source(comparison_call, "cruise_speed") == "inputs.cruise_speed"
  assert keyword_source(comparison_call, "daily_miles") == "inputs.daily_miles"
  assert keyword_source(comparison_call, "sun_hours") == "inputs.sun_hours"


def test_economic_comparison_uses_current_sidebar_inputs():
  economic_call = calls_named("build_vessel_economic_comparison")[0]

  assert len(calls_named("build_vessel_economic_comparison")) == 1
  assert len(calls_named("build_vessel_decision_summary")) == 1
  assert len(calls_named("render_vessel_decision_summary")) == 1
  assert keyword_source(economic_call, "vessel_specs") == "VESSEL_SPECS"
  assert keyword_source(economic_call, "cruise_speed") == "inputs.cruise_speed"
  assert keyword_source(economic_call, "daily_miles") == "inputs.daily_miles"
  assert keyword_source(economic_call, "sun_hours") == "inputs.sun_hours"
  assert keyword_source(economic_call, "season_days") == "inputs.operating_days"
  assert keyword_source(economic_call, "electricity_price") == "inputs.elec_price"
  assert keyword_source(economic_call, "diesel_price") == "inputs.diesel_price"
  assert keyword_source(economic_call, "exchange_rate") == "inputs.eur_rate"


def test_assumptions_transparency_uses_current_values_and_live_flags():
  transparency_call = calls_named("build_assumptions_transparency")[0]

  assert len(calls_named("build_assumptions_transparency")) == 1
  assert len(calls_named("render_assumptions_transparency")) == 1
  assert keyword_source(transparency_call, "inputs") == "inputs"
  assert keyword_source(transparency_call, "vessel_specs") == "VESSEL_SPECS"
  assert keyword_source(transparency_call, "eur_is_live") == "eur_is_live"
  assert keyword_source(transparency_call, "diesel_is_live") == "diesel_is_live"
