"""Bind v0.2 vessel sizing and PVGIS climatology to seasonal SOC simulation."""

from calculations.normative_sizing import calculate_normative_sizing
from calculations.seasonal_energy_balance import simulate_seasonal_vessel_energy
from config.operational_profile import (
    BATTERY_CHARGE_EFFICIENCY,
    BATTERY_DISCHARGE_EFFICIENCY,
    DEFAULT_OPERATION_START_HOUR_LOCAL,
)
from config.solar_assumptions import SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2


def installed_pv_kwp(spec):
  solar_area_m2 = float(spec["loa"]) * float(spec["beam"]) * 0.80
  return solar_area_m2 * SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2


def build_vessel_hourly_energy_balance(
    *,
    vessel_id,
    spec,
    cruise_speed,
    daily_miles,
    season_start,
    season_end,
    typical_hourly_specific_pv,
    operating_days=None,
    sizing_calculator=calculate_normative_sizing,
    auxiliary_power_kw=0.0,
    auxiliary_operating_hours_per_day=0.0,
):
  sizing = sizing_calculator(vessel_id, cruise_speed, daily_miles)

  return simulate_seasonal_vessel_energy(
      season_start=season_start,
      season_end=season_end,
      typical_hourly_specific_pv=typical_hourly_specific_pv,
      operating_days=operating_days,
      installed_pv_kwp=installed_pv_kwp(spec),
      propulsion_power_kw=sizing.reference_electrical_input_power_kw,
      cruise_hours_per_day=sizing.operating_hours_per_day,
      nominal_battery_kwh=sizing.reference_nominal_battery_capacity_kwh,
      usable_fraction=sizing.usable_energy_fraction,
      reserve_fraction=sizing.reserve_fraction,
      operation_start_hour_local=DEFAULT_OPERATION_START_HOUR_LOCAL,
      charge_efficiency=BATTERY_CHARGE_EFFICIENCY,
      discharge_efficiency=BATTERY_DISCHARGE_EFFICIENCY,
      auxiliary_power_kw=auxiliary_power_kw,
      auxiliary_operating_hours_per_day=auxiliary_operating_hours_per_day,
  )
