from types import SimpleNamespace

import pytest

from calculations.vessel_detail_analysis import (
    TECHNICAL_PROFILE_BY_VESSEL,
    build_vessel_detail_analysis,
)


def _inputs():
  return SimpleNamespace(
      cruise_speed=6.0,
      daily_miles=35.0,
      sun_hours=8.0,
      operating_days=180,
      diesel_price=81.81,
      elec_price=3.50,
      eur_rate=55.50,
  )


def _spec(hull="monohull"):
  return {
      "hull": hull,
      "loa": 12.0,
      "beam": 3.8,
      "merged": 1,
      "grantRate": 0.55,
      "maxGrant": 3_299_752,
      "totalCost": 5_999_550,
      "batCostEur": 40_000,
  }


def _sizing(vessel_id, speed, distance):
  assert speed == 6.0
  assert distance == 35.0
  return SimpleNamespace(
      vessel_id=vessel_id,
      reference_installed_mechanical_power_kw=30.0,
      reference_electrical_input_power_kw=11.71,
      reference_daily_propulsion_energy_kwh=68.3,
      reference_nominal_battery_capacity_kwh=94.8,
      operating_hours_per_day=35.0 / 6.0,
  )


def test_detail_analysis_uses_v02_energy_for_grid_requirement():
  result = build_vessel_detail_analysis(
      "v1",
      _spec(),
      _inputs(),
      sizing_calculator=_sizing,
  )

  expected_solar = 12.0 * 3.8 * 0.80 * 0.15 * 8.0
  assert result.daily_solar_kwh == pytest.approx(expected_solar)
  assert result.daily_grid_kwh == pytest.approx(68.3 - expected_solar)
  assert result.sizing.reference_nominal_battery_capacity_kwh == pytest.approx(94.8)


def test_v4_profiles_reuse_v1_v2_technical_sizing_without_new_envelopes():
  assert TECHNICAL_PROFILE_BY_VESSEL["v4_24"] == "v1"
  assert TECHNICAL_PROFILE_BY_VESSEL["v4_32"] == "v2"

  result = build_vessel_detail_analysis(
      "v4_24",
      _spec(),
      _inputs(),
      sizing_calculator=_sizing,
  )
  assert result.technical_profile_id == "v1"
  assert result.sizing.vessel_id == "v1"


def test_turnkey_capex_is_not_rebuilt_from_motor_and_battery_unit_costs():
  result = build_vessel_detail_analysis(
      "v1",
      _spec(),
      _inputs(),
      sizing_calculator=_sizing,
  )

  assert result.grant_amount_tl == pytest.approx(3_299_752)
  assert result.net_capex_tl == pytest.approx(5_999_550 - 3_299_752)
  assert not hasattr(result, "motor_cost_tl")
  assert not hasattr(result, "hull_cost_tl")
