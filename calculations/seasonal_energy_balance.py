"""Hourly solar-first propulsion and battery-SOC simulation."""

from datetime import timedelta

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
    operating_days=None,
    propulsion_power_kw,
    cruise_hours_per_day,
    nominal_battery_kwh,
    usable_fraction,
    reserve_fraction,
    operation_start_hour_local=9.0,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    auxiliary_power_kw=0.0,
    auxiliary_operating_hours_per_day=0.0,
):
  """Simulate one vessel over every calendar day in the selected season."""
  if season_end < season_start:
    raise ValueError("season_end must not be before season_start")

  season_days = (season_end - season_start).days + 1

  if operating_days is None:
    operating_days = season_days

  if not isinstance(operating_days, int):
    raise ValueError("operating_days must be an integer")
  if operating_days < 1:
    raise ValueError("operating_days must be at least 1")
  if operating_days > season_days:
    raise ValueError("operating_days must not exceed season duration")

  # Select exactly operating_days calendar days, spread as evenly as
  # possible across the season.  Full-season operation therefore
  # preserves the historical behaviour exactly.
  if operating_days == season_days:
    operating_day_offsets = set(range(season_days))
  elif operating_days == 1:
    operating_day_offsets = {0}
  else:
    operating_day_offsets = {
        round(i * (season_days - 1) / (operating_days - 1))
        for i in range(operating_days)
    }

  if len(operating_day_offsets) != operating_days:
    raise RuntimeError("failed to construct deterministic operating-day schedule")

  if installed_pv_kwp < 0 or propulsion_power_kw < 0:
    raise ValueError("power values must be non-negative")
  if auxiliary_power_kw < 0:
    raise ValueError("auxiliary_power_kw must be non-negative")
  if cruise_hours_per_day <= 0 or cruise_hours_per_day > 24:
    raise ValueError("cruise_hours_per_day must be in (0, 24]")
  if not 0 <= auxiliary_operating_hours_per_day <= 24:
    raise ValueError("auxiliary_operating_hours_per_day must be in [0, 24]")
  if nominal_battery_kwh <= 0:
    raise ValueError("nominal_battery_kwh must be positive")
  if not 0 < usable_fraction <= 1:
    raise ValueError("usable_fraction must be in (0, 1]")
  if not 0 <= reserve_fraction < 1:
    raise ValueError("reserve_fraction must be in [0, 1)")
  if not 0 < charge_efficiency <= 1:
    raise ValueError("charge_efficiency must be in (0, 1]")
  if not 0 < discharge_efficiency <= 1:
    raise ValueError("discharge_efficiency must be in (0, 1]")

  max_soc = nominal_battery_kwh * usable_fraction
  min_soc = max_soc * reserve_fraction
  soc = max_soc

  season_propulsion = 0.0
  season_auxiliary = 0.0
  season_solar = 0.0
  direct_solar_propulsion = 0.0
  direct_solar_auxiliary = 0.0
  battery_discharge_propulsion = 0.0
  battery_discharge_auxiliary = 0.0
  battery_storage_withdrawal = 0.0
  battery_charge = 0.0
  solar_to_battery_input = 0.0
  curtailed_solar = 0.0
  shore_propulsion = 0.0
  shore_auxiliary = 0.0
  solar_only_hours = 0.0
  minimum_soc = soc

  def process_segment(
      *,
      duration_hours,
      solar_power_kw,
      propulsion_active,
      auxiliary_active,
  ):
    nonlocal soc
    nonlocal direct_solar_propulsion
    nonlocal direct_solar_auxiliary
    nonlocal battery_discharge_propulsion
    nonlocal battery_discharge_auxiliary
    nonlocal battery_storage_withdrawal
    nonlocal battery_charge
    nonlocal solar_to_battery_input
    nonlocal curtailed_solar
    nonlocal shore_propulsion
    nonlocal shore_auxiliary
    nonlocal minimum_soc

    if duration_hours <= 0:
      return

    solar_available_kwh = solar_power_kw * duration_hours
    propulsion_demand_kwh = (
        propulsion_power_kw * duration_hours
        if propulsion_active
        else 0.0
    )
    auxiliary_demand_kwh = (
        auxiliary_power_kw * duration_hours
        if auxiliary_active
        else 0.0
    )

    solar_to_propulsion_kwh = min(
        propulsion_demand_kwh,
        solar_available_kwh,
    )
    direct_solar_propulsion += solar_to_propulsion_kwh
    solar_available_kwh -= solar_to_propulsion_kwh

    solar_to_auxiliary_kwh = min(
        auxiliary_demand_kwh,
        solar_available_kwh,
    )
    direct_solar_auxiliary += solar_to_auxiliary_kwh
    solar_available_kwh -= solar_to_auxiliary_kwh

    propulsion_deficit_kwh = (
        propulsion_demand_kwh - solar_to_propulsion_kwh
    )
    auxiliary_deficit_kwh = (
        auxiliary_demand_kwh - solar_to_auxiliary_kwh
    )

    available_to_bus_kwh = max(
        0.0,
        (soc - min_soc) * discharge_efficiency,
    )

    battery_to_propulsion_kwh = min(
        propulsion_deficit_kwh,
        available_to_bus_kwh,
    )
    available_to_bus_kwh -= battery_to_propulsion_kwh

    battery_to_auxiliary_kwh = min(
        auxiliary_deficit_kwh,
        available_to_bus_kwh,
    )

    battery_to_loads_kwh = (
        battery_to_propulsion_kwh + battery_to_auxiliary_kwh
    )
    if battery_to_loads_kwh > 0:
      storage_withdrawal_kwh = (
          battery_to_loads_kwh / discharge_efficiency
      )
      soc -= storage_withdrawal_kwh
      battery_storage_withdrawal += storage_withdrawal_kwh

    battery_discharge_propulsion += battery_to_propulsion_kwh
    battery_discharge_auxiliary += battery_to_auxiliary_kwh

    shore_propulsion += max(
        0.0,
        propulsion_deficit_kwh - battery_to_propulsion_kwh,
    )
    shore_auxiliary += max(
        0.0,
        auxiliary_deficit_kwh - battery_to_auxiliary_kwh,
    )

    storage_room_kwh = max(0.0, max_soc - soc)
    storable_kwh = solar_available_kwh * charge_efficiency
    charged_kwh = min(storage_room_kwh, storable_kwh)
    soc += charged_kwh
    battery_charge += charged_kwh

    solar_used_for_charge_bus_kwh = (
        charged_kwh / charge_efficiency
        if charge_efficiency > 0
        else 0.0
    )
    solar_to_battery_input += solar_used_for_charge_bus_kwh
    curtailed_solar += max(
        0.0,
        solar_available_kwh - solar_used_for_charge_bus_kwh,
    )
    minimum_soc = min(minimum_soc, soc)

  current = season_start
  day_offset = 0
  while current <= season_end:
    is_operating_day = day_offset in operating_day_offsets

    for hour in range(24):
      specific_power = float(
          typical_hourly_specific_pv.get(
              (current.month, current.day, hour),
              0.0,
          )
      )
      solar_power_kw = installed_pv_kwp * max(0.0, specific_power)
      season_solar += solar_power_kw

      propulsion_active_hours = (
          _hour_overlap(
              operation_start_hour_local,
              cruise_hours_per_day,
              hour,
          )
          if is_operating_day
          else 0.0
      )
      auxiliary_active_hours = (
          _hour_overlap(
              operation_start_hour_local,
              auxiliary_operating_hours_per_day,
              hour,
          )
          if is_operating_day
          else 0.0
      )

      season_propulsion += (
          propulsion_power_kw * propulsion_active_hours
      )
      season_auxiliary += (
          auxiliary_power_kw * auxiliary_active_hours
      )

      if (
          propulsion_active_hours > 0
          and solar_power_kw >= propulsion_power_kw
      ):
        solar_only_hours += propulsion_active_hours

      both_active_hours = min(
          propulsion_active_hours,
          auxiliary_active_hours,
      )
      propulsion_only_hours = max(
          0.0,
          propulsion_active_hours - both_active_hours,
      )
      auxiliary_only_hours = max(
          0.0,
          auxiliary_active_hours - both_active_hours,
      )
      inactive_hours = max(
          0.0,
          1.0
          - both_active_hours
          - propulsion_only_hours
          - auxiliary_only_hours,
      )

      process_segment(
          duration_hours=both_active_hours,
          solar_power_kw=solar_power_kw,
          propulsion_active=True,
          auxiliary_active=True,
      )
      process_segment(
          duration_hours=propulsion_only_hours,
          solar_power_kw=solar_power_kw,
          propulsion_active=True,
          auxiliary_active=False,
      )
      process_segment(
          duration_hours=auxiliary_only_hours,
          solar_power_kw=solar_power_kw,
          propulsion_active=False,
          auxiliary_active=True,
      )
      process_segment(
          duration_hours=inactive_hours,
          solar_power_kw=solar_power_kw,
          propulsion_active=False,
          auxiliary_active=False,
      )

    current += timedelta(days=1)
    day_offset += 1

  shore_energy = shore_propulsion + shore_auxiliary

  return SeasonalVesselEnergyBalance(
      season_propulsion_kwh=season_propulsion,
      season_auxiliary_kwh=season_auxiliary,
      season_solar_generation_kwh=season_solar,
      solar_direct_to_propulsion_kwh=direct_solar_propulsion,
      solar_direct_to_auxiliary_kwh=direct_solar_auxiliary,
      battery_discharge_to_propulsion_kwh=battery_discharge_propulsion,
      battery_discharge_to_auxiliary_kwh=battery_discharge_auxiliary,
      battery_charge_from_solar_kwh=battery_charge,
      solar_to_battery_input_kwh=solar_to_battery_input,
      battery_storage_withdrawal_kwh=battery_storage_withdrawal,
      curtailed_solar_kwh=curtailed_solar,
      shore_to_propulsion_kwh=shore_propulsion,
      shore_to_auxiliary_kwh=shore_auxiliary,
      shore_energy_kwh=shore_energy,
      initial_soc_kwh=max_soc,
      final_soc_kwh=soc,
      minimum_soc_kwh=minimum_soc,
      solar_only_propulsion_hours=solar_only_hours,
      charge_efficiency=charge_efficiency,
      discharge_efficiency=discharge_efficiency,
  )
