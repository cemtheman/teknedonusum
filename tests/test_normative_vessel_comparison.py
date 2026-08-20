from dataclasses import FrozenInstanceError, fields, replace

import pytest

from calculations.normative_decision_summary import (
    build_normative_decision_summary,
)
from calculations.normative_sizing import calculate_normative_sizing
from calculations.normative_vessel_comparison import (
    build_normative_vessel_comparison,
)
from config.vessels import BASE_VESSEL_SPECS
from models.normative_vessel_comparison import (
    NormativeVesselComparisonRow,
)


def comparison(speed_knots=8.0):
  return build_normative_vessel_comparison(speed_knots)


def test_result_rows_and_assumptions_are_immutable():
  result = comparison()

  with pytest.raises(FrozenInstanceError):
    result.selected_speed_knots = 9.0
  with pytest.raises(FrozenInstanceError):
    result.rows[0].vessel_id = "changed"
  with pytest.raises(FrozenInstanceError):
    result.assumptions.duty_cycle = 1.0


@pytest.mark.parametrize("speed_knots", (6.0, 7.0, 8.0, 9.0, 10.0))
def test_same_speed_ordered_v1_v2_v3_coverage(speed_knots):
  result = comparison(speed_knots)

  assert tuple(row.vessel_id for row in result.rows) == ("v1", "v2", "v3")
  assert all(row.selected_speed_knots == speed_knots for row in result.rows)


@pytest.mark.parametrize("speed_knots", (6.0, 7.0, 8.0, 9.0, 10.0))
def test_exact_decision_summary_propagation(speed_knots):
  result = comparison(speed_knots)

  for row in result.rows:
    source = build_normative_decision_summary(
        calculate_normative_sizing(row.vessel_id, speed_knots)
    )
    assert row.reference_installed_mechanical_power_kw == (
        source.reference_estimate_installed_mechanical_power_kw
    )
    assert row.reference_daily_propulsion_energy_kwh == (
        source.reference_estimate_daily_propulsion_energy_kwh
    )
    assert row.reference_nominal_battery_capacity_kwh == (
        source.reference_estimate_nominal_battery_capacity_kwh
    )
    assert row.reference_propulsion_system_cost == (
        source.reference_estimate_propulsion_system_cost
    )


@pytest.mark.parametrize(
    ("speed_knots", "expected_reference_power"),
    (
        (6.0, (30.0, 30.0, 35.0)),
        (7.0, (36.25, 36.25, 43.75)),
        (8.0, (42.5, 42.5, 52.5)),
        (9.0, (51.25, 53.75, 63.75)),
        (10.0, (60.0, 65.0, 75.0)),
    ),
)
def test_reference_power_regression(speed_knots, expected_reference_power):
  result = comparison(speed_knots)

  assert tuple(
      row.reference_installed_mechanical_power_kw for row in result.rows
  ) == pytest.approx(expected_reference_power)


def test_passenger_metadata_comes_from_vessel_config():
  result = comparison()

  assert tuple(row.passenger_capacity for row in result.rows) == tuple(
      BASE_VESSEL_SPECS[row.vessel_id]["capacity"] for row in result.rows
  )


def test_common_assumptions_currency_and_vessel_cost_multiplier():
  result = comparison()

  assert result.currency == "EUR"
  assert all(row.currency == result.currency for row in result.rows)
  assert all(row.assumptions == result.assumptions for row in result.rows)
  assert result.assumptions.motor_efficiency == 0.95
  assert result.assumptions.operating_hours_per_day == 8.0
  assert result.assumptions.duty_cycle == 0.75
  assert result.assumptions.usable_energy_fraction == 0.90
  assert result.assumptions.reserve_fraction == 0.20
  assert tuple(row.motor_system_multiplier for row in result.rows) == (
      1.0,
      1.2,
      1.2,
  )


def test_rows_are_raw_numeric_export_ready_without_ranking_fields():
  row = comparison().rows[0]
  names = {field.name for field in fields(NormativeVesselComparisonRow)}

  assert isinstance(row.reference_installed_mechanical_power_kw, float)
  assert isinstance(row.reference_daily_propulsion_energy_kwh, float)
  assert isinstance(row.reference_nominal_battery_capacity_kwh, float)
  assert isinstance(row.reference_propulsion_system_cost, float)
  assert names.isdisjoint({"rank", "score", "recommendation", "best_vessel"})


@pytest.mark.parametrize("speed_knots", (5.9, 10.1, float("inf")))
def test_invalid_speed_is_rejected(speed_knots):
  with pytest.raises(ValueError, match="6"):
    comparison(speed_knots)


def test_missing_duplicate_or_reordered_rows_are_rejected():
  result = comparison()

  for invalid_rows in (
      result.rows[:2],
      (result.rows[0], result.rows[0], result.rows[2]),
      tuple(reversed(result.rows)),
  ):
    with pytest.raises(ValueError, match="ordered, unique"):
      replace(result, rows=invalid_rows)


def test_currency_and_common_assumption_mismatch_are_rejected():
  result = comparison()

  with pytest.raises(ValueError, match="currency"):
    replace(
        result,
        rows=(replace(result.rows[0], currency="TRY"), *result.rows[1:]),
    )
  changed = replace(result.rows[0].assumptions, duty_cycle=0.5)
  with pytest.raises(ValueError, match="common normative assumptions"):
    replace(
        result,
        rows=(replace(result.rows[0], assumptions=changed), *result.rows[1:]),
    )


def test_speed_mismatch_and_invalid_envelope_are_rejected():
  result = comparison()

  with pytest.raises(ValueError, match="selected comparison speed"):
    replace(
        result,
        rows=(replace(result.rows[0], selected_speed_knots=7.0), *result.rows[1:]),
    )
  with pytest.raises(ValueError, match="envelopes must be ordered"):
    replace(
        result.rows[0],
        min_installed_mechanical_power_kw=(
            result.rows[0].max_installed_mechanical_power_kw + 1.0
        ),
    )
