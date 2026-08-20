from copy import deepcopy

import pytest

from calculations.fleet import calculate_fleet
from calculations.fleet_energy_balance import build_fleet_energy_balance
from config.vessels import BASE_VESSEL_SPECS


def default_vessel_specs():
  vessel_specs = deepcopy(BASE_VESSEL_SPECS)
  dynamic_values = {
      "v1": (108100, 5999550, 3299752),
      "v2": (144140, 7999770, 4399873),
      "v3": (180180, 9999990, 6999993),
      "v4_24": (108100, 5999550, 2399820),
      "v4_32": (144140, 7999770, 3199908),
  }
  for vessel_key, values in dynamic_values.items():
    total_cost_eur, total_cost, max_grant = values
    vessel_specs[vessel_key].update({
        "totalCostEur": total_cost_eur,
        "totalCost": total_cost,
        "maxGrant": max_grant,
    })
  return vessel_specs


def test_default_fleet_regression():
  vessel_specs = default_vessel_specs()
  counts = {
      "v1": 50,
      "v2": 50,
      "v3": 40,
      "v4_24": 30,
      "v4_32": 20,
  }

  result = calculate_fleet(
      vessel_specs,
      counts,
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=8.0,
      operating_days=180,
  )

  expected_energy = build_fleet_energy_balance(
      vessel_specs,
      counts,
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=8.0,
      operating_days=180,
  )

  assert result.total_vessels == 190
  assert result.total_capacity == 6320
  assert result.grants_per_type == pytest.approx({
      "v1": 3299752.0,
      "v2": 4399873.0,
      "v3": 6999993.0,
      "v4_24": 2399820.0,
      "v4_32": 3199908.0,
  })
  assert result.fleet_total_cost == pytest.approx(1439947500.0)
  assert result.fleet_total_grant == pytest.approx(800973730.0)
  assert result.fleet_total_capex == pytest.approx(638973770.0)

  assert result.fleet_daily_solar_kwh == pytest.approx(9731.52)
  assert result.fleet_daily_grid_kwh == pytest.approx(
      expected_energy.daily_grid_kwh
  )
  assert result.fleet_daily_brut_kwh == pytest.approx(
      expected_energy.daily_propulsion_kwh
  )
  assert result.fleet_annual_grid_kwh == pytest.approx(
      expected_energy.annual_grid_kwh
  )
  assert result.fleet_annual_solar_kwh == pytest.approx(1751673.6)
  assert result.solar_coverage_ratio == pytest.approx(
      expected_energy.solar_coverage_ratio
  )
  assert result.fleet_total_co2_reduction == pytest.approx(
      expected_energy.total_co2_reduction_tonnes
  )
  assert result.equivalent_trees == expected_energy.equivalent_trees

  # The v0.2 route-based balance must no longer collapse to the legacy
  # "solar exceeds demand, therefore zero grid" result.
  assert result.fleet_daily_grid_kwh > 0
  assert 0 < result.solar_coverage_ratio < 100
