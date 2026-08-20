"""Map a normative sizing result into a technical decision-summary contract."""

from models.normative_decision_summary import (
    NormativeDecisionAssumptionSnapshot,
    NormativeDecisionSummary,
)
from models.normative_sizing import NormativeSizingResult


def build_normative_decision_summary(
    sizing: NormativeSizingResult,
) -> NormativeDecisionSummary:
  """Copy sizing outputs without introducing engineering or cost calculations."""
  if not isinstance(sizing, NormativeSizingResult):
    raise TypeError("sizing must be a NormativeSizingResult")

  assumptions = NormativeDecisionAssumptionSnapshot(
      motor_efficiency=sizing.motor_efficiency,
      operating_hours_per_day=sizing.operating_hours_per_day,
      duty_cycle=sizing.duty_cycle,
      effective_powered_hours_per_day=sizing.effective_powered_hours_per_day,
      usable_energy_fraction=sizing.usable_energy_fraction,
      reserve_fraction=sizing.reserve_fraction,
      motor_unit_cost_per_total_installed_kw=(
          sizing.motor_unit_cost_per_total_installed_kw
      ),
      battery_unit_cost_per_nominal_kwh=(
          sizing.battery_unit_cost_per_nominal_kwh
      ),
      motor_system_multiplier=sizing.motor_system_multiplier,
  )
  return NormativeDecisionSummary(
      vessel_id=sizing.vessel_id,
      vessel_type=sizing.vessel_type,
      selected_speed_knots=sizing.selected_speed_knots,
      profile_version=sizing.profile_version,
      methodology_status=sizing.assumption_status,
      validation_status="not externally validated / non-certified",
      intended_use="preliminary vessel conversion sizing / decision support",
      preliminary_only=True,
      externally_validated=False,
      twin_motor_configuration=sizing.motor_count == 2,
      min_envelope_installed_mechanical_power_kw=(
          sizing.min_installed_mechanical_power_kw
      ),
      reference_estimate_installed_mechanical_power_kw=(
          sizing.reference_installed_mechanical_power_kw
      ),
      max_envelope_installed_mechanical_power_kw=(
          sizing.max_installed_mechanical_power_kw
      ),
      reference_electrical_input_power_kw=(
          sizing.reference_electrical_input_power_kw
      ),
      min_envelope_daily_propulsion_energy_kwh=(
          sizing.min_daily_propulsion_energy_kwh
      ),
      reference_estimate_daily_propulsion_energy_kwh=(
          sizing.reference_daily_propulsion_energy_kwh
      ),
      max_envelope_daily_propulsion_energy_kwh=(
          sizing.max_daily_propulsion_energy_kwh
      ),
      min_envelope_nominal_battery_capacity_kwh=(
          sizing.min_nominal_battery_capacity_kwh
      ),
      reference_estimate_nominal_battery_capacity_kwh=(
          sizing.reference_nominal_battery_capacity_kwh
      ),
      max_envelope_nominal_battery_capacity_kwh=(
          sizing.max_nominal_battery_capacity_kwh
      ),
      currency=sizing.currency,
      min_envelope_propulsion_system_cost=sizing.min_propulsion_system_cost,
      reference_estimate_propulsion_system_cost=(
          sizing.reference_propulsion_system_cost
      ),
      max_envelope_propulsion_system_cost=sizing.max_propulsion_system_cost,
      assumptions=assumptions,
      limitation_ids=(
          "market_envelope_power_sizing",
          "not_manufacturer_certified",
          "not_sea_trial_validated",
          "propulsion_energy_only",
          "auxiliary_and_hotel_loads_excluded",
          "defined_motor_and_battery_cost_baseline_only",
          "solar_and_charging_infrastructure_excluded",
      ),
  )
