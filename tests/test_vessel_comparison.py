from copy import deepcopy

import pytest

from calculations.fleet import calculate_fleet
from calculations.fleet_energy_balance import build_fleet_energy_balance
from calculations.vessel_comparison import (
    VesselTechnicalComparisonRow,
    build_vessel_technical_comparison,
)
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.vessels import BASE_VESSEL_SPECS


def comparison(**overrides):
  inputs = {
      "vessel_specs": deepcopy(BASE_VESSEL_SPECS),
      "cruise_speed": 6.0,
      "daily_miles": 35.0,
      "sun_hours": 8.0,
  }
  inputs.update(overrides)
  return build_vessel_technical_comparison(**inputs)


def rows_by_id(rows):
  return {row.vessel_id: row for row in rows}


def test_comparison_returns_exactly_v1_v2_v3():
  rows = comparison()

  assert all(isinstance(row, VesselTechnicalComparisonRow) for row in rows)
  assert [row.vessel_id for row in rows] == ["v1", "v2", "v3"]
  assert rows[0].estimate_basis == "preliminary_technical_scenario"
  assert rows[1].estimate_basis == "calibrated_preliminary"
  assert rows[2].estimate_basis == "calibrated_preliminary"


def test_capacities_batteries_and_hull_types_match_vessel_specs():
  rows = rows_by_id(comparison())

  for vessel_id in ("v1", "v2", "v3"):
    spec = BASE_VESSEL_SPECS[vessel_id]
    assert rows[vessel_id].vessel_name == spec["name"]
    assert rows[vessel_id].hull_type == spec["hull"]
    assert rows[vessel_id].passenger_capacity == spec["capacity"]
    assert rows[vessel_id].battery_capacity_kwh == spec["batCapacity"]


def test_cruise_speed_affects_all_comparison_power_outputs():
  slow = rows_by_id(comparison(cruise_speed=6.0))
  fast = rows_by_id(comparison(cruise_speed=10.0))

  for vessel_id in ("v1", "v2", "v3"):
    assert slow[vessel_id].selected_cruise_speed_knots == 6.0
    assert fast[vessel_id].selected_cruise_speed_knots == 10.0
    assert (
        slow[vessel_id].calculated_cruise_power_kw
        < fast[vessel_id].calculated_cruise_power_kw
    )
  assert slow["v1"].commission_compliance_status is None
  assert fast["v1"].commission_compliance_status is None


def test_daily_miles_affects_all_daily_propulsion_energy_outputs():
  short = rows_by_id(comparison(daily_miles=20.0))
  long = rows_by_id(comparison(daily_miles=40.0))

  for vessel_id in ("v1", "v2", "v3"):
    assert (
        short[vessel_id].daily_propulsion_energy_kwh
        < long[vessel_id].daily_propulsion_energy_kwh
    )


def test_sun_hours_affects_solar_and_net_grid_outputs():
  no_sun = rows_by_id(comparison(sun_hours=0.0))
  sunny = rows_by_id(comparison(sun_hours=8.0))

  for vessel_id in ("v1", "v2", "v3"):
    assert no_sun[vessel_id].solar_energy_contribution_kwh == 0.0
    assert (
        sunny[vessel_id].solar_energy_contribution_kwh
        > no_sun[vessel_id].solar_energy_contribution_kwh
    )
    assert (
        sunny[vessel_id].net_grid_energy_requirement_kwh
        <= no_sun[vessel_id].net_grid_energy_requirement_kwh
    )
    assert sunny[vessel_id].estimated_navigation_range_nm == pytest.approx(
        no_sun[vessel_id].estimated_navigation_range_nm
    )


def test_all_vessels_expose_battery_only_range_but_compliance_remains_unavailable():
  rows = rows_by_id(comparison(cruise_speed=10.0))

  assert rows["v1"].estimated_navigation_range_nm == pytest.approx(
      22.831668369348257
  )
  assert rows["v2"].estimated_navigation_range_nm == pytest.approx(
      22.528516941789867
  )
  assert rows["v3"].estimated_navigation_range_nm == pytest.approx(
      29.80857925719718
  )
  for vessel_id in ("v1", "v2", "v3"):
    assert rows[vessel_id].commission_compliance_status is None


def test_range_is_available_when_net_grid_requirement_is_zero():
  rows = rows_by_id(comparison(cruise_speed=6.0, sun_hours=8.0))

  assert rows["v1"].estimated_navigation_range_nm is not None
  for vessel_id in ("v2", "v3"):
    assert rows[vessel_id].net_grid_energy_requirement_kwh == 0.0
    assert rows[vessel_id].estimated_navigation_range_nm is not None
    assert rows[vessel_id].estimated_navigation_range_nm > 0.0


def test_commission_thresholds_are_unchanged():
  constraints = DALYAN_COMMISSION_CONSTRAINTS

  assert constraints.minimum_required_speed_knots == 10.0
  assert constraints.minimum_navigation_range_nm == 15.0
  assert constraints.minimum_motor_efficiency == 0.95
  assert constraints.minimum_battery_capacity_kwh == 20.0


def test_fleet_aggregation_uses_v02_energy_without_rewriting_legacy_comparison():
  specs = deepcopy(BASE_VESSEL_SPECS)
  for spec in specs.values():
    spec.update(totalCost=0.0, maxGrant=0.0)
  counts = {"v1": 50, "v2": 50, "v3": 40, "v4_24": 30, "v4_32": 20}

  result = calculate_fleet(specs, counts, 6.0, 35.0, 8.0, 180)
  expected_energy = build_fleet_energy_balance(
      specs, counts, 6.0, 35.0, 8.0, 180
  )

  assert result.fleet_daily_solar_kwh == pytest.approx(
      expected_energy.daily_solar_kwh
  )
  assert result.fleet_daily_grid_kwh == pytest.approx(
      expected_energy.daily_grid_kwh
  )
  assert result.fleet_daily_brut_kwh == pytest.approx(
      expected_energy.daily_propulsion_kwh
  )
  assert result.fleet_daily_grid_kwh >= 0
  assert result.solar_coverage_ratio >= 0
