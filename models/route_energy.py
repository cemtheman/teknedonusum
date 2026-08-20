"""Immutable route-based propulsion energy result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class RoutePropulsionEnergyEnvelopeResult:
  vessel_id: str
  speed_knots: float
  daily_distance_nm: float
  cruise_hours_per_day: float
  min_cruise_electrical_power_kw: float
  reference_cruise_electrical_power_kw: float
  max_cruise_electrical_power_kw: float
  min_daily_propulsion_energy_kwh: float
  reference_daily_propulsion_energy_kwh: float
  max_daily_propulsion_energy_kwh: float

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")

    positive_values = (
        self.speed_knots,
        self.daily_distance_nm,
        self.cruise_hours_per_day,
        self.min_cruise_electrical_power_kw,
        self.reference_cruise_electrical_power_kw,
        self.max_cruise_electrical_power_kw,
        self.min_daily_propulsion_energy_kwh,
        self.reference_daily_propulsion_energy_kwh,
        self.max_daily_propulsion_energy_kwh,
    )
    if any(not isfinite(value) or value <= 0 for value in positive_values):
      raise ValueError("route energy values must be finite and positive")

    power = (
        self.min_cruise_electrical_power_kw,
        self.reference_cruise_electrical_power_kw,
        self.max_cruise_electrical_power_kw,
    )
    energy = (
        self.min_daily_propulsion_energy_kwh,
        self.reference_daily_propulsion_energy_kwh,
        self.max_daily_propulsion_energy_kwh,
    )

    if not power[0] <= power[1] <= power[2]:
      raise ValueError("cruise electrical power values must be ordered")
    if not energy[0] <= energy[1] <= energy[2]:
      raise ValueError("daily propulsion energy values must be ordered")