import pytest

from calculations.solar_assisted_propulsion import (
    available_solar_power_kw,
    split_propulsion_power,
)


def test_solar_above_propulsion_demand_gives_true_solar_only_operation():
  result = split_propulsion_power(
      propulsion_demand_kw=7.0,
      solar_available_kw=8.5,
  )

  assert result.solar_to_propulsion_kw == pytest.approx(7.0)
  assert result.battery_discharge_kw == pytest.approx(0.0)
  assert result.solar_surplus_kw == pytest.approx(1.5)
  assert result.solar_only_propulsion is True


def test_battery_supplies_only_solar_deficit():
  result = split_propulsion_power(
      propulsion_demand_kw=7.0,
      solar_available_kw=3.0,
  )

  assert result.solar_to_propulsion_kw == pytest.approx(3.0)
  assert result.battery_discharge_kw == pytest.approx(4.0)
  assert result.solar_surplus_kw == pytest.approx(0.0)
  assert result.solar_only_propulsion is False


def test_no_sun_means_full_propulsion_demand_comes_from_battery():
  result = split_propulsion_power(
      propulsion_demand_kw=7.0,
      solar_available_kw=0.0,
  )

  assert result.battery_discharge_kw == pytest.approx(7.0)
  assert result.solar_only_propulsion is False


def test_installed_pv_kwp_scales_normalized_pvgis_power():
  assert available_solar_power_kw(9.0, 0.82) == pytest.approx(7.38)
