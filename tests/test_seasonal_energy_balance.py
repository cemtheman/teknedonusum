from datetime import date

import pytest

from calculations.seasonal_energy_balance import simulate_seasonal_vessel_energy


def profile(value):
  return {
      (6, 1, hour): value
      for hour in range(24)
  }


def test_solar_first_propulsion_can_need_zero_shore_energy():
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=profile(1.0),
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=6.0,
      nominal_battery_kwh=60.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
  )

  assert result.shore_energy_kwh == pytest.approx(0.0)
  assert result.solar_direct_to_propulsion_kwh == pytest.approx(42.0)
  assert result.solar_only_propulsion_hours == pytest.approx(6.0)


def test_low_solar_uses_battery_before_shore():
  low = {(6, 1, hour): 0.25 for hour in range(24)}
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=low,
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=6.0,
      nominal_battery_kwh=60.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
  )

  assert result.battery_discharge_to_propulsion_kwh > 0
  assert result.shore_energy_kwh == pytest.approx(0.0)


def test_shore_energy_appears_only_after_reserve_floor_is_reached():
  dark = {(6, 1, hour): 0.0 for hour in range(24)}
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=dark,
      installed_pv_kwp=8.0,
      propulsion_power_kw=10.0,
      cruise_hours_per_day=8.0,
      nominal_battery_kwh=20.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
  )

  assert result.minimum_soc_kwh == pytest.approx(4.0)
  assert result.shore_energy_kwh > 0
