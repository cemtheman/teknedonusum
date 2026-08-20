from datetime import date

from models.inputs import SimulationInputs


def make_simulation_inputs(**overrides):
  """Central test factory for the current SimulationInputs contract."""
  values = {
      "count_v1": 50,
      "count_v2": 50,
      "count_v3": 40,
      "count_v4_24": 30,
      "count_v4_32": 20,
      "cost_eur_v1": 108100,
      "cost_eur_v2": 144140,
      "cost_eur_v3": 180180,
      "eur_rate": 55.5,
      "diesel_price": 81.81,
      "elec_price": 3.5,
      "operating_days": 150,
      "daily_miles": 35.0,
      "cruise_speed": 6.0,
      "location_name": "Dalyan, Ortaca, Muğla, Türkiye",
      "latitude": 36.8350,
      "longitude": 28.6424,
      "season_start": date(2026, 4, 1),
      "season_end": date(2026, 9, 30),
      "season_days": 183,
      "average_daily_specific_yield_kwh_per_kwp": 5.0,
      "season_specific_yield_kwh_per_kwp": 915.0,
      "solar_resource_source": "test fixture",
      "sun_hours": None,
  }
  values.update(overrides)
  return SimulationInputs(**values)
