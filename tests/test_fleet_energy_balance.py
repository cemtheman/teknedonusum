from copy import deepcopy
from types import SimpleNamespace

import pytest

from calculations.fleet_energy_balance import build_fleet_energy_balance
from config.vessels import BASE_VESSEL_SPECS


def _specs():
  return deepcopy(BASE_VESSEL_SPECS)


def _sizing(vessel_id, speed, distance):
  assert speed == 6.0
  assert distance == 35.0
  values = {
      "v1": 68.3,
      "v2": 93.1,
      "v3": 107.4,
  }
  return SimpleNamespace(
      vessel_id=vessel_id,
      reference_daily_propulsion_energy_kwh=values[vessel_id],
      operating_hours_per_day=35.0 / 6.0,
  )


def test_fleet_energy_aggregates_v02_route_energy_and_per_vessel_grid():
  counts = {
      "v1": 50,
      "v2": 50,
      "v3": 40,
      "v4_24": 30,
      "v4_32": 20,
  }

  result = build_fleet_energy_balance(
      _specs(),
      counts,
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=8.0,
      operating_days=180,
      sizing_calculator=_sizing,
  )

  expected_propulsion = (
      68.3 * 50
      + 93.1 * 50
      + 107.4 * 40
      + 68.3 * 30
      + 93.1 * 20
  )
  expected_solar = (
      (12.0 * 3.8 * 0.80 * 0.15 * 8.0) * 80
      + (13.5 * 4.2 * 0.80 * 0.15 * 8.0) * 70
      + (14.0 * 4.5 * 0.80 * 0.15 * 8.0) * 40
  )
  expected_grid = (
      (68.3 - 43.776) * 80
      + (93.1 - 54.432) * 70
      + (107.4 - 60.48) * 40
  )

  assert result.daily_propulsion_kwh == pytest.approx(expected_propulsion)
  assert result.daily_solar_kwh == pytest.approx(expected_solar)
  assert result.daily_grid_kwh == pytest.approx(expected_grid)
  assert result.solar_coverage_ratio == pytest.approx(
      expected_solar / expected_propulsion * 100.0
  )
  assert result.daily_grid_kwh > 0


def test_v4_technical_profiles_do_not_create_new_sizing_envelopes():
  calls = []

  def sizing(vessel_id, speed, distance):
    calls.append(vessel_id)
    return _sizing(vessel_id, speed, distance)

  counts = {
      "v1": 0,
      "v2": 0,
      "v3": 0,
      "v4_24": 1,
      "v4_32": 1,
  }

  build_fleet_energy_balance(
      _specs(),
      counts,
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=8.0,
      operating_days=180,
      sizing_calculator=sizing,
  )

  assert calls == ["v1", "v2"]
