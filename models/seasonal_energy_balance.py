"""Seasonal solar-assisted propulsion and auxiliary energy results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SeasonalVesselEnergyBalance:
  season_propulsion_kwh: float
  season_auxiliary_kwh: float
  season_solar_generation_kwh: float
  solar_direct_to_propulsion_kwh: float
  solar_direct_to_auxiliary_kwh: float
  battery_discharge_to_propulsion_kwh: float
  battery_discharge_to_auxiliary_kwh: float
  battery_charge_from_solar_kwh: float
  solar_to_battery_input_kwh: float
  battery_storage_withdrawal_kwh: float
  curtailed_solar_kwh: float
  shore_to_propulsion_kwh: float
  shore_to_auxiliary_kwh: float
  shore_energy_kwh: float
  initial_soc_kwh: float
  final_soc_kwh: float
  minimum_soc_kwh: float
  solar_only_propulsion_hours: float
  charge_efficiency: float
  discharge_efficiency: float

  @property
  def average_daily_propulsion_kwh(self):
    return self.season_propulsion_kwh

  @property
  def season_total_demand_kwh(self):
    return self.season_propulsion_kwh + self.season_auxiliary_kwh

  @property
  def shore_dependency_ratio(self):
    if self.season_total_demand_kwh <= 0:
      return 0.0
    return self.shore_energy_kwh / self.season_total_demand_kwh

  @property
  def charge_conversion_loss_kwh(self):
    return self.solar_to_battery_input_kwh - self.battery_charge_from_solar_kwh

  @property
  def discharge_conversion_loss_kwh(self):
    return (
        self.battery_storage_withdrawal_kwh
        - self.battery_discharge_to_propulsion_kwh
        - self.battery_discharge_to_auxiliary_kwh
    )

  @property
  def terminal_soc_deficit_kwh(self):
    return max(0.0, self.initial_soc_kwh - self.final_soc_kwh)

  @property
  def terminal_soc_recovery_shore_kwh(self):
    return self.terminal_soc_deficit_kwh / self.charge_efficiency

  @property
  def normalized_shore_energy_kwh(self):
    return self.shore_energy_kwh + self.terminal_soc_recovery_shore_kwh

  @property
  def pv_balance_error_kwh(self):
    return (
        self.season_solar_generation_kwh
        - self.solar_direct_to_propulsion_kwh
        - self.solar_direct_to_auxiliary_kwh
        - self.solar_to_battery_input_kwh
        - self.curtailed_solar_kwh
    )

  @property
  def propulsion_balance_error_kwh(self):
    return (
        self.season_propulsion_kwh
        - self.solar_direct_to_propulsion_kwh
        - self.battery_discharge_to_propulsion_kwh
        - self.shore_to_propulsion_kwh
    )

  @property
  def auxiliary_balance_error_kwh(self):
    return (
        self.season_auxiliary_kwh
        - self.solar_direct_to_auxiliary_kwh
        - self.battery_discharge_to_auxiliary_kwh
        - self.shore_to_auxiliary_kwh
    )

  @property
  def battery_balance_error_kwh(self):
    expected_delta = (
        self.battery_charge_from_solar_kwh
        - self.battery_storage_withdrawal_kwh
    )
    actual_delta = self.final_soc_kwh - self.initial_soc_kwh
    return actual_delta - expected_delta
