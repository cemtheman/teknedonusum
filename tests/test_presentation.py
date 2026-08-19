from dataclasses import FrozenInstanceError

import pytest

from calculations.presentation import build_technical_scenario_presentation
from calculations.technical_scenario import evaluate_preliminary_technical_scenario
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from models.compliance import ComplianceStatus
from models.presentation import (
    ComplianceDisplayValue,
    TechnicalDisplayValue,
    TechnicalScenarioPresentation,
    TechnicalValueCategory,
)


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


def build_presentation(**overrides):
  scenario = evaluate_preliminary_technical_scenario(
      **(BASELINE_ARGUMENTS | overrides)
  )
  return scenario, build_technical_scenario_presentation(scenario)


def test_baseline_presentation_values_and_order():
  _, presentation = build_presentation()

  assert presentation.overall_status is ComplianceStatus.PASS
  assert [value.key for value in presentation.primary_values] == [
      "installed_motor_power",
      "electrical_input_power",
      "battery_navigation_range",
      "daily_solar_energy",
      "net_external_energy",
  ]
  assert [value.criterion for value in presentation.compliance_values] == [
      "loa",
      "passenger_capacity",
      "minimum_speed",
      "minimum_navigation_range",
      "motor_efficiency",
      "battery_capacity",
      "roof_length_fraction",
  ]
  assert [value.key for value in presentation.detail_values] == [
      "effective_power",
      "motor_output_power",
      "energy_per_nm",
      "solar_coverage",
      "excess_solar_energy",
  ]

  assert [value.value for value in presentation.primary_values] == pytest.approx([
      25.922967778137256,
      23.728116959393372,
      22.831668369348257,
      25.177680000000006,
      63.1207293578768,
  ])
  assert [value.value for value in presentation.detail_values] == pytest.approx([
      13.52502666685422,
      22.5417111114237,
      2.522811695939337,
      0.2851430754313355,
      0.0,
  ])


def test_categories_are_preliminary_estimates():
  _, presentation = build_presentation()

  assert all(
      value.category is TechnicalValueCategory.PRELIMINARY_ESTIMATE
      for value in presentation.primary_values
  )
  assert all(
      value.category is TechnicalValueCategory.PRELIMINARY_ESTIMATE
      for value in presentation.detail_values
  )


def test_compliance_mapping_is_exact():
  scenario, presentation = build_presentation()
  expected_labels = [
      "Tam Boy (LOA)",
      "Yolcu Kapasitesi",
      "Asgari Hız",
      "Seyir Menzili",
      "Motor Verimi",
      "Batarya Kapasitesi",
      "Çatı Uzunluğu / LOA",
  ]

  assert [value.label for value in presentation.compliance_values] == expected_labels
  assert [value.actual_value for value in presentation.compliance_values] == [
      check.actual_value for check in scenario.compliance.checks
  ]
  assert [value.required_value for value in presentation.compliance_values] == [
      check.required_value for check in scenario.compliance.checks
  ]
  assert [value.status for value in presentation.compliance_values] == [
      check.status for check in scenario.compliance.checks
  ]


def test_failed_roof_scenario_maps_failure_and_keeps_values():
  _, presentation = build_presentation(roof_length_fraction_of_loa=0.79)
  roof = next(
      value for value in presentation.compliance_values
      if value.criterion == "roof_length_fraction"
  )

  assert presentation.overall_status is ComplianceStatus.FAIL
  assert roof.status is ComplianceStatus.FAIL
  assert len(presentation.primary_values) == 5
  assert len(presentation.detail_values) == 5


def display_value():
  return TechnicalDisplayValue(
      key="value",
      label="Value",
      value=1.0,
      unit="unit",
      category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
  )


def compliance_value(status):
  return ComplianceDisplayValue(
      criterion="criterion",
      label="Criterion",
      actual_value=1.0,
      required_value=">= 1",
      status=status,
  )


def test_presentation_rejects_pass_with_failed_compliance():
  with pytest.raises(ValueError, match="overall PASS"):
    TechnicalScenarioPresentation(
        overall_status=ComplianceStatus.PASS,
        primary_values=(display_value(),),
        compliance_values=(compliance_value(ComplianceStatus.FAIL),),
        detail_values=(display_value(),),
    )


def test_presentation_rejects_fail_when_all_compliance_passes():
  with pytest.raises(ValueError, match="overall FAIL"):
    TechnicalScenarioPresentation(
        overall_status=ComplianceStatus.FAIL,
        primary_values=(display_value(),),
        compliance_values=(compliance_value(ComplianceStatus.PASS),),
        detail_values=(display_value(),),
    )


def test_presentation_rejects_empty_primary_values():
  with pytest.raises(ValueError, match="primary_values must not be empty"):
    TechnicalScenarioPresentation(
        overall_status=ComplianceStatus.PASS,
        primary_values=(),
        compliance_values=(compliance_value(ComplianceStatus.PASS),),
        detail_values=(display_value(),),
    )


def test_presentation_rejects_empty_compliance_values():
  with pytest.raises(ValueError, match="compliance_values must not be empty"):
    TechnicalScenarioPresentation(
        overall_status=ComplianceStatus.PASS,
        primary_values=(display_value(),),
        compliance_values=(),
        detail_values=(display_value(),),
    )


def test_presentation_models_are_frozen():
  technical = display_value()
  compliance = compliance_value(ComplianceStatus.PASS)
  presentation = TechnicalScenarioPresentation(
      overall_status=ComplianceStatus.PASS,
      primary_values=(technical,),
      compliance_values=(compliance,),
      detail_values=(technical,),
  )

  with pytest.raises(FrozenInstanceError):
    technical.value = 2.0
  with pytest.raises(FrozenInstanceError):
    compliance.status = ComplianceStatus.FAIL
  with pytest.raises(FrozenInstanceError):
    presentation.overall_status = ComplianceStatus.FAIL


def test_builder_rejects_wrong_scenario_type():
  with pytest.raises(
      TypeError,
      match="scenario must be a PreliminaryTechnicalScenarioResult",
  ):
    build_technical_scenario_presentation(object())


def test_technical_value_category_has_exactly_two_members():
  assert list(TechnicalValueCategory) == [
      TechnicalValueCategory.COMMISSION_CRITERION,
      TechnicalValueCategory.PRELIMINARY_ESTIMATE,
  ]
