from copy import deepcopy
from datetime import date

import pytest

from calculations.fleet_energy_balance import build_fleet_energy_balance
from config.vessels import BASE_VESSEL_SPECS


def test_hourly_fleet_path_can_report_zero_shore_energy_for_v1():
  specs = {"v1": deepcopy(BASE_VESSEL_SPECS["v1"])}
  specs["v1"].update(
      merged=1,
      totalCost=0.0,
      maxGrant=0.0,
      grantRate=0.0,
  )
  counts = {"v1": 1}
  typical = {
      (6, 1, hour): (0.90 if 8 <= hour <= 17 else 0.0)
      for hour in range(24)
  }

  result = build_fleet_energy_balance(
      specs,
      counts,
      6.0,
      35.0,
      None,
      1,
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=typical,
  )

  assert result.daily_propulsion_kwh == pytest.approx(
      41.08703676465949
  )
  assert result.annual_grid_kwh == pytest.approx(0.0)
  assert result.daily_grid_kwh == pytest.approx(0.0)


def test_hourly_path_supports_fewer_operating_days_than_calendar_days():
  specs = {"v1": deepcopy(BASE_VESSEL_SPECS["v1"])}
  specs["v1"].update(
      merged=1,
      totalCost=0.0,
      maxGrant=0.0,
      grantRate=0.0,
  )

  result = build_fleet_energy_balance(
      specs,
      {"v1": 1},
      6.0,
      35.0,
      None,
      1,
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 2),
      typical_hourly_specific_pv={},
  )

  assert result.annual_grid_kwh >= 0.0
  assert result.daily_propulsion_kwh > 0.0


def test_hourly_path_rejects_operating_days_above_season_duration():
  specs = {"v1": deepcopy(BASE_VESSEL_SPECS["v1"])}
  specs["v1"].update(
      merged=1,
      totalCost=0.0,
      maxGrant=0.0,
      grantRate=0.0,
  )

  with pytest.raises(ValueError):
    build_fleet_energy_balance(
        specs,
        {"v1": 1},
        6.0,
        35.0,
        None,
        3,
        season_start=date(2026, 6, 1),
        season_end=date(2026, 6, 2),
        typical_hourly_specific_pv={},
    )
