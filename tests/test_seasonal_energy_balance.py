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

  assert result.minimum_soc_kwh == pytest.approx(3.6)
  assert result.shore_energy_kwh > 0


def test_reserve_fraction_is_applied_within_usable_soc_window():
  dark = {(6, 1, hour): 0.0 for hour in range(24)}
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=dark,
      installed_pv_kwp=0.0,
      propulsion_power_kw=9.0,
      cruise_hours_per_day=8.0,
      nominal_battery_kwh=100.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
  )

  assert result.initial_soc_kwh == pytest.approx(90.0)
  assert result.minimum_soc_kwh == pytest.approx(18.0)
  assert result.battery_discharge_to_propulsion_kwh == pytest.approx(72.0)
  assert result.shore_energy_kwh == pytest.approx(0.0)


def test_zero_auxiliary_preserves_propulsion_only_balances():
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=profile(0.50),
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=6.0,
      nominal_battery_kwh=60.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
  )

  assert result.season_auxiliary_kwh == pytest.approx(0.0)
  assert result.solar_direct_to_auxiliary_kwh == pytest.approx(0.0)
  assert result.battery_discharge_to_auxiliary_kwh == pytest.approx(0.0)
  assert result.shore_to_auxiliary_kwh == pytest.approx(0.0)
  assert result.pv_balance_error_kwh == pytest.approx(0.0)
  assert result.propulsion_balance_error_kwh == pytest.approx(0.0)
  assert result.auxiliary_balance_error_kwh == pytest.approx(0.0)
  assert result.battery_balance_error_kwh == pytest.approx(0.0)


def test_auxiliary_load_uses_battery_before_shore():
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=profile(0.0),
      installed_pv_kwp=0.0,
      propulsion_power_kw=0.0,
      cruise_hours_per_day=1.0,
      nominal_battery_kwh=100.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
      auxiliary_power_kw=1.0,
      auxiliary_operating_hours_per_day=10.0,
  )

  assert result.season_auxiliary_kwh == pytest.approx(10.0)
  assert result.battery_discharge_to_auxiliary_kwh == pytest.approx(10.0)
  assert result.shore_to_auxiliary_kwh == pytest.approx(0.0)
  assert result.auxiliary_balance_error_kwh == pytest.approx(0.0)
  assert result.battery_balance_error_kwh == pytest.approx(0.0)


def test_solar_priority_is_propulsion_then_auxiliary_then_battery():
  hourly = {
      (6, 1, hour): (1.0 if hour == 9 else 0.0)
      for hour in range(24)
  }
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=hourly,
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=1.0,
      nominal_battery_kwh=20.0,
      usable_fraction=1.0,
      reserve_fraction=0.0,
      charge_efficiency=1.0,
      discharge_efficiency=1.0,
      auxiliary_power_kw=2.0,
      auxiliary_operating_hours_per_day=1.0,
  )

  assert result.solar_direct_to_propulsion_kwh == pytest.approx(7.0)
  assert result.solar_direct_to_auxiliary_kwh == pytest.approx(1.0)
  assert result.battery_discharge_to_propulsion_kwh == pytest.approx(0.0)
  assert result.battery_discharge_to_auxiliary_kwh == pytest.approx(1.0)
  assert result.shore_energy_kwh == pytest.approx(0.0)
  assert result.pv_balance_error_kwh == pytest.approx(0.0)
  assert result.propulsion_balance_error_kwh == pytest.approx(0.0)
  assert result.auxiliary_balance_error_kwh == pytest.approx(0.0)
  assert result.battery_balance_error_kwh == pytest.approx(0.0)
