from calculations.fleet_energy_balance import build_fleet_energy_balance
from models.results import FleetResult


def calculate_fleet(
    vessel_specs,
    counts,
    cruise_speed,
    daily_miles,
    sun_hours,
    operating_days,
):
  total_vessels = sum(counts.values())
  total_capacity = sum(
      counts[k] * vessel_specs[k]["capacity"] for k in vessel_specs
  )

  grants_per_type = {
      k: min(
          vessel_specs[k]["maxGrant"],
          vessel_specs[k]["totalCost"] * vessel_specs[k]["grantRate"],
      )
      for k in vessel_specs
  }

  fleet_total_cost = sum(
      counts[k] * vessel_specs[k]["totalCost"] for k in vessel_specs
  )
  fleet_total_grant = sum(counts[k] * grants_per_type[k] for k in vessel_specs)
  fleet_total_capex = fleet_total_cost - fleet_total_grant

  energy = build_fleet_energy_balance(
      vessel_specs,
      counts,
      cruise_speed,
      daily_miles,
      sun_hours,
      operating_days,
  )

  return FleetResult(
      total_vessels=total_vessels,
      total_capacity=total_capacity,
      grants_per_type=grants_per_type,
      fleet_total_cost=fleet_total_cost,
      fleet_total_grant=fleet_total_grant,
      fleet_total_capex=fleet_total_capex,
      fleet_total_co2_reduction=energy.total_co2_reduction_tonnes,
      fleet_daily_solar_kwh=energy.daily_solar_kwh,
      fleet_daily_grid_kwh=energy.daily_grid_kwh,
      # Retain the result-field name for compatibility; its v0.2 semantic is
      # total route-based daily propulsion electrical energy before solar.
      fleet_daily_brut_kwh=energy.daily_propulsion_kwh,
      equivalent_trees=energy.equivalent_trees,
      fleet_annual_grid_kwh=energy.annual_grid_kwh,
      fleet_annual_solar_kwh=energy.annual_solar_kwh,
      solar_coverage_ratio=energy.solar_coverage_ratio,
  )
