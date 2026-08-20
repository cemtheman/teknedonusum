from dataclasses import dataclass
from datetime import date


@dataclass
class SimulationInputs:
  count_v1: int
  count_v2: int
  count_v3: int
  count_v4_24: int
  count_v4_32: int
  cost_eur_v1: float
  cost_eur_v2: float
  cost_eur_v3: float
  eur_rate: float
  diesel_price: float
  elec_price: float
  operating_days: int
  daily_miles: float
  cruise_speed: float
  location_name: str
  latitude: float
  longitude: float
  season_start: date
  season_end: date
  season_days: int
  average_daily_specific_yield_kwh_per_kwp: float
  season_specific_yield_kwh_per_kwp: float
  solar_resource_source: str
  # Transitional compatibility only; primary UI no longer exposes it.
  sun_hours: float | None = None
