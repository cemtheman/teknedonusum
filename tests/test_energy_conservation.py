from datetime import date

import pytest

from calculations.seasonal_energy_balance import simulate_seasonal_vessel_energy


def _profile(value):
  return {(6, 1, hour): value for hour in range(24)}


@pytest.mark.parametrize("specific_pv", [0.0, 0.25, 1.0])
def test_energy_conservation_closes_for_all_major_flows(specific_pv):
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=_profile(specific_pv),
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=6.0,
      nominal_battery_kwh=60.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=0.95,
      discharge_efficiency=0.95,
  )

  assert result.pv_balance_error_kwh == pytest.approx(0.0, abs=1e-9)
  assert result.propulsion_balance_error_kwh == pytest.approx(0.0, abs=1e-9)
  assert result.battery_balance_error_kwh == pytest.approx(0.0, abs=1e-9)


def test_terminal_soc_deficit_is_not_hidden_from_shore_interpretation():
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=_profile(0.0),
      installed_pv_kwp=8.0,
      propulsion_power_kw=10.0,
      cruise_hours_per_day=8.0,
      nominal_battery_kwh=20.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
      charge_efficiency=0.95,
      discharge_efficiency=0.95,
  )

  assert result.terminal_soc_deficit_kwh > 0
  assert result.terminal_soc_recovery_shore_kwh > 0
  assert result.normalized_shore_energy_kwh > result.shore_energy_kwh


def test_pv_generation_equals_direct_charge_input_and_curtailment():
  result = simulate_seasonal_vessel_energy(
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=_profile(0.8),
      installed_pv_kwp=8.0,
      propulsion_power_kw=7.0,
      cruise_hours_per_day=6.0,
      nominal_battery_kwh=60.0,
      usable_fraction=0.90,
      reserve_fraction=0.20,
  )

  accounted = (
      result.solar_direct_to_propulsion_kwh
      + result.solar_to_battery_input_kwh
      + result.curtailed_solar_kwh
  )
  assert result.season_solar_generation_kwh == pytest.approx(accounted)
