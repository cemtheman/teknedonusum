from dataclasses import FrozenInstanceError

import pytest

from calculations.battery_capacity_envelope import (
    calculate_nominal_battery_capacity_envelope,
)
from calculations.electrical_power_envelope import (
    convert_to_electrical_input_power_envelope,
)
from calculations.energy import calculate_navigation_energy
from calculations.operational_energy_envelope import (
    calculate_daily_propulsion_energy_envelope,
)
from calculations.power_envelope import (
    interpolate_installed_mechanical_power_envelope,
)
from config.normative_operational_profiles import (
    NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
)
from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.operational_energy_envelope import (
    DailyPropulsionElectricalEnergyEnvelopeResult,
)


def energy(vessel_id, speed_knots):
  mechanical = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      speed_knots,
  )
  electrical = convert_to_electrical_input_power_envelope(mechanical)
  return calculate_daily_propulsion_energy_envelope(
      vessel_id,
      electrical,
      NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
  )


def direct_energy(minimum=120.0, reference=180.0, maximum=240.0):
  return DailyPropulsionElectricalEnergyEnvelopeResult(
      vessel_id="test",
      speed_knots=6.0,
      min_electrical_input_power_kw=20.0,
      reference_electrical_input_power_kw=30.0,
      max_electrical_input_power_kw=40.0,
      operating_hours_per_day=8.0,
      duty_cycle=0.75,
      effective_powered_hours_per_day=6.0,
      min_daily_electrical_energy_kwh=minimum,
      reference_daily_electrical_energy_kwh=reference,
      max_daily_electrical_energy_kwh=maximum,
  )


def test_result_is_immutable():
  result = calculate_nominal_battery_capacity_envelope(direct_energy())

  with pytest.raises(FrozenInstanceError):
    result.reserve_fraction = 0.1


def test_exact_nominal_capacity_conversion():
  result = calculate_nominal_battery_capacity_envelope(
      direct_energy(),
      usable_soc_fraction=0.80,
      reserve_fraction=0.10,
  )

  assert result.effective_usable_energy_fraction == pytest.approx(0.72)
  assert result.min_nominal_battery_capacity_kwh == pytest.approx(120 / .72)
  assert result.reference_nominal_battery_capacity_kwh == pytest.approx(180 / .72)
  assert result.max_nominal_battery_capacity_kwh == pytest.approx(240 / .72)


def test_fully_usable_without_reserve_is_identity():
  result = calculate_nominal_battery_capacity_envelope(
      direct_energy(),
      usable_soc_fraction=1.0,
      reserve_fraction=0.0,
  )

  assert result.effective_usable_energy_fraction == 1.0
  assert result.min_nominal_battery_capacity_kwh == 120.0
  assert result.reference_nominal_battery_capacity_kwh == 180.0
  assert result.max_nominal_battery_capacity_kwh == 240.0


def test_zero_reserve_applies_only_usable_soc_fraction():
  result = calculate_nominal_battery_capacity_envelope(
      direct_energy(),
      usable_soc_fraction=0.80,
      reserve_fraction=0.0,
  )

  assert result.reference_nominal_battery_capacity_kwh == pytest.approx(225.0)


@pytest.mark.parametrize(
    "usable_soc_fraction",
    (0.0, -0.1, 1.01, float("nan"), float("inf")),
)
def test_invalid_usable_soc_fraction_is_rejected(usable_soc_fraction):
  with pytest.raises(ValueError, match="usable_soc_fraction"):
    calculate_nominal_battery_capacity_envelope(
        direct_energy(),
        usable_soc_fraction=usable_soc_fraction,
    )


@pytest.mark.parametrize(
    "reserve_fraction",
    (-0.1, 1.0, 1.01, float("nan"), float("inf")),
)
def test_invalid_reserve_fraction_is_rejected(reserve_fraction):
  with pytest.raises(ValueError, match="reserve_fraction"):
    calculate_nominal_battery_capacity_envelope(
        direct_energy(),
        reserve_fraction=reserve_fraction,
    )


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots"),
    (("v1", 6.0), ("v2", 8.0), ("v3", 10.0)),
)
def test_normative_operational_energy_compatibility(vessel_id, speed_knots):
  source = energy(vessel_id, speed_knots)
  result = calculate_nominal_battery_capacity_envelope(source)

  assert result.usable_soc_fraction == (
      V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.usable_energy_fraction
  )
  assert result.reserve_fraction == (
      V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.operational_reserve_fraction
  )
  assert result.effective_usable_energy_fraction == pytest.approx(0.72)
  assert (
      result.min_nominal_battery_capacity_kwh
      <= result.reference_nominal_battery_capacity_kwh
      <= result.max_nominal_battery_capacity_kwh
  )
  assert result.min_nominal_battery_capacity_kwh >= result.min_daily_energy_kwh
  assert result.reference_nominal_battery_capacity_kwh >= (
      result.reference_daily_energy_kwh
  )
  assert result.max_nominal_battery_capacity_kwh >= result.max_daily_energy_kwh


def test_existing_battery_semantics_recovers_reference_mission_energy():
  source = energy("v1", 6.0)
  result = calculate_nominal_battery_capacity_envelope(source)
  existing = calculate_navigation_energy(
      speed_knots=6.0,
      battery_capacity_kwh=result.reference_nominal_battery_capacity_kwh,
      propulsion_electrical_power_kw=(
          source.reference_electrical_input_power_kw
      ),
      hotel_load_kw=0.0,
      usable_energy_fraction=result.usable_soc_fraction,
      operational_reserve_fraction=result.reserve_fraction,
  )

  assert existing.mission_energy_kwh == pytest.approx(
      source.reference_daily_electrical_energy_kwh
  )
