import ast
from pathlib import Path


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
APP_TREE = ast.parse(APP_SOURCE)
VESSEL_DETAIL_SOURCE = Path("ui/vessel_detail.py").read_text(encoding="utf-8")


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


def test_management_sections_imports_are_present():
  required_imports = {
      "from calculations.assumptions_transparency import build_assumptions_transparency",
      "from calculations.decision_summary import build_vessel_decision_summary",
      "from calculations.economic_comparison import build_vessel_economic_comparison",
      "from calculations.vessel_comparison import build_vessel_technical_comparison",
      "from ui.assumptions_transparency import render_assumptions_transparency",
      "from ui.decision_summary import render_vessel_decision_summary",
      "from ui.vessel_comparison import render_vessel_technical_comparison",
      "from ui.vessel_detail import render_vessel_details",
  }
  assert all(import_line in APP_SOURCE for import_line in required_imports)


def test_preliminary_technical_section_is_not_rendered():
  assert not calls_named("evaluate_preliminary_technical_scenario")
  assert not calls_named("build_technical_scenario_presentation")
  assert not calls_named("render_technical_scenario")
  assert "⚙️ Ön Teknik Uygunluk ve Enerji Değerlendirmesi" not in APP_SOURCE


def test_vessel_detail_section_remains_available_but_collapsed():
  assert len(calls_named("render_vessel_details")) == 1
  assert 'with st.expander(f"📌 {spec[\'name\']}", expanded=False)' in (
      VESSEL_DETAIL_SOURCE
  )


def test_render_order_preserves_legacy_flow():
  fleet_position = APP_SOURCE.index("render_fleet_dashboard(")
  decision_position = APP_SOURCE.index("render_vessel_decision_summary(")
  assumptions_position = APP_SOURCE.index("render_assumptions_transparency(")
  comparison_position = APP_SOURCE.index("render_vessel_technical_comparison(")
  details_position = APP_SOURCE.index("render_vessel_details(")

  assert (
      fleet_position
      < decision_position
      < assumptions_position
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
