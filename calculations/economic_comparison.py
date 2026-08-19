"""Structured v1/v2/v3 economic comparison using existing calculations.

This module only assembles the existing calibrated vessel-physics and vessel
economics results. It does not introduce or duplicate engineering or economic
formulas.
"""

from dataclasses import dataclass
from math import isfinite

from calculations.economics import calculate_vessel_economics
from calculations.vessel_physics import calc_calibrated_vessel_physics


@dataclass(frozen=True)
class VesselEconomicComparisonRow:
  vessel_id: str
  vessel_name: str
  investment_cost_tl: float
  grant_amount_tl: float
  net_investment_tl: float
  daily_electrical_energy_requirement_kwh: float
  annual_electrical_energy_requirement_kwh: float
  annual_electricity_cost_tl: float
  diesel_baseline_annual_fuel_cost_tl: float
  annual_operating_saving_tl: float
  simple_payback_seasons: float | None
  annual_co2_reduction_t: float


def build_vessel_economic_comparison(
    vessel_specs,
    cruise_speed: float,
    daily_miles: float,
    sun_hours: float,
    season_days: int,
    electricity_price: float,
    diesel_price: float,
    exchange_rate: float,
) -> tuple[VesselEconomicComparisonRow, ...]:
  """Build economic rows exclusively from existing physics/economics APIs."""
  vessel_ids = ("v1", "v2", "v3")
  if any(vessel_id not in vessel_specs for vessel_id in vessel_ids):
    raise ValueError("vessel_specs must contain v1, v2, and v3")

  rows = []
  for vessel_id in vessel_ids:
    spec = vessel_specs[vessel_id]
    physics = calc_calibrated_vessel_physics(
        spec,
        cruise_spd=cruise_speed,
        d_miles=daily_miles,
        s_hours=sun_hours,
    )
    economics = calculate_vessel_economics(
        spec,
        physics,
        eur_rate=exchange_rate,
        diesel_price=diesel_price,
        elec_price=electricity_price,
        operating_days=season_days,
    )

    rows.append(
        VesselEconomicComparisonRow(
            vessel_id=vessel_id,
            vessel_name=spec["name"],
            investment_cost_tl=economics.total_investment,
            grant_amount_tl=economics.grant_amount,
            net_investment_tl=economics.net_capex,
            daily_electrical_energy_requirement_kwh=physics.net_grid_kwh,
            annual_electrical_energy_requirement_kwh=(
                economics.grid_electricity_consumption
            ),
            annual_electricity_cost_tl=economics.new_elec_cost,
            diesel_baseline_annual_fuel_cost_tl=economics.old_diesel_cost,
            annual_operating_saving_tl=economics.net_savings,
            simple_payback_seasons=(
                economics.payback_seasons
                if isfinite(economics.payback_seasons)
                else None
            ),
            annual_co2_reduction_t=economics.net_co2,
        )
    )

  return tuple(rows)
