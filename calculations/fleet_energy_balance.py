"""Fleet-level v0.2 propulsion-energy, solar, grid, and CO2 aggregation."""

from dataclasses import dataclass
from math import isfinite

from calculations.normative_sizing import calculate_normative_sizing
from calculations.vessel_detail_analysis import TECHNICAL_PROFILE_BY_VESSEL
from config.solar_assumptions import SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2


@dataclass(frozen=True)
class FleetEnergyBalance:
  daily_propulsion_kwh: float
  daily_solar_kwh: float
  daily_grid_kwh: float
  annual_grid_kwh: float
  annual_solar_kwh: float
  solar_coverage_ratio: float
  total_co2_reduction_tonnes: float
  equivalent_trees: int


def _diesel_baseline_lph(spec, cruise_speed_knots):
  exponent = 3.3 if spec["hull"] == "monohull" else 2.85
  return 30.0 * ((cruise_speed_knots / 10.0) ** exponent)


def _daily_solar_kwh(
    spec,
    *,
    average_daily_specific_yield_kwh_per_kwp=None,
    sun_hours=None,
):
  solar_area_m2 = spec["loa"] * spec["beam"] * 0.80

  if average_daily_specific_yield_kwh_per_kwp is not None:
    installed_solar_kwp = (
        solar_area_m2 * SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2
    )
    return installed_solar_kwp * float(
        average_daily_specific_yield_kwh_per_kwp
    )

  if sun_hours is None:
    raise ValueError(
        "average_daily_specific_yield_kwh_per_kwp or legacy sun_hours is required"
    )

  return solar_area_m2 * 0.15 * float(sun_hours)


def build_fleet_energy_balance(
    vessel_specs,
    counts,
    cruise_speed,
    daily_miles,
    sun_hours,
    operating_days,
    *,
    average_daily_specific_yield_kwh_per_kwp=None,
    sizing_calculator=calculate_normative_sizing,
):
  daily_propulsion_kwh = 0.0
  daily_solar_kwh = 0.0
  daily_grid_kwh = 0.0
  total_co2_reduction_tonnes = 0.0

  for vessel_key, spec in vessel_specs.items():
    count = counts.get(vessel_key, 0)
    if count <= 0:
      continue

    try:
      technical_profile_id = TECHNICAL_PROFILE_BY_VESSEL[vessel_key]
    except KeyError as exc:
      raise ValueError(f"unsupported vessel key: {vessel_key}") from exc

    sizing = sizing_calculator(
        technical_profile_id,
        cruise_speed,
        daily_miles,
    )

    propulsion_kwh = sizing.reference_daily_propulsion_energy_kwh
    solar_kwh = _daily_solar_kwh(
        spec,
        average_daily_specific_yield_kwh_per_kwp=(
            average_daily_specific_yield_kwh_per_kwp
        ),
        sun_hours=sun_hours,
    )
    grid_kwh = max(0.0, propulsion_kwh - solar_kwh)

    cruise_hours = sizing.operating_hours_per_day
    old_diesel_lph = _diesel_baseline_lph(spec, cruise_speed)
    old_co2_tonnes = (
        spec["merged"]
        * old_diesel_lph
        * cruise_hours
        * operating_days
        * 2.68
    ) / 1000.0
    new_co2_tonnes = (grid_kwh * operating_days * 0.44) / 1000.0

    daily_propulsion_kwh += propulsion_kwh * count
    daily_solar_kwh += solar_kwh * count
    daily_grid_kwh += grid_kwh * count
    total_co2_reduction_tonnes += (
        old_co2_tonnes - new_co2_tonnes
    ) * count

  annual_grid_kwh = daily_grid_kwh * operating_days
  annual_solar_kwh = daily_solar_kwh * operating_days
  solar_coverage_ratio = (
      (daily_solar_kwh / daily_propulsion_kwh) * 100.0
      if daily_propulsion_kwh > 0
      else 0.0
  )
  equivalent_trees = int(total_co2_reduction_tonnes / 0.022)

  result = FleetEnergyBalance(
      daily_propulsion_kwh=daily_propulsion_kwh,
      daily_solar_kwh=daily_solar_kwh,
      daily_grid_kwh=daily_grid_kwh,
      annual_grid_kwh=annual_grid_kwh,
      annual_solar_kwh=annual_solar_kwh,
      solar_coverage_ratio=solar_coverage_ratio,
      total_co2_reduction_tonnes=total_co2_reduction_tonnes,
      equivalent_trees=equivalent_trees,
  )

  if any(
      not isfinite(value)
      for value in (
          result.daily_propulsion_kwh,
          result.daily_solar_kwh,
          result.daily_grid_kwh,
          result.annual_grid_kwh,
          result.annual_solar_kwh,
          result.solar_coverage_ratio,
          result.total_co2_reduction_tonnes,
      )
  ):
    raise ValueError("fleet energy balance produced non-finite values")

  return result
