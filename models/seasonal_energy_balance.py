"""Seasonal solar-assisted propulsion energy results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SeasonalVesselEnergyBalance:
  season_propulsion_kwh: float
  season_solar_generation_kwh: float
  solar_direct_to_propulsion_kwh: float
  battery_discharge_to_propulsion_kwh: float
  battery_charge_from_solar_kwh: float
  curtailed_solar_kwh: float
  shore_energy_kwh: float
  initial_soc_kwh: float
  final_soc_kwh: float
  minimum_soc_kwh: float
  solar_only_propulsion_hours: float

  @property
  def average_daily_propulsion_kwh(self):
    return self.season_propulsion_kwh

  @property
  def shore_dependency_ratio(self):
    if self.season_propulsion_kwh <= 0:
      return 0.0
    return self.shore_energy_kwh / self.season_propulsion_kwh
