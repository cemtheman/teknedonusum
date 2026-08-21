import math

import pytest

from calculations.continuous_cruise import (
    calculate_continuous_cruise_power,
    infer_solar_only_observation_bound,
)


def test_continuous_cruise_uses_resistance_chain_not_speed_power_exponent():
  result = calculate_continuous_cruise_power(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
      residual_resistance_n=0.0,
      appendage_resistance_n=0.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )

  expected_froude = (6.0 * 0.514444) / math.sqrt(9.80665 * 11.4)
  assert result.froude_number == pytest.approx(expected_froude)
  assert result.frictional_resistance_n > 0
  assert result.viscous_resistance_n > result.frictional_resistance_n
  assert result.total_resistance_n == pytest.approx(
      result.viscous_resistance_n
  )
  assert result.electrical_input_power_kw > result.shaft_power_kw
  assert result.shaft_power_kw > result.effective_power_kw


def test_residual_and_appendage_are_explicit_additive_inputs():
  baseline = calculate_continuous_cruise_power(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
      residual_resistance_n=0.0,
      appendage_resistance_n=0.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )
  calibrated = calculate_continuous_cruise_power(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
      residual_resistance_n=800.0,
      appendage_resistance_n=100.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )

  assert calibrated.total_resistance_n - baseline.total_resistance_n == pytest.approx(
      900.0
  )
  assert calibrated.electrical_input_power_kw > baseline.electrical_input_power_kw


def test_solar_only_observation_is_an_upper_bound_not_a_power_prediction():
  bound = infer_solar_only_observation_bound(
      installed_pv_kwp=11.5,
      specific_pv_power_kw_per_kwp=0.82,
  )

  assert bound.observed_solar_available_kw == pytest.approx(9.43)
  assert bound.maximum_electrical_propulsion_power_kw == pytest.approx(9.43)


def test_no_legacy_speed_exponent_is_needed_for_six_knot_power():
  low_residual = calculate_continuous_cruise_power(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
      residual_resistance_n=500.0,
      appendage_resistance_n=100.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )
  high_residual = calculate_continuous_cruise_power(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
      residual_resistance_n=1500.0,
      appendage_resistance_n=100.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )

  assert low_residual.electrical_input_power_kw < high_residual.electrical_input_power_kw
  assert low_residual.electrical_input_power_kw < 11.7


@pytest.mark.parametrize(
    "field,value",
    [
        ("speed_knots", 0.0),
        ("waterline_length_m", 0.0),
        ("wetted_surface_area_m2", 0.0),
        ("residual_resistance_n", -1.0),
        ("appendage_resistance_n", -1.0),
        ("propulsive_efficiency", 0.0),
        ("motor_efficiency", 0.0),
    ],
)
def test_invalid_physical_inputs_are_rejected(field, value):
  kwargs = {
      "speed_knots": 6.0,
      "waterline_length_m": 11.4,
      "wetted_surface_area_m2": 30.0,
      "form_factor": 0.15,
      "residual_resistance_n": 500.0,
      "appendage_resistance_n": 100.0,
      "propulsive_efficiency": 0.60,
      "motor_efficiency": 0.95,
  }
  kwargs[field] = value

  with pytest.raises(ValueError):
    calculate_continuous_cruise_power(**kwargs)
