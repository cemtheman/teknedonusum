from dataclasses import FrozenInstanceError, fields

import pytest

from calculations.energy import NavigationEnergyResult, calculate_navigation_energy


def calculate(**overrides):
  values = {
      "speed_knots": 10.0,
      "battery_capacity_kwh": 80.0,
      "propulsion_electrical_power_kw": 23.728116959393372,
      "hotel_load_kw": 1.5,
      "usable_energy_fraction": 0.90,
      "operational_reserve_fraction": 0.20,
  }
  values.update(overrides)
  return calculate_navigation_energy(**values)


def test_ten_knot_preliminary_baseline():
  # 80 kWh is a current-project battery assumption; 1.5 kW hotel load, 0.90
  # usable fraction, and 0.20 operational reserve are preliminary test inputs.
  # Propulsion power is from an example resistance scenario, not a verified
  # prediction, and the resulting range is not a final verified range.
  result = calculate()

  assert result.usable_energy_kwh == pytest.approx(72.0)
  assert result.mission_energy_kwh == pytest.approx(57.6)
  assert result.total_electrical_power_kw == pytest.approx(25.228116959393372)
  assert result.energy_per_nm_kwh == pytest.approx(2.522811695939337)
  assert result.endurance_hours == pytest.approx(2.283166836934826)
  assert result.navigation_range_nm == pytest.approx(22.831668369348257)


def test_six_knot_preliminary_baseline():
  result = calculate(
      speed_knots=6.0,
      propulsion_electrical_power_kw=5.14817201679877,
  )

  assert result.usable_energy_kwh == pytest.approx(72.0)
  assert result.mission_energy_kwh == pytest.approx(57.6)
  assert result.total_electrical_power_kw == pytest.approx(6.64817201679877)
  assert result.energy_per_nm_kwh == pytest.approx(1.1080286694664616)
  assert result.endurance_hours == pytest.approx(8.664035746135157)
  assert result.navigation_range_nm == pytest.approx(51.98421447681095)


def test_larger_battery_increases_energy_endurance_and_range():
  small = calculate(battery_capacity_kwh=60.0)
  large = calculate(battery_capacity_kwh=100.0)

  assert large.usable_energy_kwh > small.usable_energy_kwh
  assert large.mission_energy_kwh > small.mission_energy_kwh
  assert large.endurance_hours > small.endurance_hours
  assert large.navigation_range_nm > small.navigation_range_nm
  assert large.energy_per_nm_kwh == small.energy_per_nm_kwh


def test_higher_hotel_load_increases_demand_and_reduces_range():
  low = calculate(hotel_load_kw=1.0)
  high = calculate(hotel_load_kw=3.0)

  assert high.total_electrical_power_kw > low.total_electrical_power_kw
  assert high.energy_per_nm_kwh > low.energy_per_nm_kwh
  assert high.endurance_hours < low.endurance_hours
  assert high.navigation_range_nm < low.navigation_range_nm


def test_higher_reserve_reduces_mission_energy_and_range():
  low = calculate(operational_reserve_fraction=0.10)
  high = calculate(operational_reserve_fraction=0.30)

  assert high.usable_energy_kwh == low.usable_energy_kwh
  assert high.mission_energy_kwh < low.mission_energy_kwh
  assert high.navigation_range_nm < low.navigation_range_nm


def test_higher_usable_fraction_increases_mission_energy_and_range():
  low = calculate(usable_energy_fraction=0.80)
  high = calculate(usable_energy_fraction=0.95)

  assert high.mission_energy_kwh > low.mission_energy_kwh
  assert high.navigation_range_nm > low.navigation_range_nm
  assert high.total_electrical_power_kw == low.total_electrical_power_kw
  assert high.energy_per_nm_kwh == low.energy_per_nm_kwh


def test_zero_hotel_load_is_supported():
  result = calculate(hotel_load_kw=0.0)
  assert result.hotel_load_kw == 0.0
  assert result.total_electrical_power_kw == result.propulsion_electrical_power_kw


def test_result_is_frozen_and_has_exact_schema():
  result = calculate()
  assert NavigationEnergyResult.__dataclass_params__.frozen is True
  assert [field.name for field in fields(NavigationEnergyResult)] == [
      "speed_knots",
      "battery_capacity_kwh",
      "usable_energy_fraction",
      "operational_reserve_fraction",
      "usable_energy_kwh",
      "mission_energy_kwh",
      "propulsion_electrical_power_kw",
      "hotel_load_kw",
      "total_electrical_power_kw",
      "energy_per_nm_kwh",
      "endurance_hours",
      "navigation_range_nm",
  ]
  with pytest.raises(FrozenInstanceError):
    result.navigation_range_nm = 0.0


@pytest.mark.parametrize(
    "overrides",
    [
        {"speed_knots": 0.0},
        {"speed_knots": -1.0},
        {"battery_capacity_kwh": 0.0},
        {"battery_capacity_kwh": -1.0},
        {"propulsion_electrical_power_kw": -1.0},
        {"hotel_load_kw": -1.0},
        {"usable_energy_fraction": 0.0},
        {"usable_energy_fraction": 1.1},
        {"operational_reserve_fraction": -0.1},
        {"operational_reserve_fraction": 1.0},
        {"operational_reserve_fraction": 1.1},
        {"propulsion_electrical_power_kw": 0.0, "hotel_load_kw": 0.0},
    ],
)
def test_invalid_inputs_are_rejected(overrides):
  with pytest.raises(ValueError):
    calculate(**overrides)


def test_zero_propulsion_power_with_positive_hotel_load_is_supported():
  result = calculate(propulsion_electrical_power_kw=0.0, hotel_load_kw=1.5)
  assert result.total_electrical_power_kw == 1.5
