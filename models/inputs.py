from dataclasses import dataclass


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
  sun_hours: float
  daily_miles: float
  cruise_speed: float
