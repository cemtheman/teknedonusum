"""Traceable hourly solar-assisted propulsion power-flow results."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True)
class HourlyPVPoint:
  timestamp: datetime
  specific_power_kw_per_kwp: float

  def __post_init__(self):
    if not isinstance(self.timestamp, datetime):
      raise TypeError("timestamp must be datetime")
    if not isfinite(self.specific_power_kw_per_kwp):
      raise ValueError("specific PV power must be finite")
    if self.specific_power_kw_per_kwp < 0:
      raise ValueError("specific PV power must not be negative")


@dataclass(frozen=True)
class PropulsionPowerSplit:
  propulsion_demand_kw: float
  solar_available_kw: float
  solar_to_propulsion_kw: float
  battery_discharge_kw: float
  solar_surplus_kw: float
  solar_only_propulsion: bool

  def __post_init__(self):
    values = (
        self.propulsion_demand_kw,
        self.solar_available_kw,
        self.solar_to_propulsion_kw,
        self.battery_discharge_kw,
        self.solar_surplus_kw,
    )
    if any(not isfinite(value) or value < 0 for value in values):
      raise ValueError("power-flow values must be finite and non-negative")
    if self.solar_to_propulsion_kw > self.propulsion_demand_kw:
      raise ValueError("solar-to-propulsion cannot exceed propulsion demand")
    if self.solar_to_propulsion_kw > self.solar_available_kw:
      raise ValueError("solar-to-propulsion cannot exceed available solar power")
