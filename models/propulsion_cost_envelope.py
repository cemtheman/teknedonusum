"""Immutable preliminary propulsion-system cost envelope result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PropulsionSystemCostEnvelopeResult:
  vessel_id: str
  speed_knots: float
  currency: str
  min_installed_mechanical_power_kw: float
  reference_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float
  min_nominal_battery_capacity_kwh: float
  reference_nominal_battery_capacity_kwh: float
  max_nominal_battery_capacity_kwh: float
  motor_count: int
  motor_cost_per_total_installed_kw: float
  motor_system_multiplier: float
  battery_cost_per_nominal_kwh: float
  cost_basis_provenance: str
  min_motor_system_cost: float
  reference_motor_system_cost: float
  max_motor_system_cost: float
  min_battery_system_cost: float
  reference_battery_system_cost: float
  max_battery_system_cost: float
  min_total_propulsion_system_cost: float
  reference_total_propulsion_system_cost: float
  max_total_propulsion_system_cost: float

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")
    if not self.currency:
      raise ValueError("currency must not be empty")
    if not self.cost_basis_provenance:
      raise ValueError("cost_basis_provenance must not be empty")
    if not isfinite(self.speed_knots) or self.speed_knots < 0:
      raise ValueError("speed_knots must be finite and non-negative")
    if not isinstance(self.motor_count, int) or self.motor_count <= 0:
      raise ValueError("motor_count must be a positive integer")

    unit_costs = (
        self.motor_cost_per_total_installed_kw,
        self.motor_system_multiplier,
        self.battery_cost_per_nominal_kwh,
    )
    if any(not isfinite(value) or value <= 0 for value in unit_costs):
      raise ValueError("unit costs and multipliers must be finite and positive")

    power = (
        self.min_installed_mechanical_power_kw,
        self.reference_installed_mechanical_power_kw,
        self.max_installed_mechanical_power_kw,
    )
    battery = (
        self.min_nominal_battery_capacity_kwh,
        self.reference_nominal_battery_capacity_kwh,
        self.max_nominal_battery_capacity_kwh,
    )
    motor_cost = (
        self.min_motor_system_cost,
        self.reference_motor_system_cost,
        self.max_motor_system_cost,
    )
    battery_cost = (
        self.min_battery_system_cost,
        self.reference_battery_system_cost,
        self.max_battery_system_cost,
    )
    total_cost = (
        self.min_total_propulsion_system_cost,
        self.reference_total_propulsion_system_cost,
        self.max_total_propulsion_system_cost,
    )
    groups = (power, battery, motor_cost, battery_cost, total_cost)
    if any(
        not isfinite(value) or value <= 0
        for group in groups
        for value in group
    ):
      raise ValueError("power, capacity, and cost values must be finite and positive")
    if any(not group[0] <= group[1] <= group[2] for group in groups):
      raise ValueError("power, capacity, and cost values must be ordered")
