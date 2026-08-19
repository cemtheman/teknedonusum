import pytest

from calculations.power_comparison import compare_legacy_and_preliminary_power
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from config.vessels import BASE_VESSEL_SPECS


V1_SPEC = BASE_VESSEL_SPECS["v1"]
V1_GEOMETRY = PRELIMINARY_VESSEL_GEOMETRY["v1"]


def compare(**overrides):
  scenario = {
      "spec": V1_SPEC,
      "geometry": V1_GEOMETRY,
      "speed_knots": 10.0,
      "daily_miles": 35.0,
      "sun_hours": 8.0,
      "form_factor": 0.15,
      "residual_resistance_n": 1500.0,
      "appendage_resistance_n": 100.0,
      "propulsive_efficiency": 0.60,
      "motor_efficiency": 0.95,
      "design_margin_fraction": 0.15,
  }
  scenario.update(overrides)
  return compare_legacy_and_preliminary_power(**scenario)


def test_ten_knot_baseline_comparison():
  # This regression comparison does not claim that the preliminary model is
  # correct or that the legacy model is wrong. It only locks both approaches for
  # the same example scenario; the residual input is not verified vessel data.
  result = compare()

  assert result.speed_knots == 10.0
  assert result.legacy_power_kw == pytest.approx(31.406960743782072)
  assert result.effective_power_kw == pytest.approx(13.52502666685422)
  assert result.motor_output_power_kw == pytest.approx(22.5417111114237)
  assert result.electrical_input_power_kw == pytest.approx(23.728116959393372)
  assert result.installed_power_kw == pytest.approx(25.922967778137256)
  assert result.legacy_minus_installed_kw == pytest.approx(5.483992965644816)
  assert result.legacy_to_installed_ratio == pytest.approx(1.2115495807648178)


def test_higher_residual_changes_only_preliminary_power_chain():
  low_residual = compare(residual_resistance_n=500.0)
  high_residual = compare(residual_resistance_n=2500.0)

  assert high_residual.legacy_power_kw == low_residual.legacy_power_kw
  assert high_residual.effective_power_kw > low_residual.effective_power_kw
  assert high_residual.motor_output_power_kw > low_residual.motor_output_power_kw
  assert high_residual.installed_power_kw > low_residual.installed_power_kw


def test_lower_propulsive_efficiency_increases_downstream_power_only():
  low_efficiency = compare(propulsive_efficiency=0.50)
  high_efficiency = compare(propulsive_efficiency=0.65)

  assert low_efficiency.legacy_power_kw == high_efficiency.legacy_power_kw
  assert low_efficiency.effective_power_kw == high_efficiency.effective_power_kw
  assert low_efficiency.motor_output_power_kw > high_efficiency.motor_output_power_kw
  assert (
      low_efficiency.electrical_input_power_kw
      > high_efficiency.electrical_input_power_kw
  )
  assert low_efficiency.installed_power_kw > high_efficiency.installed_power_kw


def test_invalid_geometry_type_is_rejected_by_sensitivity_model():
  with pytest.raises(TypeError):
    compare(geometry=object())
