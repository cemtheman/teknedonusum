from dataclasses import FrozenInstanceError, fields, replace

import pytest

from config.preliminary_scenario import (
    PreliminaryScenarioAssumptions,
    V1_PRELIMINARY_SCENARIO_ASSUMPTIONS,
)


def test_v1_preliminary_scenario_assumptions_are_exact():
  assumptions = V1_PRELIMINARY_SCENARIO_ASSUMPTIONS

  assert [field.name for field in fields(PreliminaryScenarioAssumptions)] == [
      "form_factor",
      "residual_resistance_n",
      "appendage_resistance_n",
      "propulsive_efficiency",
      "motor_efficiency",
      "design_margin_fraction",
      "usable_energy_fraction",
      "operational_reserve_fraction",
      "hotel_load_kw",
      "roof_length_fraction_of_loa",
      "usable_roof_width_m",
      "panel_coverage_fraction",
      "panel_efficiency",
      "peak_sun_hours",
      "solar_derating_factor",
  ]
  assert tuple(getattr(assumptions, field.name) for field in fields(assumptions)) == (
      0.15,
      1500.0,
      100.0,
      0.60,
      0.95,
      0.15,
      0.90,
      0.20,
      1.5,
      0.80,
      3.0,
      0.85,
      0.22,
      5.5,
      0.85,
  )


def test_v1_preliminary_scenario_assumptions_are_frozen():
  with pytest.raises(FrozenInstanceError):
    V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.form_factor = 0.20


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("form_factor", -0.01),
        ("residual_resistance_n", -0.01),
        ("appendage_resistance_n", -0.01),
        ("propulsive_efficiency", 0.0),
        ("propulsive_efficiency", 1.01),
        ("motor_efficiency", 0.0),
        ("motor_efficiency", 1.01),
        ("design_margin_fraction", -0.01),
        ("usable_energy_fraction", 0.0),
        ("usable_energy_fraction", 1.01),
        ("operational_reserve_fraction", -0.01),
        ("operational_reserve_fraction", 1.0),
        ("hotel_load_kw", -0.01),
        ("roof_length_fraction_of_loa", 0.0),
        ("roof_length_fraction_of_loa", 1.01),
        ("usable_roof_width_m", 0.0),
        ("panel_coverage_fraction", 0.0),
        ("panel_coverage_fraction", 1.01),
        ("panel_efficiency", 0.0),
        ("panel_efficiency", 1.01),
        ("peak_sun_hours", -0.01),
        ("solar_derating_factor", 0.0),
        ("solar_derating_factor", 1.01),
    ],
)
def test_preliminary_scenario_validation(field_name, invalid_value):
  with pytest.raises(ValueError):
    replace(
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS,
        **{field_name: invalid_value},
    )
