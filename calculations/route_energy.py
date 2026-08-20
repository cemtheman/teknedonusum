"""Calculate daily propulsion energy from route distance and cruise power."""

from math import isfinite

from models.cruise_power import CruisePowerEnvelopeResult
from models.route_energy import RoutePropulsionEnergyEnvelopeResult


def calculate_route_propulsion_energy_envelope(
    cruise_power: CruisePowerEnvelopeResult,
    daily_distance_nm: float,
) -> RoutePropulsionEnergyEnvelopeResult:
  """Use route distance / selected speed as the actual daily cruise duration."""
  if not isinstance(cruise_power, CruisePowerEnvelopeResult):
    raise TypeError("cruise_power must be a CruisePowerEnvelopeResult")

  if not isfinite(daily_distance_nm) or daily_distance_nm <= 0:
    raise ValueError("daily_distance_nm must be finite and positive")

  cruise_hours = daily_distance_nm / cruise_power.speed_knots

  minimum = cruise_power.min_cruise_electrical_power_kw
  reference = cruise_power.reference_cruise_electrical_power_kw
  maximum = cruise_power.max_cruise_electrical_power_kw

  return RoutePropulsionEnergyEnvelopeResult(
      vessel_id=cruise_power.vessel_id,
      speed_knots=cruise_power.speed_knots,
      daily_distance_nm=daily_distance_nm,
      cruise_hours_per_day=cruise_hours,
      min_cruise_electrical_power_kw=minimum,
      reference_cruise_electrical_power_kw=reference,
      max_cruise_electrical_power_kw=maximum,
      min_daily_propulsion_energy_kwh=minimum * cruise_hours,
      reference_daily_propulsion_energy_kwh=reference * cruise_hours,
      max_daily_propulsion_energy_kwh=maximum * cruise_hours,
  )