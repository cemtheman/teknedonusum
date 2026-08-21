"""Hourly solar-first propulsion and battery-SOC simulation."""

from datetime import datetime, timedelta

from models.seasonal_energy_balance import SeasonalVesselEnergyBalance


def _hour_overlap(start_hour, duration_hours, hour):
  """Return propulsion-active fraction of one local clock hour."""
  route_start = float(start_hour)
  route_end = route_start + float(duration_hours)
  bucket_start = float(hour)
  bucket_end = bucket_start + 1.0
  return max(0.0, min(route_end, bucket_end) - max(route_start, bucket_start))


def simulate_seasonal_vessel_energy(
    *,
    season_start,
    season_end,
    typical_hourly_specific_pv,
    installed_pv_kwp,
    propulsion_power_kw,
    cruise_hours_per_day,
    nominal_battery_kwh,
    usable_fraction,
    reserve_fraction,
    operation_start_hour_local=9.0,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
):
  """Simulate one vessel over every calendar day in the selected season.

  Solar feeds propulsion first during route hours. Solar surplus and all solar
  outside route hours charge the battery. Battery supplies only the propulsion
  deficit. Shore energy appears only when the battery reaches its reserve floor.
  """
  if season_end < season_start:
    raise ValueError("season_end must not be before season_start")
  if installed_pv_kwp < 0 or propulsion_power_kw < 0:
    raise ValueError("power values must be non-negative")
  if cruise_hours_per_day <= 0 or cruise_hours_per_day > 24:
    raise ValueError("cruise_hours_per_day must be in (0, 24]")
  if nominal_battery_kwh <= 0:
    raise ValueError("nominal_battery_kwh must be positive")
  if not 0 < usable_fraction <= 1:
    raise ValueError("usable_fraction must be in (0, 1]")
  if not 0 <= reserve_fraction < usable_fraction:
    raise ValueError("reserve_fraction must be below usable_fraction")
  if not 0 < charge_efficiency <= 1:
    raise ValueError("charge_efficiency must be in (0, 1]")
  if not 0 < discharge_efficiency <= 1:
    raise ValueError("discharge_efficiency must be in (0, 1]")

  max_soc = nominal_battery_kwh * usable_fraction
  min_soc = nominal_battery_kwh * reserve_fraction
  soc = max_soc

  season_propulsion = 0.0
  season_solar = 0.0
  direct_solar = 0.0
  battery_discharge = 0.0
  battery_charge = 0.0
  curtailed_solar = 0.0
  shore_energy = 0.0
  solar_only_hours = 0.0
  minimum_soc = soc

  current = season_start
  while current <= season_end:
    for hour in range(24):
      specific_power = float(
          typical_hourly_specific_pv.get(
              (current.month, current.day, hour),
              0.0,
          )
      )
      solar_power_kw = installed_pv_kwp * max(0.0, specific_power)
      solar_energy_kwh = solar_power_kw
      season_solar += solar_energy_kwh

      active_hours = _hour_overlap(
          operation_start_hour_local,
          cruise_hours_per_day,
          hour,
      )
      propulsion_energy_kwh = propulsion_power_kw * active_hours
      season_propulsion += propulsion_energy_kwh

      solar_direct_kwh = min(
          propulsion_power_kw,
          solar_power_kw,
      ) * active_hours
      direct_solar += solar_direct_kwh

      propulsion_deficit_kwh = max(
          0.0,
          propulsion_energy_kwh - solar_direct_kwh,
      )

      available_to_bus = max(
          0.0,
          (soc - min_soc) * discharge_efficiency,
      )
      battery_to_propulsion_kwh = min(
          propulsion_deficit_kwh,
          available_to_bus,
      )
      if battery_to_propulsion_kwh > 0:
        soc -= battery_to_propulsion_kwh / discharge_efficiency
      battery_discharge += battery_to_propulsion_kwh

      shore_energy += max(
          0.0,
          propulsion_deficit_kwh - battery_to_propulsion_kwh,
      )

      if active_hours > 0 and solar_power_kw >= propulsion_power_kw:
        solar_only_hours += active_hours

      solar_surplus_active_kwh = max(
          0.0,
          solar_power_kw - propulsion_power_kw,
      ) * active_hours
      solar_inactive_kwh = solar_power_kw * (1.0 - active_hours)
      solar_for_charge_bus_kwh = (
          solar_surplus_active_kwh + solar_inactive_kwh
      )

      storage_room_kwh = max(0.0, max_soc - soc)
      storable_kwh = solar_for_charge_bus_kwh * charge_efficiency
      charged_kwh = min(storage_room_kwh, storable_kwh)
      soc += charged_kwh
      battery_charge += charged_kwh

      solar_used_for_charge_bus_kwh = (
          charged_kwh / charge_efficiency
          if charge_efficiency > 0
          else 0.0
      )
      curtailed_solar += max(
          0.0,
          solar_for_charge_bus_kwh - solar_used_for_charge_bus_kwh,
      )
      minimum_soc = min(minimum_soc, soc)

    current += timedelta(days=1)

  return SeasonalVesselEnergyBalance(
      season_propulsion_kwh=season_propulsion,
      season_solar_generation_kwh=season_solar,
      solar_direct_to_propulsion_kwh=direct_solar,
      battery_discharge_to_propulsion_kwh=battery_discharge,
      battery_charge_from_solar_kwh=battery_charge,
      curtailed_solar_kwh=curtailed_solar,
      shore_energy_kwh=shore_energy,
      initial_soc_kwh=max_soc,
      final_soc_kwh=soc,
      minimum_soc_kwh=minimum_soc,
      solar_only_propulsion_hours=solar_only_hours,
  )
