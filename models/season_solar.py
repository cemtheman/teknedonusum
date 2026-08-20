"""Traceable location/date-specific seasonal solar resource result."""

from dataclasses import dataclass
from datetime import date
from math import isfinite


@dataclass(frozen=True)
class SeasonSolarResource:
  location_name: str
  latitude: float
  longitude: float
  season_start: date
  season_end: date
  season_days: int
  average_daily_specific_yield_kwh_per_kwp: float
  season_specific_yield_kwh_per_kwp: float
  source: str

  def __post_init__(self):
    if not self.location_name:
      raise ValueError("location_name must not be empty")
    if self.season_end < self.season_start:
      raise ValueError("season_end must not be before season_start")
    if self.season_days <= 0:
      raise ValueError("season_days must be positive")
    numeric_values = (
        self.latitude,
        self.longitude,
        self.average_daily_specific_yield_kwh_per_kwp,
        self.season_specific_yield_kwh_per_kwp,
    )
    if any(not isfinite(value) for value in numeric_values):
      raise ValueError("solar-resource values must be finite")
    if not -90 <= self.latitude <= 90:
      raise ValueError("latitude must be between -90 and 90")
    if not -180 <= self.longitude <= 180:
      raise ValueError("longitude must be between -180 and 180")
    if self.average_daily_specific_yield_kwh_per_kwp <= 0:
      raise ValueError("average daily specific yield must be positive")
    if self.season_specific_yield_kwh_per_kwp <= 0:
      raise ValueError("season specific yield must be positive")
    if not self.source:
      raise ValueError("source must not be empty")
