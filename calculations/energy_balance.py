"""Preliminary daily electrical-energy balance using aggregate daily totals.

Solar generation timing is not matched to demand timing. Solar energy used is only
a daily energy-accounting quantity. The model does not resolve a battery buffer,
simultaneous generation and use, midday excess timing, charging acceptance,
curtailment timing, or an hourly profile. Net external energy required is the part
of daily demand not covered by solar; no source or storage mechanism is assigned.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyEnergyBalanceResult:
  operating_hours: float
  propulsion_electrical_power_kw: float
  hotel_load_kw: float
  propulsion_energy_kwh: float
  hotel_energy_kwh: float
  gross_daily_demand_kwh: float
  daily_solar_energy_kwh: float
  solar_energy_used_kwh: float
  excess_solar_energy_kwh: float
  net_external_energy_required_kwh: float
  solar_coverage_ratio: float


def calculate_daily_energy_balance(
    operating_hours: float,
    propulsion_electrical_power_kw: float,
    hotel_load_kw: float,
    daily_solar_energy_kwh: float,
) -> DailyEnergyBalanceResult:
  if not operating_hours >= 0:
    raise ValueError("operating_hours must be non-negative")
  if not propulsion_electrical_power_kw >= 0:
    raise ValueError("propulsion_electrical_power_kw must be non-negative")
  if not hotel_load_kw >= 0:
    raise ValueError("hotel_load_kw must be non-negative")
  if not daily_solar_energy_kwh >= 0:
    raise ValueError("daily_solar_energy_kwh must be non-negative")

  propulsion_energy_kwh = propulsion_electrical_power_kw * operating_hours
  hotel_energy_kwh = hotel_load_kw * operating_hours
  gross_daily_demand_kwh = propulsion_energy_kwh + hotel_energy_kwh
  solar_energy_used_kwh = min(daily_solar_energy_kwh, gross_daily_demand_kwh)
  excess_solar_energy_kwh = max(
      daily_solar_energy_kwh - gross_daily_demand_kwh,
      0.0,
  )
  net_external_energy_required_kwh = max(
      gross_daily_demand_kwh - daily_solar_energy_kwh,
      0.0,
  )
  solar_coverage_ratio = (
      solar_energy_used_kwh / gross_daily_demand_kwh
      if gross_daily_demand_kwh > 0
      else 0.0
  )

  return DailyEnergyBalanceResult(
      operating_hours=operating_hours,
      propulsion_electrical_power_kw=propulsion_electrical_power_kw,
      hotel_load_kw=hotel_load_kw,
      propulsion_energy_kwh=propulsion_energy_kwh,
      hotel_energy_kwh=hotel_energy_kwh,
      gross_daily_demand_kwh=gross_daily_demand_kwh,
      daily_solar_energy_kwh=daily_solar_energy_kwh,
      solar_energy_used_kwh=solar_energy_used_kwh,
      excess_solar_energy_kwh=excess_solar_energy_kwh,
      net_external_energy_required_kwh=net_external_energy_required_kwh,
      solar_coverage_ratio=solar_coverage_ratio,
  )
