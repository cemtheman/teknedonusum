from dataclasses import FrozenInstanceError, fields

import pytest

from calculations.energy_balance import (
    DailyEnergyBalanceResult,
    calculate_daily_energy_balance,
)


def calculate(**overrides):
  values = {
      "operating_hours": 5.833333333333333,
      "propulsion_electrical_power_kw": 5.14817201679877,
      "hotel_load_kw": 1.5,
      "daily_solar_energy_kwh": 25.177680000000006,
  }
  values.update(overrides)
  return calculate_daily_energy_balance(**values)


def test_six_knot_daily_baseline():
  # Inputs come from previous preliminary examples and are not final verified
  # vessel-design values.
  result = calculate()

  assert result.propulsion_energy_kwh == pytest.approx(30.03100343132616)
  assert result.hotel_energy_kwh == pytest.approx(8.75)
  assert result.gross_daily_demand_kwh == pytest.approx(38.781003431326155)
  assert result.solar_energy_used_kwh == pytest.approx(25.177680000000006)
  assert result.excess_solar_energy_kwh == pytest.approx(0.0)
  assert result.net_external_energy_required_kwh == pytest.approx(13.60332343132615)
  assert result.solar_coverage_ratio == pytest.approx(0.6492271414427151)


def test_ten_knot_daily_baseline():
  result = calculate(
      operating_hours=3.5,
      propulsion_electrical_power_kw=23.728116959393372,
  )

  assert result.propulsion_energy_kwh == pytest.approx(83.0484093578768)
  assert result.hotel_energy_kwh == pytest.approx(5.25)
  assert result.gross_daily_demand_kwh == pytest.approx(88.2984093578768)
  assert result.solar_energy_used_kwh == pytest.approx(25.177680000000006)
  assert result.excess_solar_energy_kwh == pytest.approx(0.0)
  assert result.net_external_energy_required_kwh == pytest.approx(63.1207293578768)
  assert result.solar_coverage_ratio == pytest.approx(0.2851430754313355)


def test_solar_above_demand_is_capped_at_full_coverage():
  result = calculate_daily_energy_balance(
      operating_hours=1.0,
      propulsion_electrical_power_kw=2.0,
      hotel_load_kw=1.0,
      daily_solar_energy_kwh=5.0,
  )

  assert result.gross_daily_demand_kwh == 3.0
  assert result.solar_energy_used_kwh == 3.0
  assert result.excess_solar_energy_kwh == 2.0
  assert result.net_external_energy_required_kwh == 0.0
  assert result.solar_coverage_ratio == 1.0


def test_zero_solar_leaves_all_demand_external():
  result = calculate(daily_solar_energy_kwh=0.0)
  assert result.solar_energy_used_kwh == 0.0
  assert result.excess_solar_energy_kwh == 0.0
  assert result.net_external_energy_required_kwh == result.gross_daily_demand_kwh
  assert result.solar_coverage_ratio == 0.0


def test_zero_operating_hours_preserves_solar_as_excess():
  result = calculate(operating_hours=0.0)
  assert result.propulsion_energy_kwh == 0.0
  assert result.hotel_energy_kwh == 0.0
  assert result.gross_daily_demand_kwh == 0.0
  assert result.solar_energy_used_kwh == 0.0
  assert result.excess_solar_energy_kwh == pytest.approx(25.177680000000006)
  assert result.net_external_energy_required_kwh == 0.0
  assert result.solar_coverage_ratio == 0.0


def test_more_solar_reduces_external_energy_and_increases_coverage():
  low = calculate(daily_solar_energy_kwh=5.0)
  high = calculate(daily_solar_energy_kwh=15.0)
  assert high.solar_energy_used_kwh >= low.solar_energy_used_kwh
  assert high.net_external_energy_required_kwh < low.net_external_energy_required_kwh
  assert high.solar_coverage_ratio > low.solar_coverage_ratio


def test_higher_hotel_load_increases_demand_and_external_energy():
  low = calculate(hotel_load_kw=1.0)
  high = calculate(hotel_load_kw=3.0)
  assert high.gross_daily_demand_kwh > low.gross_daily_demand_kwh
  assert high.net_external_energy_required_kwh >= low.net_external_energy_required_kwh
  assert high.solar_coverage_ratio <= low.solar_coverage_ratio


def test_longer_operation_increases_demand_and_external_energy():
  short = calculate(operating_hours=3.0)
  long = calculate(operating_hours=6.0)
  assert long.gross_daily_demand_kwh > short.gross_daily_demand_kwh
  assert long.net_external_energy_required_kwh >= short.net_external_energy_required_kwh
  assert long.solar_coverage_ratio <= short.solar_coverage_ratio


def test_result_is_frozen_and_has_exact_schema():
  result = calculate()
  assert DailyEnergyBalanceResult.__dataclass_params__.frozen is True
  assert [field.name for field in fields(DailyEnergyBalanceResult)] == [
      "operating_hours",
      "propulsion_electrical_power_kw",
      "hotel_load_kw",
      "propulsion_energy_kwh",
      "hotel_energy_kwh",
      "gross_daily_demand_kwh",
      "daily_solar_energy_kwh",
      "solar_energy_used_kwh",
      "excess_solar_energy_kwh",
      "net_external_energy_required_kwh",
      "solar_coverage_ratio",
  ]
  with pytest.raises(FrozenInstanceError):
    result.solar_coverage_ratio = 0.0


@pytest.mark.parametrize(
    "overrides",
    [
        {"operating_hours": -1.0},
        {"propulsion_electrical_power_kw": -1.0},
        {"hotel_load_kw": -1.0},
        {"daily_solar_energy_kwh": -1.0},
    ],
)
def test_negative_inputs_are_rejected(overrides):
  with pytest.raises(ValueError):
    calculate(**overrides)
