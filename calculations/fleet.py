from calculations.vessel_physics import calc_calibrated_vessel_physics
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

  # --- Fleet Total CO2 Reduction, Tree Equivalent & Energy Balance Calculation ---
  fleet_total_co2_reduction = 0.0
  fleet_daily_solar_kwh = 0.0
  fleet_daily_grid_kwh = 0.0
  fleet_daily_brut_kwh = 0.0

  for k, spec_item in vessel_specs.items():
    if counts[k] > 0:
      p = calc_calibrated_vessel_physics(
          spec_item, cruise_speed, daily_miles, sun_hours
      )

      co2_old = (
          spec_item["merged"]
          * p.cruise_diesel_lph
          * p.cruise_hours
          * operating_days
          * 2.68
      ) / 1000
      co2_new = (p.net_grid_kwh * operating_days * 0.44) / 1000
      single_co2_saved = co2_old - co2_new

      fleet_total_co2_reduction += single_co2_saved * counts[k]
      fleet_daily_solar_kwh += p.solar_kwh * counts[k]
      fleet_daily_grid_kwh += p.net_grid_kwh * counts[k]
      fleet_daily_brut_kwh += (p.brut_kwh / 0.95) * counts[k]

  equivalent_trees = int(fleet_total_co2_reduction / 0.022)
  fleet_annual_grid_kwh = fleet_daily_grid_kwh * operating_days
  fleet_annual_solar_kwh = fleet_daily_solar_kwh * operating_days
  solar_coverage_ratio = (
      (fleet_daily_solar_kwh / fleet_daily_brut_kwh) * 100
      if fleet_daily_brut_kwh > 0
      else 0
  )

  return FleetResult(
      total_vessels=total_vessels,
      total_capacity=total_capacity,
      grants_per_type=grants_per_type,
      fleet_total_cost=fleet_total_cost,
      fleet_total_grant=fleet_total_grant,
      fleet_total_capex=fleet_total_capex,
      fleet_total_co2_reduction=fleet_total_co2_reduction,
      fleet_daily_solar_kwh=fleet_daily_solar_kwh,
      fleet_daily_grid_kwh=fleet_daily_grid_kwh,
      fleet_daily_brut_kwh=fleet_daily_brut_kwh,
      equivalent_trees=equivalent_trees,
      fleet_annual_grid_kwh=fleet_annual_grid_kwh,
      fleet_annual_solar_kwh=fleet_annual_solar_kwh,
      solar_coverage_ratio=solar_coverage_ratio,
  )
