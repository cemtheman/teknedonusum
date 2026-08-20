"""Convert daily propulsion energy to a nominal battery-capacity envelope."""

from math import isfinite

from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.battery_capacity_envelope import (
    NominalBatteryCapacityEnvelopeResult,
)
from models.operational_energy_envelope import (
    DailyPropulsionElectricalEnergyEnvelopeResult,
)
from models.route_energy import RoutePropulsionEnergyEnvelopeResult


def _validate_battery_fractions(
    usable_soc_fraction: float,
    reserve_fraction: float,
) -> None:
  if not isfinite(usable_soc_fraction) or not 0 < usable_soc_fraction <= 1:
    raise ValueError(
        "usable_soc_fraction must be finite, positive, and at most one"
    )
  if not isfinite(reserve_fraction) or not 0 <= reserve_fraction < 1:
    raise ValueError(
        "reserve_fraction must be finite, non-negative, and less than one"
    )


def _build_nominal_battery_capacity_envelope(
    *,
    vessel_id: str,
    speed_knots: float,
    minimum_energy_kwh: float,
    reference_energy_kwh: float,
    maximum_energy_kwh: float,
    usable_soc_fraction: float,
    reserve_fraction: float,
) -> NominalBatteryCapacityEnvelopeResult:
  _validate_battery_fractions(
      usable_soc_fraction,
      reserve_fraction,
  )

  if not minimum_energy_kwh <= reference_energy_kwh <= maximum_energy_kwh:
    raise ValueError("daily energy values must be ordered")

  effective_fraction = usable_soc_fraction * (1.0 - reserve_fraction)

  return NominalBatteryCapacityEnvelopeResult(
      vessel_id=vessel_id,
      speed_knots=speed_knots,
      min_daily_energy_kwh=minimum_energy_kwh,
      reference_daily_energy_kwh=reference_energy_kwh,
      max_daily_energy_kwh=maximum_energy_kwh,
      usable_soc_fraction=usable_soc_fraction,
      reserve_fraction=reserve_fraction,
      effective_usable_energy_fraction=effective_fraction,
      min_nominal_battery_capacity_kwh=minimum_energy_kwh / effective_fraction,
      reference_nominal_battery_capacity_kwh=(
          reference_energy_kwh / effective_fraction
      ),
      max_nominal_battery_capacity_kwh=maximum_energy_kwh / effective_fraction,
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
  """Apply usable-energy and reserve fractions to legacy normative energy."""
  if not isinstance(
      energy_envelope,
      DailyPropulsionElectricalEnergyEnvelopeResult,
  ):
    raise TypeError(
        "energy_envelope must be a "
        "DailyPropulsionElectricalEnergyEnvelopeResult"
    )

  return _build_nominal_battery_capacity_envelope(
      vessel_id=energy_envelope.vessel_id,
      speed_knots=energy_envelope.speed_knots,
      minimum_energy_kwh=energy_envelope.min_daily_electrical_energy_kwh,
      reference_energy_kwh=(
          energy_envelope.reference_daily_electrical_energy_kwh
      ),
      maximum_energy_kwh=energy_envelope.max_daily_electrical_energy_kwh,
      usable_soc_fraction=usable_soc_fraction,
      reserve_fraction=reserve_fraction,
  )


def calculate_route_based_battery_capacity_envelope(
    route_energy: RoutePropulsionEnergyEnvelopeResult,
    usable_soc_fraction: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.usable_energy_fraction
    ),
    reserve_fraction: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.operational_reserve_fraction
    ),
) -> NominalBatteryCapacityEnvelopeResult:
  """Size nominal battery capacity from route-based propulsion energy."""
  if not isinstance(route_energy, RoutePropulsionEnergyEnvelopeResult):
    raise TypeError(
        "route_energy must be a RoutePropulsionEnergyEnvelopeResult"
    )

  return _build_nominal_battery_capacity_envelope(
      vessel_id=route_energy.vessel_id,
      speed_knots=route_energy.speed_knots,
      minimum_energy_kwh=route_energy.min_daily_propulsion_energy_kwh,
      reference_energy_kwh=route_energy.reference_daily_propulsion_energy_kwh,
      maximum_energy_kwh=route_energy.max_daily_propulsion_energy_kwh,
      usable_soc_fraction=usable_soc_fraction,
      reserve_fraction=reserve_fraction,
  )