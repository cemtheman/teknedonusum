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


def test_primary_app_has_single_technical_comparison_flow():
  assert not calls_named("render_normative_sizing_section")
  assert len(calls_named("render_normative_comparison_section")) == 1
  assert len(calls_named("render_vessel_details")) == 1

  assert not calls_named("render_vessel_decision_summary")
  assert not calls_named("render_assumptions_transparency")
  assert not calls_named("build_vessel_decision_summary")
  assert not calls_named("build_vessel_economic_comparison")
  assert not calls_named("build_vessel_technical_comparison")


def test_render_order_is_fleet_then_technical_then_financial_details():
  fleet_position = APP_SOURCE.index("render_fleet_dashboard(")
  comparison_position = APP_SOURCE.index("render_normative_comparison_section(")
  details_position = APP_SOURCE.index("render_vessel_details(")

  assert fleet_position < comparison_position < details_position


def test_sidebar_speed_and_route_feed_single_technical_comparison():
  comparison_call = calls_named("render_normative_comparison_section")[0]

  assert ast.unparse(comparison_call.args[0]) == "vessel_specs"
  assert ast.unparse(comparison_call.args[1]) == "inputs.cruise_speed"
  assert ast.unparse(comparison_call.args[2]) == "inputs.daily_miles"


def test_vessel_financial_details_remain_collapsed():
  assert "with st.expander(f\"📌 {spec['name']}\", expanded=False)" in (
      VESSEL_DETAIL_SOURCE
  )


def test_header_is_turkish_only():
  assert "Quiet Current" not in APP_SOURCE
  assert "e-Fleet Simulation" not in APP_SOURCE
