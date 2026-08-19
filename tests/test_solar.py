from dataclasses import FrozenInstanceError, fields

import pytest

from calculations.solar import SolarEnergyResult, calculate_solar_energy


def calculate(**overrides):
  values = {
      "loa_m": 12.0,
      "roof_length_fraction_of_loa": 0.80,
      "usable_roof_width_m": 3.0,
      "panel_coverage_fraction": 0.85,
      "panel_efficiency": 0.22,
      "peak_sun_hours": 5.5,
      "derating_factor": 0.85,
      "reference_irradiance_kw_m2": 1.0,
  }
  values.update(overrides)
  return calculate_solar_energy(**values)


def test_v1_preliminary_baseline():
  # 0.80 aligns with the commission threshold for this test. Usable width,
  # coverage, panel efficiency, PSH, and derating are preliminary scenario inputs;
  # this is not a final verified PV design.
  result = calculate()

  assert result.roof_length_m == pytest.approx(9.600000000000001)
  assert result.roof_area_m2 == pytest.approx(28.800000000000004)
  assert result.panel_area_m2 == pytest.approx(24.480000000000004)
  assert result.installed_pv_power_kwp == pytest.approx(5.385600000000001)
  assert result.daily_solar_energy_kwh == pytest.approx(25.177680000000006)


def test_zero_peak_sun_hours_keeps_installed_power_and_zeroes_energy():
  result = calculate(peak_sun_hours=0.0)
  assert result.installed_pv_power_kwp > 0.0
  assert result.daily_solar_energy_kwh == 0.0


def test_higher_panel_coverage_increases_area_power_and_energy():
  low = calculate(panel_coverage_fraction=0.60)
  high = calculate(panel_coverage_fraction=0.90)

  assert high.panel_area_m2 > low.panel_area_m2
  assert high.installed_pv_power_kwp > low.installed_pv_power_kwp
  assert high.daily_solar_energy_kwh > low.daily_solar_energy_kwh


def test_higher_panel_efficiency_increases_power_and_energy_only():
  low = calculate(panel_efficiency=0.18)
  high = calculate(panel_efficiency=0.24)

  assert high.roof_length_m == low.roof_length_m
  assert high.roof_area_m2 == low.roof_area_m2
  assert high.panel_area_m2 == low.panel_area_m2
  assert high.installed_pv_power_kwp > low.installed_pv_power_kwp
  assert high.daily_solar_energy_kwh > low.daily_solar_energy_kwh


def test_higher_derating_increases_energy_without_changing_installed_power():
  low = calculate(derating_factor=0.70)
  high = calculate(derating_factor=0.90)

  assert high.installed_pv_power_kwp == low.installed_pv_power_kwp
  assert high.daily_solar_energy_kwh > low.daily_solar_energy_kwh


def test_higher_peak_sun_hours_increases_energy_without_changing_power():
  low = calculate(peak_sun_hours=4.0)
  high = calculate(peak_sun_hours=6.0)

  assert high.installed_pv_power_kwp == low.installed_pv_power_kwp
  assert high.daily_solar_energy_kwh > low.daily_solar_energy_kwh


def test_higher_roof_fraction_increases_geometry_power_and_energy():
  low = calculate(roof_length_fraction_of_loa=0.70)
  high = calculate(roof_length_fraction_of_loa=0.90)

  assert high.roof_length_m > low.roof_length_m
  assert high.roof_area_m2 > low.roof_area_m2
  assert high.panel_area_m2 > low.panel_area_m2
  assert high.installed_pv_power_kwp > low.installed_pv_power_kwp
  assert high.daily_solar_energy_kwh > low.daily_solar_energy_kwh


def test_result_is_frozen_and_has_exact_schema():
  result = calculate()
  assert SolarEnergyResult.__dataclass_params__.frozen is True
  assert [field.name for field in fields(SolarEnergyResult)] == [
      "loa_m",
      "roof_length_fraction_of_loa",
      "roof_length_m",
      "usable_roof_width_m",
      "roof_area_m2",
      "panel_coverage_fraction",
      "panel_area_m2",
      "panel_efficiency",
      "reference_irradiance_kw_m2",
      "installed_pv_power_kwp",
      "peak_sun_hours",
      "derating_factor",
      "daily_solar_energy_kwh",
  ]
  with pytest.raises(FrozenInstanceError):
    result.daily_solar_energy_kwh = 0.0


@pytest.mark.parametrize(
    "overrides",
    [
        {"loa_m": 0.0},
        {"loa_m": -1.0},
        {"roof_length_fraction_of_loa": 0.0},
        {"roof_length_fraction_of_loa": -0.1},
        {"roof_length_fraction_of_loa": 1.1},
        {"usable_roof_width_m": 0.0},
        {"usable_roof_width_m": -1.0},
        {"panel_coverage_fraction": 0.0},
        {"panel_coverage_fraction": -0.1},
        {"panel_coverage_fraction": 1.1},
        {"panel_efficiency": 0.0},
        {"panel_efficiency": -0.1},
        {"panel_efficiency": 1.1},
        {"peak_sun_hours": -1.0},
        {"derating_factor": 0.0},
        {"derating_factor": -0.1},
        {"derating_factor": 1.1},
        {"reference_irradiance_kw_m2": 0.0},
        {"reference_irradiance_kw_m2": -1.0},
    ],
)
def test_invalid_inputs_are_rejected(overrides):
  with pytest.raises(ValueError):
    calculate(**overrides)
