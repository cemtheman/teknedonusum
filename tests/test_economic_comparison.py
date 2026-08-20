from copy import deepcopy

import pytest

from calculations.economic_comparison import (
    VesselEconomicComparisonRow,
    build_vessel_economic_comparison,
)
from calculations.economics import calculate_vessel_economics
from calculations.fleet import calculate_fleet
from calculations.fleet_energy_balance import build_fleet_energy_balance
from calculations.vessel_physics import calc_calibrated_vessel_physics
from config.vessel_factory import build_vessel_specs


BASE_COSTS_EUR = (108100, 144140, 180180)
EXCHANGE_RATE = 55.50


def vessel_specs():
  return build_vessel_specs(*BASE_COSTS_EUR, EXCHANGE_RATE)


def comparison(**overrides):
  inputs = {
      "vessel_specs": vessel_specs(),
      "cruise_speed": 6.0,
      "daily_miles": 35.0,
      "sun_hours": 8.0,
      "season_days": 180,
      "electricity_price": 3.50,
      "diesel_price": 81.81,
      "exchange_rate": EXCHANGE_RATE,
  }
  inputs.update(overrides)
  return build_vessel_economic_comparison(**inputs)


def rows_by_id(rows):
  return {row.vessel_id: row for row in rows}


def test_returns_exactly_v1_v2_v3():
  rows = comparison()

  assert all(isinstance(row, VesselEconomicComparisonRow) for row in rows)
  assert [row.vessel_id for row in rows] == ["v1", "v2", "v3"]


def test_cost_grant_and_net_investment_are_consistent():
  specs = vessel_specs()
  rows = rows_by_id(comparison(vessel_specs=specs))

  for vessel_id in ("v1", "v2", "v3"):
    row = rows[vessel_id]
    spec = specs[vessel_id]
    assert row.investment_cost_tl == spec["totalCost"]
    assert row.grant_amount_tl == min(
        spec["maxGrant"],
        spec["totalCost"] * spec["grantRate"],
    )
    assert row.net_investment_tl == pytest.approx(
        row.investment_cost_tl - row.grant_amount_tl
    )


def test_annual_electrical_energy_uses_season_days():
  short = rows_by_id(comparison(sun_hours=0.0, season_days=90))
  long = rows_by_id(comparison(sun_hours=0.0, season_days=180))

  for vessel_id in ("v1", "v2", "v3"):
    assert long[vessel_id].annual_electrical_energy_requirement_kwh == (
        pytest.approx(
            short[vessel_id].annual_electrical_energy_requirement_kwh * 2
        )
    )


def test_electricity_price_changes_annual_cost_and_saving():
  low = rows_by_id(comparison(sun_hours=0.0, electricity_price=3.5))
  high = rows_by_id(comparison(sun_hours=0.0, electricity_price=7.0))

  for vessel_id in ("v1", "v2", "v3"):
    assert (
        high[vessel_id].annual_electricity_cost_tl
        > low[vessel_id].annual_electricity_cost_tl
    )
    assert (
        high[vessel_id].annual_operating_saving_tl
        < low[vessel_id].annual_operating_saving_tl
    )


def test_diesel_price_changes_baseline_cost_and_saving():
  low = rows_by_id(comparison(diesel_price=50.0))
  high = rows_by_id(comparison(diesel_price=100.0))

  for vessel_id in ("v1", "v2", "v3"):
    assert (
        high[vessel_id].diesel_baseline_annual_fuel_cost_tl
        > low[vessel_id].diesel_baseline_annual_fuel_cost_tl
    )
    assert (
        high[vessel_id].annual_operating_saving_tl
        > low[vessel_id].annual_operating_saving_tl
    )


def test_grant_cap_changes_grant_net_investment_and_payback():
  full_specs = vessel_specs()
  reduced_specs = deepcopy(full_specs)
  reduced_specs["v1"]["maxGrant"] = 1000000
  full = rows_by_id(comparison(vessel_specs=full_specs))["v1"]
  reduced = rows_by_id(comparison(vessel_specs=reduced_specs))["v1"]

  assert reduced.grant_amount_tl == 1000000
  assert reduced.net_investment_tl > full.net_investment_tl
  assert reduced.simple_payback_seasons > full.simple_payback_seasons


def test_non_positive_saving_has_no_meaningful_payback():
  rows = comparison(
      sun_hours=0.0,
      electricity_price=1000.0,
      diesel_price=0.0,
  )

  assert all(row.annual_operating_saving_tl <= 0 for row in rows)
  assert all(row.simple_payback_seasons is None for row in rows)


def test_legacy_economics_remains_stable_while_fleet_uses_v02_energy():
  specs = vessel_specs()
  physics = calc_calibrated_vessel_physics(specs["v1"], 6.0, 35.0, 8.0)
  economics = calculate_vessel_economics(
      specs["v1"],
      physics,
      EXCHANGE_RATE,
      81.81,
      3.50,
      180,
  )
  counts = {"v1": 50, "v2": 50, "v3": 40, "v4_24": 30, "v4_32": 20}
  fleet = calculate_fleet(specs, counts, 6.0, 35.0, 8.0, 180)
  expected_energy = build_fleet_energy_balance(
      specs, counts, 6.0, 35.0, 8.0, 180
  )

  assert economics.net_savings == pytest.approx(540019.9295150795)
  assert economics.payback_seasons == pytest.approx(4.9994414139943535)
  assert economics.net_co2 == pytest.approx(15.643879933281948)

  assert fleet.fleet_daily_solar_kwh == pytest.approx(
      expected_energy.daily_solar_kwh
  )
  assert fleet.fleet_daily_grid_kwh == pytest.approx(
      expected_energy.daily_grid_kwh
  )
  assert fleet.fleet_daily_brut_kwh == pytest.approx(
      expected_energy.daily_propulsion_kwh
  )
  assert fleet.fleet_daily_grid_kwh > 0
