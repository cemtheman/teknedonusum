"""Convert propulsion electrical-input power to a daily energy envelope."""

from models.electrical_power_envelope import ElectricalInputPowerEnvelopeResult
from models.operational_energy_envelope import (
    DailyPropulsionElectricalEnergyEnvelopeResult,
    OperationalEnergyAssumption,
)


def calculate_daily_propulsion_energy_envelope(
    vessel_id: str,
    electrical_envelope: ElectricalInputPowerEnvelopeResult,
    operation: OperationalEnergyAssumption,
) -> DailyPropulsionElectricalEnergyEnvelopeResult:
  """Apply an explicit operating window and duty cycle to each power bound."""
  if not vessel_id:
    raise ValueError("vessel_id must not be empty")
  if not isinstance(electrical_envelope, ElectricalInputPowerEnvelopeResult):
    raise TypeError(
        "electrical_envelope must be an ElectricalInputPowerEnvelopeResult"
    )
  if not isinstance(operation, OperationalEnergyAssumption):
    raise TypeError("operation must be an OperationalEnergyAssumption")

  minimum = electrical_envelope.min_electrical_input_power_kw
  reference = electrical_envelope.reference_electrical_input_power_kw
  maximum = electrical_envelope.max_electrical_input_power_kw
  if not minimum <= reference <= maximum:
    raise ValueError("electrical power values must be ordered")

  effective_hours = operation.operating_hours_per_day * operation.duty_cycle
  return DailyPropulsionElectricalEnergyEnvelopeResult(
      vessel_id=vessel_id,
      speed_knots=electrical_envelope.speed_knots,
      min_electrical_input_power_kw=minimum,
      reference_electrical_input_power_kw=reference,
      max_electrical_input_power_kw=maximum,
      operating_hours_per_day=operation.operating_hours_per_day,
      duty_cycle=operation.duty_cycle,
      effective_powered_hours_per_day=effective_hours,
      min_daily_electrical_energy_kwh=minimum * effective_hours,
      reference_daily_electrical_energy_kwh=reference * effective_hours,
      max_daily_electrical_energy_kwh=maximum * effective_hours,
  )
