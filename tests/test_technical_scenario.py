from dataclasses import FrozenInstanceError, fields

import pytest

from calculations.technical_scenario import (
    PreliminaryTechnicalScenarioResult,
    evaluate_preliminary_technical_scenario,
)
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from models.compliance import ComplianceStatus


BASELINE_ARGUMENTS = {
    "geometry": PRELIMINARY_VESSEL_GEOMETRY["v1"],
    "constraints": DALYAN_COMMISSION_CONSTRAINTS,
    "passenger_capacity": 24,
    "speed_knots": 10.0,
    "daily_distance_nm": 35.0,
    "form_factor": 0.15,
    "residual_resistance_n": 1500.0,
    "appendage_resistance_n": 100.0,
    "propulsive_efficiency": 0.60,
    "motor_efficiency": 0.95,
    "design_margin_fraction": 0.15,
    "battery_capacity_kwh": 80.0,
    "usable_energy_fraction": 0.90,
    "operational_reserve_fraction": 0.20,
    "hotel_load_kw": 1.5,
    "roof_length_fraction_of_loa": 0.80,
    "usable_roof_width_m": 3.0,
    "panel_coverage_fraction": 0.85,
    "panel_efficiency": 0.22,
    "peak_sun_hours": 5.5,
    "solar_derating_factor": 0.85,
}


def evaluate(**overrides):
  arguments = BASELINE_ARGUMENTS | overrides
  return evaluate_preliminary_technical_scenario(**arguments)


def check_status(result, criterion):
  return next(
      check.status for check in result.compliance.checks
      if check.criterion == criterion
  )


def test_baseline_scenario_regression():
  result = evaluate()

  assert result.resistance.effective_power_kw == pytest.approx(13.52502666685422)
  assert result.propulsion.motor_output_power_kw == pytest.approx(22.5417111114237)
  assert result.propulsion.electrical_input_power_kw == pytest.approx(
      23.728116959393372
  )
  assert result.propulsion.installed_power_kw == pytest.approx(25.922967778137256)
  assert result.navigation_energy.navigation_range_nm == pytest.approx(
      22.831668369348257
  )
  assert result.solar.daily_solar_energy_kwh == pytest.approx(25.177680000000006)
  assert result.daily_energy_balance.operating_hours == pytest.approx(3.5)
  assert result.daily_energy_balance.gross_daily_demand_kwh == pytest.approx(
      88.2984093578768
  )
  assert result.daily_energy_balance.net_external_energy_required_kwh == pytest.approx(
      63.1207293578768
  )
  assert result.daily_energy_balance.solar_coverage_ratio == pytest.approx(
      0.2851430754313355
  )
  assert all(
      check.status is ComplianceStatus.PASS for check in result.compliance.checks
  )
  assert result.compliance.overall_status is ComplianceStatus.PASS


def test_insufficient_range_fails_without_failing_battery_capacity():
  result = evaluate(battery_capacity_kwh=50.0)

  assert result.navigation_energy.navigation_range_nm < 15.0
  assert check_status(result, "battery_capacity") is ComplianceStatus.PASS
  assert check_status(result, "minimum_navigation_range") is ComplianceStatus.FAIL
  assert result.compliance.overall_status is ComplianceStatus.FAIL


def test_roof_fraction_only_fails_roof_compliance_and_solar_still_computes():
  result = evaluate(roof_length_fraction_of_loa=0.79)

  assert result.solar.daily_solar_energy_kwh > 0.0
  failed = [
      check.criterion for check in result.compliance.checks
      if check.status is ComplianceStatus.FAIL
  ]
  assert failed == ["roof_length_fraction"]


def test_motor_efficiency_only_fails_motor_efficiency_compliance():
  result = evaluate(motor_efficiency=0.94)

  assert result.propulsion.electrical_input_power_kw > 23.728116959393372
  failed = [
      check.criterion for check in result.compliance.checks
      if check.status is ComplianceStatus.FAIL
  ]
  assert failed == ["motor_efficiency"]


