from models.results import VesselEconomicsResult


def calculate_vessel_economics(
    spec,
    physics,
    eur_rate,
    diesel_price,
    elec_price,
    operating_days,
):
  motor_multiplier = 1.20 if spec["motors"] == 2 else 1.0
  motor_cost_tl = physics.max_power * (400 * eur_rate) * motor_multiplier

  solar_cost_tl = physics.solar_area * (150 * eur_rate)
  bat_cost_tl = spec["batCostEur"] * eur_rate
  infra_share_tl = (750000 * eur_rate) / 150

  hull_cost_tl = spec["totalCost"] - (
      motor_cost_tl + solar_cost_tl + bat_cost_tl + infra_share_tl
  )

  total_investment = spec["totalCost"]
  grant_amount = min(spec["maxGrant"], spec["totalCost"] * spec["grantRate"])
  net_capex = spec["totalCost"] - grant_amount

  old_diesel_consumption = (
      spec["merged"]
      * physics.cruise_diesel_lph
      * physics.cruise_hours
      * operating_days
  )
  old_diesel_cost = (
      spec["merged"]
      * (
          physics.cruise_diesel_lph
          * physics.cruise_hours
          * operating_days
          * diesel_price
      )
  )
  old_maint_cost = spec["merged"] * 140000
  old_total_annual = old_diesel_cost + old_maint_cost

  grid_electricity_consumption = physics.net_grid_kwh * operating_days
  new_elec_cost = physics.net_grid_kwh * operating_days * elec_price
  new_degradation = (
      (bat_cost_tl / 3000)
      * (physics.brut_kwh / spec["batCapacity"])
      * operating_days
  )
  new_maint_cost = old_maint_cost * 0.15
  new_total_annual = new_elec_cost + new_degradation + new_maint_cost

  net_savings = old_total_annual - new_total_annual

  payback_seasons = net_capex / net_savings if net_savings > 0 else float("inf")
  payback_months = (
      payback_seasons * (operating_days / 30.0)
      if net_savings > 0
      else float("inf")
  )

  old_co2 = (
      spec["merged"]
      * physics.cruise_diesel_lph
      * physics.cruise_hours
      * operating_days
      * 2.68
  ) / 1000
  new_co2 = (physics.net_grid_kwh * operating_days * 0.44) / 1000
  net_co2 = old_co2 - new_co2

  return VesselEconomicsResult(
      motor_cost_tl=motor_cost_tl,
      solar_cost_tl=solar_cost_tl,
      bat_cost_tl=bat_cost_tl,
      infra_share_tl=infra_share_tl,
      hull_cost_tl=hull_cost_tl,
      total_investment=total_investment,
      grant_amount=grant_amount,
      net_capex=net_capex,
      old_diesel_consumption=old_diesel_consumption,
      old_diesel_cost=old_diesel_cost,
      old_maint_cost=old_maint_cost,
      old_total_annual=old_total_annual,
      grid_electricity_consumption=grid_electricity_consumption,
      new_elec_cost=new_elec_cost,
      new_degradation=new_degradation,
      new_maint_cost=new_maint_cost,
      new_total_annual=new_total_annual,
      net_savings=net_savings,
      payback_seasons=payback_seasons,
      payback_months=payback_months,
      old_co2=old_co2,
      new_co2=new_co2,
      net_co2=net_co2,
  )
