from dataclasses import FrozenInstanceError

import pytest

from calculations.compliance import evaluate_commission_compliance
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from models.compliance import (
    CommissionComplianceResult,
    ComplianceCheck,
    ComplianceStatus,
)


EXPECTED_CRITERIA = [
    "loa",
    "passenger_capacity",
    "minimum_navigation_range",
    "motor_efficiency",
    "battery_capacity",
    "roof_length_fraction",
]


def evaluate(**overrides):
  values = {
      "constraints": DALYAN_COMMISSION_CONSTRAINTS,
      "loa_m": 12.0,
      "passenger_capacity": 24,
      "navigation_range_nm": 15.0,
      "motor_efficiency": 0.95,
      "battery_capacity_kwh": 20.0,
      "roof_length_fraction_of_loa": 0.80,
  }
  values.update(overrides)
  return evaluate_commission_compliance(**values)


def checks_by_criterion(result):
  return {check.criterion: check for check in result.checks}


def test_all_inclusive_boundaries_pass():
  result = evaluate()
  assert len(result.checks) == 6
  assert [check.criterion for check in result.checks] == EXPECTED_CRITERIA
  assert all(check.status is ComplianceStatus.PASS for check in result.checks)
  assert result.overall_status is ComplianceStatus.PASS


@pytest.mark.parametrize(
    ("loa_m", "expected_status"),
    [
        (14.0, ComplianceStatus.PASS),
        (14.01, ComplianceStatus.FAIL),
        (11.99, ComplianceStatus.FAIL),
    ],
)
def test_loa_boundaries(loa_m, expected_status):
  result = evaluate(loa_m=loa_m)
  assert checks_by_criterion(result)["loa"].status is expected_status


@pytest.mark.parametrize(
    ("capacity", "expected_status"),
    [
        (24, ComplianceStatus.PASS),
        (32, ComplianceStatus.PASS),
        (54, ComplianceStatus.PASS),
        (25, ComplianceStatus.FAIL),
    ],
)
def test_passenger_capacity_values(capacity, expected_status):
  result = evaluate(passenger_capacity=capacity)
  assert checks_by_criterion(result)["passenger_capacity"].status is expected_status


@pytest.mark.parametrize(
    ("overrides", "failed_criterion"),
    [
        ({"navigation_range_nm": 14.99}, "minimum_navigation_range"),
        ({"motor_efficiency": 0.949}, "motor_efficiency"),
        ({"battery_capacity_kwh": 19.99}, "battery_capacity"),
        ({"roof_length_fraction_of_loa": 0.799}, "roof_length_fraction"),
    ],
)
def test_each_minimum_failure_is_isolated(overrides, failed_criterion):
  result = evaluate(**overrides)
  failed = [
      check.criterion
      for check in result.checks
      if check.status is ComplianceStatus.FAIL
  ]
  assert failed == [failed_criterion]
  assert result.overall_status is ComplianceStatus.FAIL


def test_multiple_failures_preserve_check_order():
  result = evaluate(
      loa_m=14.01,
      passenger_capacity=25,
  )
  assert [check.criterion for check in result.checks] == EXPECTED_CRITERIA
  assert result.overall_status is ComplianceStatus.FAIL


def test_required_value_strings_and_raw_actual_values():
  result = evaluate()
  checks = checks_by_criterion(result)
  assert checks["loa"].required_value == "12.0–14.0 m"
  assert checks["passenger_capacity"].required_value == "24 / 32 / 54 yolcu"
  assert checks["minimum_navigation_range"].required_value == "≥ 15.0 NM"
  assert checks["motor_efficiency"].required_value == "≥ %95.0"
  assert checks["battery_capacity"].required_value == "≥ 20.0 kWh"
  assert checks["roof_length_fraction"].required_value == "≥ LOA'nın %80.0'ı"
  assert checks["motor_efficiency"].actual_value == 0.95


def test_result_models_are_frozen():
  result = evaluate()
  with pytest.raises(FrozenInstanceError):
    result.checks[0].status = ComplianceStatus.FAIL
  with pytest.raises(FrozenInstanceError):
    result.overall_status = ComplianceStatus.FAIL


def test_result_rejects_fail_check_with_overall_pass():
  failed_check = ComplianceCheck("criterion", 0.0, "requirement", ComplianceStatus.FAIL)
  with pytest.raises(ValueError):
    CommissionComplianceResult((failed_check,), ComplianceStatus.PASS)


def test_result_rejects_all_pass_checks_with_overall_fail():
  passed_check = ComplianceCheck("criterion", 1.0, "requirement", ComplianceStatus.PASS)
  with pytest.raises(ValueError):
    CommissionComplianceResult((passed_check,), ComplianceStatus.FAIL)


def test_result_rejects_empty_checks():
  with pytest.raises(ValueError):
    CommissionComplianceResult((), ComplianceStatus.PASS)


@pytest.mark.parametrize(
    "overrides",
    [
        {"loa_m": 0.0},
        {"loa_m": -1.0},
        {"passenger_capacity": 0},
        {"passenger_capacity": -1},
        {"navigation_range_nm": -1.0},
        {"motor_efficiency": 0.0},
        {"motor_efficiency": -0.1},
        {"motor_efficiency": 1.1},
        {"battery_capacity_kwh": 0.0},
        {"battery_capacity_kwh": -1.0},
        {"roof_length_fraction_of_loa": 0.0},
        {"roof_length_fraction_of_loa": -0.1},
        {"roof_length_fraction_of_loa": 1.1},
    ],
)
def test_invalid_inputs_are_rejected(overrides):
  with pytest.raises(ValueError):
    evaluate(**overrides)


def test_invalid_constraints_type_is_rejected():
  with pytest.raises(TypeError):
    evaluate(constraints=object())
