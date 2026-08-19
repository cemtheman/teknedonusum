from dataclasses import FrozenInstanceError, fields

import pytest

from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from models.constraints import CommissionTechnicalConstraints


def valid_constraints(**overrides):
  values = {
      "minimum_loa_m": 12.0,
      "maximum_loa_m": 14.0,
      "allowed_passenger_capacities": (24, 32, 54),
      "minimum_required_speed_knots": 10.0,
      "minimum_navigation_range_nm": 15.0,
      "minimum_motor_efficiency": 0.95,
      "minimum_battery_capacity_kwh": 20.0,
      "minimum_roof_length_fraction_of_loa": 0.80,
  }
  values.update(overrides)
  return CommissionTechnicalConstraints(**values)


def test_constraint_model_is_frozen_and_has_exact_schema():
  assert CommissionTechnicalConstraints.__dataclass_params__.frozen is True
  assert [field.name for field in fields(CommissionTechnicalConstraints)] == [
      "minimum_loa_m",
      "maximum_loa_m",
      "allowed_passenger_capacities",
      "minimum_required_speed_knots",
      "minimum_navigation_range_nm",
      "minimum_motor_efficiency",
      "minimum_battery_capacity_kwh",
      "minimum_roof_length_fraction_of_loa",
  ]


def test_commission_constraint_values_and_capacity_order():
  constraints = DALYAN_COMMISSION_CONSTRAINTS
  assert constraints.minimum_loa_m == 12.0
  assert constraints.maximum_loa_m == 14.0
  assert constraints.allowed_passenger_capacities == (24, 32, 54)
  assert constraints.minimum_required_speed_knots == 10.0
  assert constraints.minimum_navigation_range_nm == 15.0
  assert constraints.minimum_motor_efficiency == 0.95
  assert constraints.minimum_battery_capacity_kwh == 20.0
  assert constraints.minimum_roof_length_fraction_of_loa == 0.80


def test_commission_constraint_instance_is_immutable():
  with pytest.raises(FrozenInstanceError):
    DALYAN_COMMISSION_CONSTRAINTS.minimum_loa_m = 13.0


@pytest.mark.parametrize("minimum_loa_m", [0.0, -1.0])
def test_minimum_loa_m_must_be_positive(minimum_loa_m):
  with pytest.raises(ValueError):
    valid_constraints(minimum_loa_m=minimum_loa_m)


def test_maximum_loa_m_must_not_be_below_minimum():
  with pytest.raises(ValueError):
    valid_constraints(maximum_loa_m=11.9)


def test_passenger_capacities_must_not_be_empty():
  with pytest.raises(ValueError):
    valid_constraints(allowed_passenger_capacities=())


@pytest.mark.parametrize("capacities", [(0,), (-1,), (24, 0, 54)])
def test_passenger_capacities_must_be_positive(capacities):
  with pytest.raises(ValueError):
    valid_constraints(allowed_passenger_capacities=capacities)


@pytest.mark.parametrize("minimum_required_speed_knots", [0.0, -1.0])
def test_minimum_speed_must_be_positive(minimum_required_speed_knots):
  with pytest.raises(ValueError):
    valid_constraints(minimum_required_speed_knots=minimum_required_speed_knots)


@pytest.mark.parametrize("minimum_navigation_range_nm", [0.0, -1.0])
def test_minimum_navigation_range_must_be_positive(minimum_navigation_range_nm):
  with pytest.raises(ValueError):
    valid_constraints(minimum_navigation_range_nm=minimum_navigation_range_nm)


@pytest.mark.parametrize("minimum_motor_efficiency", [0.0, -0.1, 1.1])
def test_minimum_motor_efficiency_must_be_in_valid_range(minimum_motor_efficiency):
  with pytest.raises(ValueError):
    valid_constraints(minimum_motor_efficiency=minimum_motor_efficiency)


@pytest.mark.parametrize("minimum_battery_capacity_kwh", [0.0, -1.0])
def test_minimum_battery_capacity_must_be_positive(minimum_battery_capacity_kwh):
  with pytest.raises(ValueError):
    valid_constraints(minimum_battery_capacity_kwh=minimum_battery_capacity_kwh)


@pytest.mark.parametrize("roof_fraction", [0.0, -0.1, 1.1])
def test_minimum_roof_fraction_must_be_in_valid_range(roof_fraction):
  with pytest.raises(ValueError):
    valid_constraints(minimum_roof_length_fraction_of_loa=roof_fraction)
