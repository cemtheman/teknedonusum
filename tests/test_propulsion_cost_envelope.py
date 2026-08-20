from dataclasses import FrozenInstanceError, replace

import pytest

from calculations.battery_capacity_envelope import (
    calculate_nominal_battery_capacity_envelope,
)
from calculations.electrical_power_envelope import (
    convert_to_electrical_input_power_envelope,
)
from calculations.operational_energy_envelope import (
    calculate_daily_propulsion_energy_envelope,
)
from calculations.power_envelope import (
    interpolate_installed_mechanical_power_envelope,
)
from calculations.propulsion_cost_envelope import (
    calculate_propulsion_system_cost_envelope,
)
from config.normative_operational_profiles import (
    NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
)
from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from config.vessels import BASE_VESSEL_SPECS


def envelopes(vessel_id, speed_knots):
  power = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      speed_knots,
  )
  electrical = convert_to_electrical_input_power_envelope(power)
  energy = calculate_daily_propulsion_energy_envelope(
      vessel_id,
      electrical,
      NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
  )
  battery = calculate_nominal_battery_capacity_envelope(energy)
  return power, battery


def cost(vessel_id, speed_knots):
  power, battery = envelopes(vessel_id, speed_knots)
  return calculate_propulsion_system_cost_envelope(
      vessel_id,
      power,
      battery,
  )


def test_result_is_immutable():
  result = cost("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.currency = "TRY"


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "motor_count", "multiplier"),
    (("v1", 6.0, 1, 1.0), ("v2", 8.0, 2, 1.2), ("v3", 10.0, 2, 1.2)),
)
def test_normative_envelope_costs(
    vessel_id,
    speed_knots,
    motor_count,
    multiplier,
):
  power, battery = envelopes(vessel_id, speed_knots)
  result = calculate_propulsion_system_cost_envelope(
      vessel_id,
      power,
      battery,
  )

  assert result.currency == "EUR"
  assert result.motor_count == motor_count
  assert result.motor_system_multiplier == multiplier
  assert result.motor_cost_per_total_installed_kw == 400.0
  assert result.battery_cost_per_nominal_kwh == 500.0
  assert result.min_motor_system_cost == pytest.approx(
      power.min_installed_mechanical_power_kw * 400 * multiplier
  )
  assert result.reference_motor_system_cost == pytest.approx(
      power.reference_installed_power_kw * 400 * multiplier
  )
  assert result.max_motor_system_cost == pytest.approx(
      power.max_installed_mechanical_power_kw * 400 * multiplier
  )
  assert result.min_battery_system_cost == pytest.approx(
      battery.min_nominal_battery_capacity_kwh * 500
  )
  assert result.reference_battery_system_cost == pytest.approx(
      battery.reference_nominal_battery_capacity_kwh * 500
  )
  assert result.max_battery_system_cost == pytest.approx(
      battery.max_nominal_battery_capacity_kwh * 500
  )
  assert result.reference_total_propulsion_system_cost == pytest.approx(
      result.reference_motor_system_cost + result.reference_battery_system_cost
  )
  assert (
      result.min_total_propulsion_system_cost
      <= result.reference_total_propulsion_system_cost
      <= result.max_total_propulsion_system_cost
  )


def test_twin_motor_uses_total_power_once():
  power, battery = envelopes("v2", 8.0)
  result = calculate_propulsion_system_cost_envelope("v2", power, battery)

  assert power.reference_installed_power_kw == 42.5
  assert result.reference_motor_system_cost == pytest.approx(42.5 * 400 * 1.2)
  assert result.reference_motor_system_cost != pytest.approx(
      42.5 * 2 * 400 * 1.2
  )


def test_existing_cost_assumption_sources_are_compatible():
  for vessel_id in ("v1", "v2", "v3"):
    result = cost(vessel_id, 6.0)
    spec = BASE_VESSEL_SPECS[vessel_id]

    assert result.motor_count == spec["motors"]
    assert result.battery_cost_per_nominal_kwh == (
        spec["batCostEur"] / spec["batCapacity"]
    )
    assert "calculations/economics.py" in result.cost_basis_provenance


def test_model_rejects_negative_unit_cost():
  result = cost("v1", 6.0)

  with pytest.raises(ValueError, match="unit costs"):
    replace(result, battery_cost_per_nominal_kwh=-1.0)


def test_conversion_rejects_zero_power_or_capacity():
  power, battery = envelopes("v1", 6.0)

  with pytest.raises(ValueError, match="power and battery"):
    calculate_propulsion_system_cost_envelope(
        "v1",
        replace(power, min_installed_mechanical_power_kw=0.0),
        battery,
    )
  with pytest.raises(ValueError, match="capacity"):
    calculate_propulsion_system_cost_envelope(
        "v1",
        power,
        replace(battery, min_nominal_battery_capacity_kwh=0.0),
    )


def test_mismatched_identity_and_speed_are_rejected():
  v1_power, v1_battery = envelopes("v1", 6.0)
  v2_power, _ = envelopes("v2", 8.0)

  with pytest.raises(ValueError, match="vessel_id"):
    calculate_propulsion_system_cost_envelope(
        "v2",
        v1_power,
        v1_battery,
    )
  with pytest.raises(ValueError, match="speeds"):
    calculate_propulsion_system_cost_envelope(
        "v1",
        v2_power,
        v1_battery,
    )
