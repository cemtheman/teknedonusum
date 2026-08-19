from calculations.technical_scenario import PreliminaryTechnicalScenarioResult
from models.presentation import (
    ComplianceDisplayValue,
    TechnicalDisplayValue,
    TechnicalScenarioPresentation,
    TechnicalValueCategory,
)


COMPLIANCE_LABELS = {
    "loa": "LOA",
    "passenger_capacity": "Passenger Capacity",
    "minimum_speed": "Minimum Speed",
    "minimum_navigation_range": "Navigation Range",
    "motor_efficiency": "Motor Efficiency",
    "battery_capacity": "Battery Capacity",
    "roof_length_fraction": "Roof Length",
}


def build_technical_scenario_presentation(
    scenario: PreliminaryTechnicalScenarioResult,
) -> TechnicalScenarioPresentation:
  if not isinstance(scenario, PreliminaryTechnicalScenarioResult):
    raise TypeError("scenario must be a PreliminaryTechnicalScenarioResult")

  primary_values = (
      TechnicalDisplayValue(
          key="installed_motor_power",
          label="Installed Motor Power",
          value=scenario.propulsion.installed_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="electrical_input_power",
          label="Electrical Input Power",
          value=scenario.propulsion.electrical_input_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="battery_navigation_range",
          label="Battery-only Navigation Range",
          value=scenario.navigation_energy.navigation_range_nm,
          unit="NM",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="daily_solar_energy",
          label="Daily Solar Production",
          value=scenario.solar.daily_solar_energy_kwh,
          unit="kWh/day",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="net_external_energy",
          label="Net External Energy Requirement",
          value=scenario.daily_energy_balance.net_external_energy_required_kwh,
          unit="kWh/day",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
  )
  compliance_values = tuple(
      ComplianceDisplayValue(
          criterion=check.criterion,
          label=COMPLIANCE_LABELS[check.criterion],
          actual_value=check.actual_value,
          required_value=check.required_value,
          status=check.status,
      )
      for check in scenario.compliance.checks
  )
  detail_values = (
      TechnicalDisplayValue(
          key="effective_power",
          label="Effective Power",
          value=scenario.resistance.effective_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="motor_output_power",
          label="Motor Mechanical Output",
          value=scenario.propulsion.motor_output_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="energy_per_nm",
          label="Energy per Nautical Mile",
          value=scenario.navigation_energy.energy_per_nm_kwh,
          unit="kWh/NM",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="solar_coverage",
          label="Solar Coverage",
          value=scenario.daily_energy_balance.solar_coverage_ratio,
          unit="ratio",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="excess_solar_energy",
          label="Excess Solar Energy",
          value=scenario.daily_energy_balance.excess_solar_energy_kwh,
          unit="kWh/day",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
  )

  return TechnicalScenarioPresentation(
      overall_status=scenario.compliance.overall_status,
      primary_values=primary_values,
      compliance_values=compliance_values,
      detail_values=detail_values,
  )
