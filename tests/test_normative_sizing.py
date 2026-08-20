from dataclasses import FrozenInstanceError

import pytest

from calculations.normative_sizing import calculate_normative_sizing


def test_result_is_immutable():
  result = calculate_normative_sizing("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.selected_speed_knots = 8.0


@pytest.mark.parametrize("vessel_id", ("v1", "v2", "v3"))
@pytest.mark.parametrize("speed_knots", (6.0, 8.0, 10.0))
def test_all_normative_anchor_full_chains(vessel_id, speed_knots):
  result = calculate_normative_sizing(vessel_id, speed_knots)

  assert result.vessel_id == vessel_id
  assert result.selected_speed_knots == speed_knots
  for group in (
      (
          result.min_installed_mechanical_power_kw,
          result.reference_installed_mechanical_power_kw,
          result.max_installed_mechanical_power_kw,
      ),
      (
          result.min_electrical_input_power_kw,
          result.reference_electrical_input_power_kw,
          result.max_electrical_input_power_kw,
      ),
      (
          result.min_daily_propulsion_energy_kwh,
          result.reference_daily_propulsion_energy_kwh,
          result.max_daily_propulsion_energy_kwh,
      ),
      (
          result.min_nominal_battery_capacity_kwh,
          result.reference_nominal_battery_capacity_kwh,
          result.max_nominal_battery_capacity_kwh,
      ),
      (
          result.min_propulsion_system_cost,
          result.reference_propulsion_system_cost,
          result.max_propulsion_system_cost,
      ),
  ):
    assert group[0] <= group[1] <= group[2]


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots"),
    (("v1", 7.0), ("v1", 9.0), ("v2", 7.0), ("v3", 9.0)),
)
def test_interpolated_speed_full_chain(vessel_id, speed_knots):
  result = calculate_normative_sizing(vessel_id, speed_knots)

  assert result.selected_speed_knots == speed_knots
  assert result.min_propulsion_system_cost > 0


@pytest.mark.parametrize("vessel_id", ("", "v4", "V1"))
def test_unsupported_vessel_is_rejected(vessel_id):
  with pytest.raises(ValueError, match="vessel_id"):
    calculate_normative_sizing(vessel_id, 6.0)


@pytest.mark.parametrize("speed_knots", (5.0, 11.0))
def test_out_of_range_speed_is_rejected(speed_knots):
  with pytest.raises(ValueError, match="within profile range"):
    calculate_normative_sizing("v1", speed_knots)


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected"),
    (
        (
            "v1",
            6.0,
            (30.0, 11.703796755532077, 68.27214774060377, 94.82242741750522, 59411.21370875261),
        ),
        (
            "v2",
            8.0,
            (42.5, 36.22398407799687, 158.4799303412363, 220.11101436282817, 130455.50718141408),
        ),
        (
            "v3",
            10.0,
            (75.0, 78.94736842105263, 276.3157894736842, 383.77192982456137, 227885.96491228067),
        ),
    ),
)
def test_commit_51_to_55_reference_regressions(
    vessel_id,
    speed_knots,
    expected,
):
  result = calculate_normative_sizing(vessel_id, speed_knots)

  actual = (
      result.reference_installed_mechanical_power_kw,
      result.reference_electrical_input_power_kw,
      result.reference_daily_propulsion_energy_kwh,
      result.reference_nominal_battery_capacity_kwh,
      result.reference_propulsion_system_cost,
  )
  assert actual == pytest.approx(expected)


def test_relationships_and_assumption_traceability():
  result = calculate_normative_sizing("v2", 8.0)

  assert result.reference_cruise_mechanical_power_kw <= (
      result.reference_installed_mechanical_power_kw
  )
  assert result.reference_electrical_input_power_kw == pytest.approx(
      result.reference_cruise_mechanical_power_kw / result.motor_efficiency
  )
  assert result.reference_daily_propulsion_energy_kwh == pytest.approx(
      result.reference_electrical_input_power_kw
      * result.effective_powered_hours_per_day
  )
  assert result.reference_nominal_battery_capacity_kwh >= (
      result.reference_daily_propulsion_energy_kwh
  )
  assert result.motor_efficiency == 0.95
  assert result.operating_hours_per_day == pytest.approx(35.0 / 8.0)
  assert result.duty_cycle == 1.0
  assert result.usable_energy_fraction == 0.90
  assert result.reserve_fraction == 0.20
  assert result.motor_count == 2
  assert result.motor_system_multiplier == 1.20
  assert result.motor_unit_cost_per_total_installed_kw == 400.0
  assert result.battery_unit_cost_per_nominal_kwh == 500.0
  assert result.currency == "EUR"
  assert "preliminary" in result.assumption_status
  assert result.limitations