def test_passenger_capacity_only_fails_passenger_compliance():
  result = evaluate(passenger_capacity=25)

  failed = [
      check.criterion for check in result.compliance.checks
      if check.status is ComplianceStatus.FAIL
  ]
  assert failed == ["passenger_capacity"]


def test_operating_speed_is_not_a_commission_compliance_check():
  slow = evaluate(speed_knots=6.0)
  fast = evaluate(speed_knots=10.0)

  assert slow.resistance.speed_knots == 6.0
  assert all(
      check.criterion != "minimum_speed" for check in slow.compliance.checks
  )
  assert slow.compliance.overall_status is ComplianceStatus.PASS
  assert (
      slow.propulsion.electrical_input_power_kw
      < fast.propulsion.electrical_input_power_kw
  )
  assert (
      slow.daily_energy_balance.propulsion_energy_kwh
      < fast.daily_energy_balance.propulsion_energy_kwh
  )


def test_daily_distance_changes_only_operational_energy_balance():
  short_day = evaluate(daily_distance_nm=20.0)
  baseline = evaluate()

  assert short_day.resistance == baseline.resistance
  assert short_day.propulsion == baseline.propulsion
  assert short_day.navigation_energy == baseline.navigation_energy
  assert short_day.solar == baseline.solar
  assert (
      short_day.daily_energy_balance.gross_daily_demand_kwh
      < baseline.daily_energy_balance.gross_daily_demand_kwh
  )


def test_peak_sun_hours_does_not_change_navigation_range():
  no_solar = evaluate(peak_sun_hours=0.0)
  baseline = evaluate()

  assert no_solar.navigation_energy == baseline.navigation_energy
  assert no_solar.solar.daily_solar_energy_kwh == pytest.approx(0.0)
  assert no_solar.daily_energy_balance != baseline.daily_energy_balance


def test_lower_propulsive_efficiency_cascades_through_energy_results():
  lower_efficiency = evaluate(propulsive_efficiency=0.50)
  baseline = evaluate()

  assert lower_efficiency.resistance.effective_power_kw == pytest.approx(
      baseline.resistance.effective_power_kw
  )
  assert (
      lower_efficiency.propulsion.motor_output_power_kw
      > baseline.propulsion.motor_output_power_kw
  )
  assert (
      lower_efficiency.propulsion.electrical_input_power_kw
      > baseline.propulsion.electrical_input_power_kw
  )
  assert (
      lower_efficiency.navigation_energy.navigation_range_nm
      < baseline.navigation_energy.navigation_range_nm
  )
  assert (
      lower_efficiency.daily_energy_balance.gross_daily_demand_kwh
      > baseline.daily_energy_balance.gross_daily_demand_kwh
  )
  assert (
      lower_efficiency.daily_energy_balance.net_external_energy_required_kwh
      > baseline.daily_energy_balance.net_external_energy_required_kwh
  )


def test_negative_daily_distance_is_rejected():
  with pytest.raises(ValueError, match="daily_distance_nm must be non-negative"):
    evaluate(daily_distance_nm=-1.0)


def test_zero_daily_distance_keeps_navigation_and_allows_solar_excess():
  result = evaluate(daily_distance_nm=0.0)

  assert result.navigation_energy.navigation_range_nm == pytest.approx(
      22.831668369348257
  )
  assert result.daily_energy_balance.operating_hours == pytest.approx(0.0)
  assert result.daily_energy_balance.gross_daily_demand_kwh == pytest.approx(0.0)
  assert result.daily_energy_balance.excess_solar_energy_kwh == pytest.approx(
      25.177680000000006
  )


def test_zero_speed_is_rejected_by_navigation_before_operating_hours_division():
  with pytest.raises(ValueError, match="speed_knots must be positive"):
    evaluate(speed_knots=0.0)


def test_result_is_frozen_and_has_exactly_six_fields():
  result = evaluate()

  assert [field.name for field in fields(PreliminaryTechnicalScenarioResult)] == [
      "resistance",
      "propulsion",
      "navigation_energy",
      "solar",
      "daily_energy_balance",
      "compliance",
  ]
  with pytest.raises(FrozenInstanceError):
    result.resistance = result.resistance
