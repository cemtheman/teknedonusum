from dataclasses import FrozenInstanceError

import pytest

from calculations.electrical_power_envelope import (
    convert_to_electrical_input_power_envelope,
)
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
from models.operational_energy_envelope import OperationalEnergyAssumption
from models.power_envelope import InstalledMechanicalPowerEnvelopeResult


def assumption(hours=8.0, duty_cycle=0.75):
  return OperationalEnergyAssumption(
      operating_hours_per_day=hours,
      duty_cycle=duty_cycle,
      assumption_status="test preliminary assumption",
      provenance="test source",
  )


def daily(vessel_id, speed_knots, operation=None):
  mechanical = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      speed_knots,
  )
  electrical = convert_to_electrical_input_power_envelope(mechanical)
  return calculate_daily_propulsion_energy_envelope(
      vessel_id,
      electrical,
      operation or NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
  )


def test_models_are_immutable():
  operation = assumption()
  result = daily("v1", 6.0, operation)

  with pytest.raises(FrozenInstanceError):
    operation.duty_cycle = 1.0
  with pytest.raises(FrozenInstanceError):
    result.vessel_id = "changed"


def test_exact_energy_conversion_and_fractional_duty_cycle():
  mechanical = InstalledMechanicalPowerEnvelopeResult(
      speed_knots=6.0,
      min_installed_mechanical_power_kw=20.0,
      max_installed_mechanical_power_kw=40.0,
      reference_installed_power_kw=30.0,
  )
  electrical = convert_to_electrical_input_power_envelope(mechanical, 1.0)
  result = calculate_daily_propulsion_energy_envelope(
      "test",
      electrical,
      assumption(8.0, 0.75),
  )

  assert result.effective_powered_hours_per_day == 6.0
  assert result.min_daily_electrical_energy_kwh == 120.0
  assert result.reference_daily_electrical_energy_kwh == 180.0
  assert result.max_daily_electrical_energy_kwh == 240.0


def test_duty_cycle_one_and_24_hour_boundary():
  result = daily("v1", 6.0, assumption(24.0, 1.0))

  assert result.effective_powered_hours_per_day == 24.0
  assert result.max_daily_electrical_energy_kwh == pytest.approx(
      result.max_electrical_input_power_kw * 24.0
  )


@pytest.mark.parametrize("hours", (0.0, -1.0, 24.01, float("nan")))
def test_invalid_operating_hours_are_rejected(hours):
  with pytest.raises(ValueError, match="operating_hours_per_day"):
    assumption(hours=hours)


@pytest.mark.parametrize("duty_cycle", (0.0, -0.1, 1.01, float("inf")))
def test_invalid_duty_cycle_is_rejected(duty_cycle):
  with pytest.raises(ValueError, match="duty_cycle"):
    assumption(duty_cycle=duty_cycle)


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected"),
    (
        ("v1", 6.0, (20 / .95 * 6, 30 / .95 * 6, 40 / .95 * 6)),
        ("v2", 8.0, (30 / .95 * 6, 42.5 / .95 * 6, 55 / .95 * 6)),
        ("v3", 10.0, (60 / .95 * 6, 75 / .95 * 6, 90 / .95 * 6)),
    ),
)
def test_normative_power_envelope_compatibility(
    vessel_id,
    speed_knots,
    expected,
):
  result = daily(vessel_id, speed_knots)

  assert result.min_daily_electrical_energy_kwh == pytest.approx(expected[0])
  assert result.reference_daily_electrical_energy_kwh == pytest.approx(expected[1])
  assert result.max_daily_electrical_energy_kwh == pytest.approx(expected[2])
  assert (
      result.min_daily_electrical_energy_kwh
      <= result.reference_daily_electrical_energy_kwh
      <= result.max_daily_electrical_energy_kwh
  )
  assert result.effective_powered_hours_per_day <= result.operating_hours_per_day
