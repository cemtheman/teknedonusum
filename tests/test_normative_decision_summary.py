from dataclasses import FrozenInstanceError

import pytest

from calculations.normative_decision_summary import (
    build_normative_decision_summary,
)
from calculations.normative_sizing import calculate_normative_sizing


def summary(vessel_id, speed_knots):
  sizing = calculate_normative_sizing(vessel_id, speed_knots)
  return sizing, build_normative_decision_summary(sizing)


def test_summary_and_assumptions_are_immutable():
  _, result = summary("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.vessel_id = "changed"
  with pytest.raises(FrozenInstanceError):
    result.assumptions.duty_cycle = 1.0


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots"),
    (("v1", 6.0), ("v2", 8.0), ("v3", 10.0), ("v1", 7.0), ("v3", 9.0)),
)
def test_sizing_values_are_copied_exactly(vessel_id, speed_knots):
  sizing, result = summary(vessel_id, speed_knots)

  assert result.vessel_id == sizing.vessel_id
  assert result.vessel_type == sizing.vessel_type
  assert result.selected_speed_knots == sizing.selected_speed_knots
  assert result.profile_version == sizing.profile_version
  assert (
      result.min_envelope_installed_mechanical_power_kw
      == sizing.min_installed_mechanical_power_kw
  )
  assert (
      result.reference_estimate_installed_mechanical_power_kw
      == sizing.reference_installed_mechanical_power_kw
  )
  assert (
      result.max_envelope_installed_mechanical_power_kw
      == sizing.max_installed_mechanical_power_kw
  )
  assert result.reference_electrical_input_power_kw == (
      sizing.reference_electrical_input_power_kw
  )
  assert result.reference_estimate_daily_propulsion_energy_kwh == (
      sizing.reference_daily_propulsion_energy_kwh
  )
  assert result.reference_estimate_nominal_battery_capacity_kwh == (
      sizing.reference_nominal_battery_capacity_kwh
  )
  assert result.reference_estimate_propulsion_system_cost == (
      sizing.reference_propulsion_system_cost
  )
  assert result.currency == sizing.currency


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected"),
    (
        ("v1", 6.0, (30.0, 189.47368421052633, 263.1578947368421, 143578.94736842104)),
        ("v2", 8.0, (42.5, 268.42105263157896, 372.8070175438596, 206803.5087719298)),
        ("v3", 10.0, (75.0, 473.6842105263158, 657.8947368421052, 364947.3684210526)),
    ),
)
def test_commit_56_reference_regression(vessel_id, speed_knots, expected):
  _, result = summary(vessel_id, speed_knots)

  actual = (
      result.reference_estimate_installed_mechanical_power_kw,
      result.reference_estimate_daily_propulsion_energy_kwh,
      result.reference_estimate_nominal_battery_capacity_kwh,
      result.reference_estimate_propulsion_system_cost,
  )
  assert actual == pytest.approx(expected)


def test_assumption_snapshot_status_limitations_and_twin_flag():
  _, result = summary("v2", 8.0)
  assumptions = result.assumptions

  assert assumptions.motor_efficiency == 0.95
  assert assumptions.operating_hours_per_day == 8.0
  assert assumptions.duty_cycle == 0.75
  assert assumptions.effective_powered_hours_per_day == 6.0
  assert assumptions.usable_energy_fraction == 0.90
  assert assumptions.reserve_fraction == 0.20
  assert assumptions.effective_usable_energy_fraction == pytest.approx(0.72)
  assert assumptions.motor_unit_cost_per_total_installed_kw == 400.0
  assert assumptions.battery_unit_cost_per_nominal_kwh == 500.0
  assert assumptions.motor_system_multiplier == 1.20
  assert result.preliminary_only is True
  assert result.externally_validated is False
  assert result.twin_motor_configuration is True
  assert result.currency == "EUR"
  assert "preliminary" in result.methodology_status
  assert "non-certified" in result.validation_status
  assert "not_sea_trial_validated" in result.limitation_ids
  assert "auxiliary_and_hotel_loads_excluded" in result.limitation_ids


def test_monohull_is_not_marked_as_twin_motor():
  _, result = summary("v1", 6.0)

  assert result.twin_motor_configuration is False


def test_summary_envelopes_remain_ordered():
  _, result = summary("v3", 9.0)

  assert (
      result.min_envelope_installed_mechanical_power_kw
      <= result.reference_estimate_installed_mechanical_power_kw
      <= result.max_envelope_installed_mechanical_power_kw
  )
  assert (
      result.min_envelope_daily_propulsion_energy_kwh
      <= result.reference_estimate_daily_propulsion_energy_kwh
      <= result.max_envelope_daily_propulsion_energy_kwh
  )
  assert (
      result.min_envelope_nominal_battery_capacity_kwh
      <= result.reference_estimate_nominal_battery_capacity_kwh
      <= result.max_envelope_nominal_battery_capacity_kwh
  )
  assert (
      result.min_envelope_propulsion_system_cost
      <= result.reference_estimate_propulsion_system_cost
      <= result.max_envelope_propulsion_system_cost
  )
