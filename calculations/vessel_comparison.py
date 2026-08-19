"""Structured technical comparison for the three primary vessel types.

This layer only assembles results from the existing v1 preliminary scenario and
the existing calibrated vessel-physics calculation. It introduces no new
hydrodynamic, resistance, catamaran, propulsion, or energy prediction formula.
"""

from dataclasses import dataclass

from calculations.technical_scenario import (
    evaluate_preliminary_technical_scenario,
)
from calculations.vessel_physics import calc_calibrated_vessel_physics
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.compliance import ComplianceStatus


@dataclass(frozen=True)
class VesselTechnicalComparisonRow:
  vessel_id: str
  vessel_name: str
  hull_type: str
  passenger_capacity: int
  selected_cruise_speed_knots: float
  battery_capacity_kwh: float
  calculated_cruise_power_kw: float
  daily_propulsion_energy_kwh: float
  solar_energy_contribution_kwh: float
  net_grid_energy_requirement_kwh: float
  estimated_navigation_range_nm: float | None
  commission_compliance_status: ComplianceStatus | None
  estimate_basis: str


def build_vessel_technical_comparison(
    vessel_specs,
    cruise_speed: float,
    daily_miles: float,
    sun_hours: float,
) -> tuple[VesselTechnicalComparisonRow, ...]:
  """Build v1/v2/v3 comparison rows from existing calculation models.

  v1 uses the preliminary technical scenario. v2 and v3 use the calibrated
  legacy vessel-physics model; no catamaran resistance theory is inferred.
  Their range and full commission status remain unavailable because the
  calibrated result does not establish those quantities.
  """
  vessel_ids = ("v1", "v2", "v3")
  missing_vessel_ids = [key for key in vessel_ids if key not in vessel_specs]
  if missing_vessel_ids:
    raise ValueError(
        "vessel_specs must contain v1, v2, and v3"
    )

  v1_spec = vessel_specs["v1"]
  assumptions = V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
  v1_scenario = evaluate_preliminary_technical_scenario(
      geometry=PRELIMINARY_VESSEL_GEOMETRY["v1"],
      constraints=DALYAN_COMMISSION_CONSTRAINTS,
      passenger_capacity=v1_spec["capacity"],
      speed_knots=cruise_speed,
      daily_distance_nm=daily_miles,
      form_factor=assumptions.form_factor,
      residual_resistance_n=assumptions.residual_resistance_n,
      appendage_resistance_n=assumptions.appendage_resistance_n,
      propulsive_efficiency=assumptions.propulsive_efficiency,
      motor_efficiency=assumptions.motor_efficiency,
      design_margin_fraction=assumptions.design_margin_fraction,
      battery_capacity_kwh=v1_spec["batCapacity"],
      usable_energy_fraction=assumptions.usable_energy_fraction,
      operational_reserve_fraction=assumptions.operational_reserve_fraction,
      hotel_load_kw=assumptions.hotel_load_kw,
      roof_length_fraction_of_loa=assumptions.roof_length_fraction_of_loa,
      usable_roof_width_m=assumptions.usable_roof_width_m,
      panel_coverage_fraction=assumptions.panel_coverage_fraction,
      panel_efficiency=assumptions.panel_efficiency,
      peak_sun_hours=sun_hours,
      solar_derating_factor=assumptions.solar_derating_factor,
  )
  rows = [
      VesselTechnicalComparisonRow(
          vessel_id="v1",
          vessel_name=v1_spec["name"],
          hull_type=v1_spec["hull"],
          passenger_capacity=v1_spec["capacity"],
          selected_cruise_speed_knots=cruise_speed,
          battery_capacity_kwh=v1_spec["batCapacity"],
          calculated_cruise_power_kw=(
              v1_scenario.propulsion.electrical_input_power_kw
          ),
          daily_propulsion_energy_kwh=(
              v1_scenario.daily_energy_balance.propulsion_energy_kwh
          ),
          solar_energy_contribution_kwh=(
              v1_scenario.solar.daily_solar_energy_kwh
          ),
          net_grid_energy_requirement_kwh=(
              v1_scenario.daily_energy_balance.net_external_energy_required_kwh
          ),
          estimated_navigation_range_nm=(
              v1_scenario.navigation_energy.navigation_range_nm
          ),
          commission_compliance_status=(
              v1_scenario.compliance.overall_status
          ),
          estimate_basis="preliminary_technical_scenario",
      )
  ]

  for vessel_id in ("v2", "v3"):
    spec = vessel_specs[vessel_id]
    physics = calc_calibrated_vessel_physics(
        spec,
        cruise_spd=cruise_speed,
        d_miles=daily_miles,
        s_hours=sun_hours,
    )
    rows.append(
        VesselTechnicalComparisonRow(
            vessel_id=vessel_id,
            vessel_name=spec["name"],
            hull_type=spec["hull"],
            passenger_capacity=spec["capacity"],
            selected_cruise_speed_knots=cruise_speed,
            battery_capacity_kwh=spec["batCapacity"],
            calculated_cruise_power_kw=physics.cruise_power,
            daily_propulsion_energy_kwh=physics.brut_kwh,
            solar_energy_contribution_kwh=physics.solar_kwh,
            net_grid_energy_requirement_kwh=physics.net_grid_kwh,
            estimated_navigation_range_nm=None,
            commission_compliance_status=None,
            estimate_basis="calibrated_preliminary",
        )
    )

  return tuple(rows)
