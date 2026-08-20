"""Immutable nominal battery-capacity envelope result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class NominalBatteryCapacityEnvelopeResult:
  vessel_id: str
  speed_knots: float
  min_daily_energy_kwh: float
  reference_daily_energy_kwh: float
  max_daily_energy_kwh: float
  usable_soc_fraction: float
  reserve_fraction: float
  effective_usable_energy_fraction: float
  min_nominal_battery_capacity_kwh: float
  reference_nominal_battery_capacity_kwh: float
  max_nominal_battery_capacity_kwh: float

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")
    if not isfinite(self.speed_knots) or self.speed_knots < 0:
      raise ValueError("speed_knots must be finite and non-negative")
    if not isfinite(self.usable_soc_fraction) or not 0 < self.usable_soc_fraction <= 1:
      raise ValueError(
          "usable_soc_fraction must be finite, positive, and at most one"
      )
    if not isfinite(self.reserve_fraction) or not 0 <= self.reserve_fraction < 1:
      raise ValueError(
          "reserve_fraction must be finite, non-negative, and less than one"
      )
    if (
        not isfinite(self.effective_usable_energy_fraction)
        or not 0 < self.effective_usable_energy_fraction <= 1
    ):
      raise ValueError(
          "effective_usable_energy_fraction must be finite, positive, and "
          "at most one"
      )

    energy = (
        self.min_daily_energy_kwh,
        self.reference_daily_energy_kwh,
        self.max_daily_energy_kwh,
    )
    capacity = (
        self.min_nominal_battery_capacity_kwh,
        self.reference_nominal_battery_capacity_kwh,
        self.max_nominal_battery_capacity_kwh,
    )
    if any(not isfinite(value) or value <= 0 for value in energy + capacity):
      raise ValueError("energy and capacity values must be finite and positive")
    if not energy[0] <= energy[1] <= energy[2]:
      raise ValueError("daily energy values must be ordered")
    if not capacity[0] <= capacity[1] <= capacity[2]:
      raise ValueError("nominal battery capacity values must be ordered")
    if any(nominal < daily for nominal, daily in zip(capacity, energy)):
      raise ValueError("nominal battery capacity must not be below daily energy")
