from dataclasses import dataclass


@dataclass
class VesselPhysicsResult:
  total_disp: float
  payload_weight: float
  battery_weight: float
  max_power: float
  cruise_power: float
  cruise_hours: float
  brut_kwh: float
  solar_area: float
  solar_kwh: float
  net_grid_kwh: float
  cruise_diesel_lph: float


@dataclass
class FleetResult:
  total_vessels: int
  total_capacity: int
  grants_per_type: dict[str, float]
  fleet_total_cost: float
  fleet_total_grant: float
  fleet_total_capex: float
  fleet_total_co2_reduction: float
  fleet_daily_solar_kwh: float
  fleet_daily_grid_kwh: float
  fleet_daily_brut_kwh: float
  equivalent_trees: int
  fleet_annual_grid_kwh: float
  fleet_annual_solar_kwh: float
  solar_coverage_ratio: float


@dataclass
class VesselEconomicsResult:
  motor_cost_tl: float
  solar_cost_tl: float
  bat_cost_tl: float
  infra_share_tl: float
  hull_cost_tl: float
  total_investment: float
  grant_amount: float
  net_capex: float
  old_diesel_consumption: float
  old_diesel_cost: float
  old_maint_cost: float
  old_total_annual: float
  grid_electricity_consumption: float
  new_elec_cost: float
  new_degradation: float
  new_maint_cost: float
  new_total_annual: float
  net_savings: float
  payback_seasons: float
  payback_months: float
  old_co2: float
  new_co2: float
  net_co2: float
