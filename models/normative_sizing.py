"""Immutable traceable result for the complete normative sizing chain."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class NormativeSizingResult:
  vessel_id: str
  vessel_type: str
  selected_speed_knots: float
  profile_version: str
  assumption_status: str
  power_envelope_source_basis: str
  cost_baseline_status: str
  limitations: tuple[str, ...]
  min_installed_mechanical_power_kw: float
  reference_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float
  motor_efficiency: float
  min_electrical_input_power_kw: float
  reference_electrical_input_power_kw: float
  max_electrical_input_power_kw: float
  operating_hours_per_day: float
  duty_cycle: float
  effective_powered_hours_per_day: float
  min_daily_propulsion_energy_kwh: float
  reference_daily_propulsion_energy_kwh: float
  max_daily_propulsion_energy_kwh: float
  usable_energy_fraction: float
  reserve_fraction: float
  effective_usable_energy_fraction: float
  min_nominal_battery_capacity_kwh: float
  reference_nominal_battery_capacity_kwh: float
  max_nominal_battery_capacity_kwh: float
  currency: str
  motor_count: int
  motor_unit_cost_per_total_installed_kw: float
  motor_system_multiplier: float
  battery_unit_cost_per_nominal_kwh: float
  min_propulsion_system_cost: float
  reference_propulsion_system_cost: float
  max_propulsion_system_cost: float

  def __post_init__(self):
    for name in (
        "vessel_id",
        "vessel_type",
        "profile_version",
        "assumption_status",
        "power_envelope_source_basis",
        "cost_baseline_status",
        "currency",
    ):
      if not getattr(self, name):
        raise ValueError(f"{name} must not be empty")
    if not self.limitations or any(not item for item in self.limitations):
      raise ValueError("limitations must contain explicit non-empty entries")
    if not isinstance(self.motor_count, int) or self.motor_count <= 0:
      raise ValueError("motor_count must be a positive integer")

    scalar_values = (
        self.selected_speed_knots,
        self.motor_efficiency,
        self.operating_hours_per_day,
        self.duty_cycle,
        self.effective_powered_hours_per_day,
        self.usable_energy_fraction,
        self.reserve_fraction,
        self.effective_usable_energy_fraction,
        self.motor_unit_cost_per_total_installed_kw,
        self.motor_system_multiplier,
        self.battery_unit_cost_per_nominal_kwh,
    )
    if any(not isfinite(value) for value in scalar_values):
      raise ValueError("numeric sizing values must be finite")

    mechanical = (
        self.min_installed_mechanical_power_kw,
        self.reference_installed_mechanical_power_kw,
        self.max_installed_mechanical_power_kw,
    )
    electrical = (
        self.min_electrical_input_power_kw,
        self.reference_electrical_input_power_kw,
        self.max_electrical_input_power_kw,
    )
    energy = (
        self.min_daily_propulsion_energy_kwh,
        self.reference_daily_propulsion_energy_kwh,
        self.max_daily_propulsion_energy_kwh,
    )
    battery = (
        self.min_nominal_battery_capacity_kwh,
        self.reference_nominal_battery_capacity_kwh,
        self.max_nominal_battery_capacity_kwh,
    )
    cost = (
        self.min_propulsion_system_cost,
        self.reference_propulsion_system_cost,
        self.max_propulsion_system_cost,
    )
    groups = (mechanical, electrical, energy, battery, cost)
    if any(
        not isfinite(value) or value <= 0
        for group in groups
        for value in group
    ):
      raise ValueError("power, energy, battery, and cost values must be positive")
    if any(not group[0] <= group[1] <= group[2] for group in groups):
      raise ValueError("all sizing envelopes must be ordered")
    if any(
        electrical_value < mechanical_value
        for electrical_value, mechanical_value in zip(electrical, mechanical)
    ):
      raise ValueError("electrical input power must not be below mechanical power")
    if any(capacity < daily for capacity, daily in zip(battery, energy)):
      raise ValueError("nominal battery capacity must not be below daily energy")
