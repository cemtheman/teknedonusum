"""Preliminary battery-only navigation energy and range calculations.

Battery capacity is nominal installed energy. The usable-energy fraction is the
normally usable share of nominal energy. The operational-reserve fraction is the
fraction of usable energy reserved rather than spent on the mission; it is not a
state-of-charge value.

Electrical demand comprises externally supplied motor electrical-input power plus
hotel/auxiliary load. Inverter/controller, battery-internal, cabling, and DC/DC
losses are not modeled separately. Thermal-management demand may be included in the
external hotel load. Transient manoeuvring loads are excluded. The model keeps
solar contribution excluded from range calculations, along with charging
efficiency and battery degradation.

At constant speed, one knot equals one nautical mile per hour, so electrical power
divided by speed gives energy per nautical mile.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationEnergyResult:
  speed_knots: float
  battery_capacity_kwh: float
  usable_energy_fraction: float
  operational_reserve_fraction: float
  usable_energy_kwh: float
  mission_energy_kwh: float
  propulsion_electrical_power_kw: float
  hotel_load_kw: float
  total_electrical_power_kw: float
  energy_per_nm_kwh: float
  endurance_hours: float
  navigation_range_nm: float


def calculate_navigation_energy(
    speed_knots: float,
    battery_capacity_kwh: float,
    propulsion_electrical_power_kw: float,
    hotel_load_kw: float,
    usable_energy_fraction: float,
    operational_reserve_fraction: float,
) -> NavigationEnergyResult:
  if not speed_knots > 0:
    raise ValueError("speed_knots must be positive")
  if not battery_capacity_kwh > 0:
    raise ValueError("battery_capacity_kwh must be positive")
  if not propulsion_electrical_power_kw >= 0:
    raise ValueError("propulsion_electrical_power_kw must be non-negative")
  if not hotel_load_kw >= 0:
    raise ValueError("hotel_load_kw must be non-negative")
  if not 0 < usable_energy_fraction <= 1:
    raise ValueError("usable_energy_fraction must be greater than zero and at most one")
  if not 0 <= operational_reserve_fraction < 1:
    raise ValueError(
        "operational_reserve_fraction must be non-negative and less than one"
    )

  total_electrical_power_kw = propulsion_electrical_power_kw + hotel_load_kw
  if not total_electrical_power_kw > 0:
    raise ValueError("total electrical power must be positive")

  usable_energy_kwh = battery_capacity_kwh * usable_energy_fraction
  mission_energy_kwh = usable_energy_kwh * (1.0 - operational_reserve_fraction)
  energy_per_nm_kwh = total_electrical_power_kw / speed_knots
  endurance_hours = mission_energy_kwh / total_electrical_power_kw
  navigation_range_nm = endurance_hours * speed_knots

  return NavigationEnergyResult(
      speed_knots=speed_knots,
      battery_capacity_kwh=battery_capacity_kwh,
      usable_energy_fraction=usable_energy_fraction,
      operational_reserve_fraction=operational_reserve_fraction,
      usable_energy_kwh=usable_energy_kwh,
      mission_energy_kwh=mission_energy_kwh,
      propulsion_electrical_power_kw=propulsion_electrical_power_kw,
      hotel_load_kw=hotel_load_kw,
      total_electrical_power_kw=total_electrical_power_kw,
      energy_per_nm_kwh=energy_per_nm_kwh,
      endurance_hours=endurance_hours,
      navigation_range_nm=navigation_range_nm,
  )
