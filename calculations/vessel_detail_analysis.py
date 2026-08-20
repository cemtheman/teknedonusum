"""v0.2 data adapter for per-vessel technical and economic detail cards."""

from dataclasses import dataclass
from math import isfinite

from calculations.normative_sizing import calculate_normative_sizing
from config.solar_assumptions import SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2
from models.normative_sizing import NormativeSizingResult


TECHNICAL_PROFILE_BY_VESSEL = {
    "v1": "v1",
    "v2": "v2",
    "v3": "v3",
    "v4_24": "v1",
    "v4_32": "v2",
}


@dataclass(frozen=True)
class VesselDetailAnalysis:
  technical_profile_id: str
  sizing: NormativeSizingResult
  solar_area_m2: float
  daily_solar_kwh: float
  daily_grid_kwh: float
  grant_amount_tl: float
  net_capex_tl: float
  old_diesel_lph: float
  old_diesel_cost_tl: float
  old_maintenance_cost_tl: float
  old_total_annual_tl: float
  new_electricity_cost_tl: float
  new_battery_degradation_tl: float
  new_maintenance_cost_tl: float
  new_total_annual_tl: float
  net_savings_tl: float
  payback_seasons: float
  payback_months: float
  old_co2_tonnes: float
  new_co2_tonnes: float
  net_co2_tonnes: float


def _technical_profile_id(vessel_key):
  try:
    return TECHNICAL_PROFILE_BY_VESSEL[vessel_key]
  except KeyError as exc:
    raise ValueError(f"unsupported vessel key: {vessel_key}") from exc


def _diesel_baseline_lph(spec, cruise_speed_knots):
  exponent = 3.3 if spec["hull"] == "monohull" else 2.85
  return 30.0 * ((cruise_speed_knots / 10.0) ** exponent)


def _daily_solar_kwh(spec, inputs):
  solar_area_m2 = spec["loa"] * spec["beam"] * 0.80
  specific_yield = getattr(
      inputs,
      "average_daily_specific_yield_kwh_per_kwp",
      None,
  )

  if specific_yield is not None:
    installed_solar_kwp = (
        solar_area_m2 * SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2
    )
    return solar_area_m2, installed_solar_kwp * specific_yield

  sun_hours = getattr(inputs, "sun_hours", None)
  if sun_hours is None:
    raise ValueError("solar resource is missing")

  return solar_area_m2, solar_area_m2 * 0.15 * sun_hours


def build_vessel_detail_analysis(
    vessel_key,
    spec,
    inputs,
    *,
    sizing_calculator=calculate_normative_sizing,
):
  profile_id = _technical_profile_id(vessel_key)
  sizing = sizing_calculator(
      profile_id,
      inputs.cruise_speed,
      inputs.daily_miles,
  )

  solar_area_m2, daily_solar_kwh = _daily_solar_kwh(spec, inputs)
  daily_grid_kwh = max(
      0.0,
      sizing.reference_daily_propulsion_energy_kwh - daily_solar_kwh,
  )

  grant_amount_tl = min(spec["maxGrant"], spec["totalCost"] * spec["grantRate"])
  net_capex_tl = spec["totalCost"] - grant_amount_tl

  cruise_hours = sizing.operating_hours_per_day
  old_diesel_lph = _diesel_baseline_lph(spec, inputs.cruise_speed)
  old_diesel_cost_tl = (
      spec["merged"]
      * old_diesel_lph
      * cruise_hours
      * inputs.operating_days
      * inputs.diesel_price
  )
  old_maintenance_cost_tl = spec["merged"] * 140000
  old_total_annual_tl = old_diesel_cost_tl + old_maintenance_cost_tl

  new_electricity_cost_tl = (
      daily_grid_kwh * inputs.operating_days * inputs.elec_price
  )

  replacement_battery_cost_tl = spec["batCostEur"] * inputs.eur_rate
  equivalent_full_cycles = (
      sizing.reference_daily_propulsion_energy_kwh
      / sizing.reference_nominal_battery_capacity_kwh
      * inputs.operating_days
  )
  new_battery_degradation_tl = (
      replacement_battery_cost_tl / 3000.0 * equivalent_full_cycles
  )
  new_maintenance_cost_tl = old_maintenance_cost_tl * 0.15
  new_total_annual_tl = (
      new_electricity_cost_tl
      + new_battery_degradation_tl
      + new_maintenance_cost_tl
  )
  net_savings_tl = old_total_annual_tl - new_total_annual_tl

  if net_savings_tl > 0:
    payback_seasons = net_capex_tl / net_savings_tl
    payback_months = payback_seasons * (inputs.operating_days / 30.0)
  else:
    payback_seasons = float("inf")
    payback_months = float("inf")

  old_co2_tonnes = (
      spec["merged"]
      * old_diesel_lph
      * cruise_hours
      * inputs.operating_days
      * 2.68
  ) / 1000.0
  new_co2_tonnes = (daily_grid_kwh * inputs.operating_days * 0.44) / 1000.0
  net_co2_tonnes = old_co2_tonnes - new_co2_tonnes

  analysis = VesselDetailAnalysis(
      technical_profile_id=profile_id,
      sizing=sizing,
      solar_area_m2=solar_area_m2,
      daily_solar_kwh=daily_solar_kwh,
      daily_grid_kwh=daily_grid_kwh,
      grant_amount_tl=grant_amount_tl,
      net_capex_tl=net_capex_tl,
      old_diesel_lph=old_diesel_lph,
      old_diesel_cost_tl=old_diesel_cost_tl,
      old_maintenance_cost_tl=old_maintenance_cost_tl,
      old_total_annual_tl=old_total_annual_tl,
      new_electricity_cost_tl=new_electricity_cost_tl,
      new_battery_degradation_tl=new_battery_degradation_tl,
      new_maintenance_cost_tl=new_maintenance_cost_tl,
      new_total_annual_tl=new_total_annual_tl,
      net_savings_tl=net_savings_tl,
      payback_seasons=payback_seasons,
      payback_months=payback_months,
      old_co2_tonnes=old_co2_tonnes,
      new_co2_tonnes=new_co2_tonnes,
      net_co2_tonnes=net_co2_tonnes,
  )

  finite_values = (
      analysis.solar_area_m2,
      analysis.daily_solar_kwh,
      analysis.daily_grid_kwh,
      analysis.grant_amount_tl,
      analysis.net_capex_tl,
      analysis.old_diesel_lph,
      analysis.old_diesel_cost_tl,
      analysis.old_maintenance_cost_tl,
      analysis.old_total_annual_tl,
      analysis.new_electricity_cost_tl,
      analysis.new_battery_degradation_tl,
      analysis.new_maintenance_cost_tl,
      analysis.new_total_annual_tl,
      analysis.net_savings_tl,
      analysis.old_co2_tonnes,
      analysis.new_co2_tonnes,
      analysis.net_co2_tonnes,
  )
  if any(not isfinite(value) for value in finite_values):
    raise ValueError("detail analysis produced non-finite values")

  return analysis
