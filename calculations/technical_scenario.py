"""Orchestration for a preliminary vessel technical scenario.

Scenario-speed compliance only means that the evaluated scenario speed meets
the configured threshold. It does not prove that the vessel can attain that
speed and is not final sea-trial capability evidence.
"""

from dataclasses import dataclass

from calculations.compliance import evaluate_commission_compliance
from calculations.energy import NavigationEnergyResult, calculate_navigation_energy
from calculations.energy_balance import (
    DailyEnergyBalanceResult,
    calculate_daily_energy_balance,
)
from calculations.propulsion import (
    PropulsionPowerResult,
    calculate_direct_drive_propulsion_power,
)
from calculations.resistance_sensitivity import (
    ResistanceSensitivityResult,
    calculate_resistance_sensitivity,
)
from calculations.solar import SolarEnergyResult, calculate_solar_energy
from models.compliance import CommissionComplianceResult
from models.constraints import CommissionTechnicalConstraints
from models.geometry import PreliminaryVesselGeometry


@dataclass(frozen=True)
class PreliminaryTechnicalScenarioResult:
  resistance: ResistanceSensitivityResult
  propulsion: PropulsionPowerResult
  navigation_energy: NavigationEnergyResult
  solar: SolarEnergyResult
  daily_energy_balance: DailyEnergyBalanceResult
  compliance: CommissionComplianceResult


def evaluate_preliminary_technical_scenario(
    geometry: PreliminaryVesselGeometry,
    constraints: CommissionTechnicalConstraints,
    passenger_capacity: int,
    speed_knots: float,
    daily_distance_nm: float,
    form_factor: float,
    residual_resistance_n: float,
    appendage_resistance_n: float,
    propulsive_efficiency: float,
    motor_efficiency: float,
    design_margin_fraction: float,
    battery_capacity_kwh: float,
    usable_energy_fraction: float,
    operational_reserve_fraction: float,
    hotel_load_kw: float,
    roof_length_fraction_of_loa: float,
    usable_roof_width_m: float,
    panel_coverage_fraction: float,
    panel_efficiency: float,
    peak_sun_hours: float,
    solar_derating_factor: float,
) -> PreliminaryTechnicalScenarioResult:
  """Evaluate one scenario without asserting verified vessel capability."""
  if not daily_distance_nm >= 0:
    raise ValueError("daily_distance_nm must be non-negative")

  resistance = calculate_resistance_sensitivity(
      geometry,
      speed_knots,
      form_factor,
      residual_resistance_n,
      appendage_resistance_n,
  )
  propulsion = calculate_direct_drive_propulsion_power(
      resistance.effective_power_kw,
      propulsive_efficiency,
      motor_efficiency,
      design_margin_fraction,
  )
  navigation_energy = calculate_navigation_energy(
      speed_knots,
      battery_capacity_kwh,
      propulsion.electrical_input_power_kw,
      hotel_load_kw,
      usable_energy_fraction,
      operational_reserve_fraction,
  )
  solar = calculate_solar_energy(
      geometry.loa_m.value,
      roof_length_fraction_of_loa,
      usable_roof_width_m,
      panel_coverage_fraction,
      panel_efficiency,
      peak_sun_hours,
      solar_derating_factor,
  )

  operating_hours = daily_distance_nm / speed_knots
  daily_energy_balance = calculate_daily_energy_balance(
      operating_hours,
      propulsion.electrical_input_power_kw,
      hotel_load_kw,
      solar.daily_solar_energy_kwh,
  )
  compliance = evaluate_commission_compliance(
      constraints,
      geometry.loa_m.value,
      passenger_capacity,
      speed_knots,
      navigation_energy.navigation_range_nm,
      motor_efficiency,
      battery_capacity_kwh,
      roof_length_fraction_of_loa,
  )

  return PreliminaryTechnicalScenarioResult(
      resistance=resistance,
      propulsion=propulsion,
      navigation_energy=navigation_energy,
      solar=solar,
      daily_energy_balance=daily_energy_balance,
      compliance=compliance,
  )
