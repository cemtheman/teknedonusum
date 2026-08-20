"""Assemble same-speed normative decision summaries for V1, V2, and V3."""

from calculations.normative_decision_summary import (
    build_normative_decision_summary,
)
from calculations.normative_sizing import calculate_normative_sizing
from config.vessels import BASE_VESSEL_SPECS
from models.normative_decision_summary import NormativeDecisionSummary
from models.normative_vessel_comparison import (
    EXPECTED_NORMATIVE_VESSEL_IDS,
    NormativeComparisonAssumptionSnapshot,
    NormativeVesselComparisonResult,
    NormativeVesselComparisonRow,
)


def _common_assumptions(
    summary: NormativeDecisionSummary,
) -> NormativeComparisonAssumptionSnapshot:
  source = summary.assumptions
  return NormativeComparisonAssumptionSnapshot(
      motor_efficiency=source.motor_efficiency,
      operating_hours_per_day=source.operating_hours_per_day,
      duty_cycle=source.duty_cycle,
      effective_powered_hours_per_day=source.effective_powered_hours_per_day,
      usable_energy_fraction=source.usable_energy_fraction,
      reserve_fraction=source.reserve_fraction,
      motor_unit_cost_per_total_installed_kw=(
          source.motor_unit_cost_per_total_installed_kw
      ),
      battery_unit_cost_per_nominal_kwh=(
          source.battery_unit_cost_per_nominal_kwh
      ),
  )


def _comparison_row(
    summary: NormativeDecisionSummary,
) -> NormativeVesselComparisonRow:
  return NormativeVesselComparisonRow(
      vessel_id=summary.vessel_id,
      vessel_type=summary.vessel_type,
      passenger_capacity=BASE_VESSEL_SPECS[summary.vessel_id]["capacity"],
      selected_speed_knots=summary.selected_speed_knots,
      profile_version=summary.profile_version,
      methodology_status=summary.methodology_status,
      validation_status=summary.validation_status,
      intended_use=summary.intended_use,
      preliminary_only=summary.preliminary_only,
      externally_validated=summary.externally_validated,
      twin_motor_configuration=summary.twin_motor_configuration,
      motor_system_multiplier=summary.assumptions.motor_system_multiplier,
      min_installed_mechanical_power_kw=(
          summary.min_envelope_installed_mechanical_power_kw
      ),
      reference_installed_mechanical_power_kw=(
          summary.reference_estimate_installed_mechanical_power_kw
      ),
      max_installed_mechanical_power_kw=(
          summary.max_envelope_installed_mechanical_power_kw
      ),
      min_daily_propulsion_energy_kwh=(
          summary.min_envelope_daily_propulsion_energy_kwh
      ),
      reference_daily_propulsion_energy_kwh=(
          summary.reference_estimate_daily_propulsion_energy_kwh
      ),
      max_daily_propulsion_energy_kwh=(
          summary.max_envelope_daily_propulsion_energy_kwh
      ),
      min_nominal_battery_capacity_kwh=(
          summary.min_envelope_nominal_battery_capacity_kwh
      ),
      reference_nominal_battery_capacity_kwh=(
          summary.reference_estimate_nominal_battery_capacity_kwh
      ),
      max_nominal_battery_capacity_kwh=(
          summary.max_envelope_nominal_battery_capacity_kwh
      ),
      currency=summary.currency,
      min_propulsion_system_cost=summary.min_envelope_propulsion_system_cost,
      reference_propulsion_system_cost=(
          summary.reference_estimate_propulsion_system_cost
      ),
      max_propulsion_system_cost=summary.max_envelope_propulsion_system_cost,
      assumptions=_common_assumptions(summary),
  )


def build_normative_vessel_comparison(
    selected_speed_knots: float,
) -> NormativeVesselComparisonResult:
  """Build export-ready rows without adding calculations or ranking."""
  summaries = tuple(
      build_normative_decision_summary(
          calculate_normative_sizing(vessel_id, selected_speed_knots)
      )
      for vessel_id in EXPECTED_NORMATIVE_VESSEL_IDS
  )
  rows = tuple(_comparison_row(summary) for summary in summaries)
  return NormativeVesselComparisonResult(
      selected_speed_knots=selected_speed_knots,
      currency=rows[0].currency,
      assumptions=rows[0].assumptions,
      rows=rows,
  )
