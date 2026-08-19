from calculations.technical_scenario import PreliminaryTechnicalScenarioResult
from models.presentation import (
    ComplianceDisplayValue,
    TechnicalDisplayValue,
    TechnicalScenarioPresentation,
    TechnicalValueCategory,
)


COMPLIANCE_LABELS = {
    "loa": "Tam Boy (LOA)",
    "passenger_capacity": "Yolcu Kapasitesi",
    "minimum_speed": "Seçilen Senaryo Hızı",
    "minimum_navigation_range": "Seyir Menzili",
    "motor_efficiency": "Motor Verimi",
    "battery_capacity": "Batarya Kapasitesi",
    "roof_length_fraction": "Çatı Uzunluğu / LOA",
}


def build_technical_scenario_presentation(
    scenario: PreliminaryTechnicalScenarioResult,
) -> TechnicalScenarioPresentation:
  if not isinstance(scenario, PreliminaryTechnicalScenarioResult):
    raise TypeError("scenario must be a PreliminaryTechnicalScenarioResult")

  primary_values = (
      TechnicalDisplayValue(
          key="installed_motor_power",
          label="Kurulu Motor Gücü",
          value=scenario.propulsion.installed_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="electrical_input_power",
          label="Elektriksel Giriş Gücü",
          value=scenario.propulsion.electrical_input_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="battery_navigation_range",
          label="Yalnız Batarya ile Seyir Menzili",
          value=scenario.navigation_energy.navigation_range_nm,
          unit="NM",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="daily_solar_energy",
          label="Günlük Güneş Enerjisi Üretimi",
          value=scenario.solar.daily_solar_energy_kwh,
          unit="kWh/day",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="net_external_energy",
          label="Güneş Sonrası Net Enerji İhtiyacı",
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
          label="Efektif Güç",
          value=scenario.resistance.effective_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="motor_output_power",
          label="Motor Çıkış Gücü",
          value=scenario.propulsion.motor_output_power_kw,
          unit="kW",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="energy_per_nm",
          label="Mil Başına Enerji Tüketimi",
          value=scenario.navigation_energy.energy_per_nm_kwh,
          unit="kWh/NM",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="solar_coverage",
          label="Güneş Enerjisi Karşılama Oranı",
          value=scenario.daily_energy_balance.solar_coverage_ratio,
          unit="ratio",
          category=TechnicalValueCategory.PRELIMINARY_ESTIMATE,
      ),
      TechnicalDisplayValue(
          key="excess_solar_energy",
          label="Fazla Güneş Enerjisi",
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
