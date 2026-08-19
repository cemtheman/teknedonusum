import pytest

from calculations.power_sensitivity_band import calculate_power_sensitivity_band
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY


V1_GEOMETRY = PRELIMINARY_VESSEL_GEOMETRY["v1"]
RESIDUAL_VALUES = (500.0, 1500.0, 2500.0)
EFFICIENCY_VALUES = (0.50, 0.60, 0.65)


def calculate_band(**overrides):
  # Inputs are preliminary sensitivity scenarios, not established physical bounds.
  scenario = {
      "geometry": V1_GEOMETRY,
      "speed_knots": 10.0,
      "form_factor": 0.15,
      "residual_resistance_values_n": RESIDUAL_VALUES,
      "propulsive_efficiency_values": EFFICIENCY_VALUES,
      "appendage_resistance_n": 100.0,
      "motor_efficiency": 0.95,
      "design_margin_fraction": 0.15,
  }
  scenario.update(overrides)
  return calculate_power_sensitivity_band(**scenario)


def test_baseline_grid_literal_values_and_order():
  band = calculate_band()
  expected = (
      (500.0, 0.50, 8.38058666685422, 16.76117333370844, 19.275349333764705),
      (500.0, 0.60, 8.38058666685422, 13.967644444757035, 16.062791111470588),
      (500.0, 0.65, 8.38058666685422, 12.8932102566988, 14.82719179520362),
      (1500.0, 0.50, 13.52502666685422, 27.05005333370844, 31.107561333764703),
      (1500.0, 0.60, 13.52502666685422, 22.5417111114237, 25.922967778137256),
      (1500.0, 0.65, 13.52502666685422, 20.807733333621876, 23.928893333665155),
      (2500.0, 0.50, 18.66946666685422, 37.33893333370844, 42.939773333764705),
      (2500.0, 0.60, 18.66946666685422, 31.11577777809037, 35.78314444480392),
      (2500.0, 0.65, 18.66946666685422, 28.72225641054495, 33.03059487212669),
  )

  assert len(band.points) == 9
  for point, values in zip(band.points, expected):
    residual, efficiency, effective, motor_output, installed = values
    assert point.residual_resistance_n == residual
    assert point.propulsive_efficiency == efficiency
    assert point.effective_power_kw == pytest.approx(effective)
    assert point.motor_output_power_kw == pytest.approx(motor_output)
    assert point.installed_power_kw == pytest.approx(installed)

  assert band.minimum_installed_power_kw == pytest.approx(14.82719179520362)
  assert band.maximum_installed_power_kw == pytest.approx(42.939773333764705)


def test_installed_power_decreases_across_each_efficiency_row():
  points = calculate_band().points
  for row_start in (0, 3, 6):
    row = points[row_start:row_start + 3]
    assert row[0].installed_power_kw > row[1].installed_power_kw
    assert row[1].installed_power_kw > row[2].installed_power_kw


def test_effective_and_installed_power_increase_down_each_residual_column():
  points = calculate_band().points
  for column in range(3):
    low, middle, high = points[column], points[column + 3], points[column + 6]
    assert low.effective_power_kw < middle.effective_power_kw < high.effective_power_kw
    assert low.installed_power_kw < middle.installed_power_kw < high.installed_power_kw


def test_motor_efficiency_changes_only_electrical_input():
  low_efficiency = calculate_band(motor_efficiency=0.90)
  high_efficiency = calculate_band(motor_efficiency=0.95)

  for low, high in zip(low_efficiency.points, high_efficiency.points):
    assert low.effective_power_kw == high.effective_power_kw
    assert low.motor_output_power_kw == high.motor_output_power_kw
    assert low.installed_power_kw == high.installed_power_kw
    assert low.electrical_input_power_kw > high.electrical_input_power_kw


def test_design_margin_changes_only_installed_power():
  no_margin = calculate_band(design_margin_fraction=0.0)
  high_margin = calculate_band(design_margin_fraction=0.20)

  for low, high in zip(no_margin.points, high_margin.points):
    assert low.effective_power_kw == high.effective_power_kw
    assert low.motor_output_power_kw == high.motor_output_power_kw
    assert low.electrical_input_power_kw == high.electrical_input_power_kw
    assert low.installed_power_kw < high.installed_power_kw


def test_empty_residual_values_are_rejected():
  with pytest.raises(ValueError):
    calculate_band(residual_resistance_values_n=())


def test_empty_efficiency_values_are_rejected():
  with pytest.raises(ValueError):
    calculate_band(propulsive_efficiency_values=())


def test_generator_inputs_and_duplicate_values_are_preserved():
  residual_generator = (value for value in (500.0, 500.0))
  efficiency_generator = (value for value in (0.60, 0.60))
  band = calculate_band(
      residual_resistance_values_n=residual_generator,
      propulsive_efficiency_values=efficiency_generator,
  )

  assert len(band.points) == 4
  assert [
      (point.residual_resistance_n, point.propulsive_efficiency)
      for point in band.points
  ] == [(500.0, 0.60)] * 4
