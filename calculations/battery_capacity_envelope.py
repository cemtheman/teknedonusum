"""Convert daily propulsion energy to a nominal battery-capacity envelope."""

from math import isfinite

from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.battery_capacity_envelope import (
    NominalBatteryCapacityEnvelopeResult,
)
from models.operational_energy_envelope import (
    DailyPropulsionElectricalEnergyEnvelopeResult,
)


def calculate_nominal_battery_capacity_envelope(
    energy_envelope: DailyPropulsionElectricalEnergyEnvelopeResult,
    usable_soc_fraction: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.usable_energy_fraction
    ),
    reserve_fraction: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.operational_reserve_fraction
    ),
) -> NominalBatteryCapacityEnvelopeResult:
  """Apply usable-energy and reserve fractions exactly once."""
  if not isinstance(
      energy_envelope,
      DailyPropulsionElectricalEnergyEnvelopeResult,
  ):
    raise TypeError(
        "energy_envelope must be a "
        "DailyPropulsionElectricalEnergyEnvelopeResult"
    )
  if not isfinite(usable_soc_fraction) or not 0 < usable_soc_fraction <= 1:
    raise ValueError(
        "usable_soc_fraction must be finite, positive, and at most one"
    )
  if not isfinite(reserve_fraction) or not 0 <= reserve_fraction < 1:
    raise ValueError(
        "reserve_fraction must be finite, non-negative, and less than one"
    )

  minimum = energy_envelope.min_daily_electrical_energy_kwh
  reference = energy_envelope.reference_daily_electrical_energy_kwh
  maximum = energy_envelope.max_daily_electrical_energy_kwh
  if not minimum <= reference <= maximum:
    raise ValueError("daily energy values must be ordered")

  effective_fraction = usable_soc_fraction * (1.0 - reserve_fraction)
  return NominalBatteryCapacityEnvelopeResult(
      vessel_id=energy_envelope.vessel_id,
      speed_knots=energy_envelope.speed_knots,
      min_daily_energy_kwh=minimum,
      reference_daily_energy_kwh=reference,
      max_daily_energy_kwh=maximum,
      usable_soc_fraction=usable_soc_fraction,
      reserve_fraction=reserve_fraction,
      effective_usable_energy_fraction=effective_fraction,
      min_nominal_battery_capacity_kwh=minimum / effective_fraction,
      reference_nominal_battery_capacity_kwh=reference / effective_fraction,
      max_nominal_battery_capacity_kwh=maximum / effective_fraction,
  )
