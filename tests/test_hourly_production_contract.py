from datetime import date

import pytest

from calculations.fleet_energy_balance import build_fleet_energy_balance


def _spec():
  return {
      "v1": {
          "loa": 12.0,
          "beam": 3.2,
          "hull": "monohull",
          "merged": 1,
      }
  }


def _hourly_profile(value):
  return {
      (6, 1, hour): value
      for hour in range(24)
  }


def test_hourly_production_path_allows_pv_generation_above_propulsion_demand():
  result = build_fleet_energy_balance(
      vessel_specs=_spec(),
      counts={"v1": 1},
      cruise_speed=6.0,
      daily_miles=5.0,
      sun_hours=None,
      operating_days=1,
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=_hourly_profile(1.0),
  )

  assert result.daily_solar_kwh > result.daily_propulsion_kwh
  assert result.daily_grid_kwh >= 0.0
  assert result.annual_grid_kwh == pytest.approx(result.daily_grid_kwh)


def test_hourly_production_path_reports_bounded_shore_avoidance_ratio():
  result = build_fleet_energy_balance(
      vessel_specs=_spec(),
      counts={"v1": 1},
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=None,
      operating_days=1,
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=_hourly_profile(0.0),
  )

  assert 0.0 <= result.solar_coverage_ratio <= 100.0
  assert result.annual_grid_kwh >= 0.0
