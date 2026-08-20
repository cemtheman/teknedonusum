"""Orchestrate the standalone v0.2 normative vessel-sizing chain."""

from calculations.battery_capacity_envelope import (
    calculate_nominal_battery_capacity_envelope,
)
from calculations.electrical_power_envelope import (
    convert_to_electrical_input_power_envelope,
)
from calculations.operational_energy_envelope import (
    calculate_daily_propulsion_energy_envelope,
)
from calculations.power_envelope import (
    interpolate_installed_mechanical_power_envelope,
)
from calculations.propulsion_cost_envelope import (
    calculate_propulsion_system_cost_envelope,
)
from config.normative_operational_profiles import (
    NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
)
from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from models.normative_sizing import NormativeSizingResult


def calculate_normative_sizing(
    vessel_id: str,
    selected_speed_knots: float,
) -> NormativeSizingResult:
  """Run Commit 51–55 APIs without changing the legacy production path."""
  if vessel_id not in NORMATIVE_POWER_ENVELOPES:
    raise ValueError("vessel_id must be one of v1, v2, or v3")

  profile = NORMATIVE_POWER_ENVELOPES[vessel_id]
  mechanical = interpolate_installed_mechanical_power_envelope(
      profile,
      selected_speed_knots,
  )
  electrical = convert_to_electrical_input_power_envelope(mechanical)
  energy = calculate_daily_propulsion_energy_envelope(
      vessel_id,
      electrical,
      NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION,
  )
  battery = calculate_nominal_battery_capacity_envelope(energy)
  cost = calculate_propulsion_system_cost_envelope(
      vessel_id,
      mechanical,
      battery,
  )

  downstream = (electrical, energy, battery, cost)
  if any(result.speed_knots != selected_speed_knots for result in downstream):
    raise RuntimeError("downstream sizing speeds must remain consistent")
  if any(
      result.vessel_id != vessel_id
      for result in (energy, battery, cost)
  ):
    raise RuntimeError("downstream sizing vessel IDs must remain consistent")

  return NormativeSizingResult(
      vessel_id=vessel_id,
      vessel_type=profile.vessel_type,
      selected_speed_knots=selected_speed_knots,
      profile_version=profile.profile_version,
      assumption_status=profile.assumption_status,
      power_envelope_source_basis=profile.provenance,
      cost_baseline_status=cost.cost_basis_provenance,
      limitations=(
          "Normative preliminary reference estimate; not certified performance",
          "Propulsion electrical energy only; auxiliary loads are excluded",
          "Cost includes the existing motor and battery baselines only",
      ),
      min_installed_mechanical_power_kw=(
          mechanical.min_installed_mechanical_power_kw
      ),
      reference_installed_mechanical_power_kw=(
          mechanical.reference_installed_power_kw
      ),
      max_installed_mechanical_power_kw=(
          mechanical.max_installed_mechanical_power_kw
      ),
      motor_efficiency=electrical.motor_efficiency,
      min_electrical_input_power_kw=electrical.min_electrical_input_power_kw,
      reference_electrical_input_power_kw=(
          electrical.reference_electrical_input_power_kw
      ),
      max_electrical_input_power_kw=electrical.max_electrical_input_power_kw,
      operating_hours_per_day=energy.operating_hours_per_day,
      duty_cycle=energy.duty_cycle,
      effective_powered_hours_per_day=energy.effective_powered_hours_per_day,
      min_daily_propulsion_energy_kwh=energy.min_daily_electrical_energy_kwh,
      reference_daily_propulsion_energy_kwh=(
          energy.reference_daily_electrical_energy_kwh
      ),
      max_daily_propulsion_energy_kwh=energy.max_daily_electrical_energy_kwh,
      usable_energy_fraction=battery.usable_soc_fraction,
      reserve_fraction=battery.reserve_fraction,
      effective_usable_energy_fraction=(
          battery.effective_usable_energy_fraction
      ),
      min_nominal_battery_capacity_kwh=(
          battery.min_nominal_battery_capacity_kwh
      ),
      reference_nominal_battery_capacity_kwh=(
          battery.reference_nominal_battery_capacity_kwh
      ),
      max_nominal_battery_capacity_kwh=(
          battery.max_nominal_battery_capacity_kwh
      ),
      currency=cost.currency,
      motor_count=cost.motor_count,
      motor_unit_cost_per_total_installed_kw=(
          cost.motor_cost_per_total_installed_kw
      ),
      motor_system_multiplier=cost.motor_system_multiplier,
      battery_unit_cost_per_nominal_kwh=cost.battery_cost_per_nominal_kwh,
      min_propulsion_system_cost=cost.min_total_propulsion_system_cost,
      reference_propulsion_system_cost=(
          cost.reference_total_propulsion_system_cost
      ),
      max_propulsion_system_cost=cost.max_total_propulsion_system_cost,
  )
