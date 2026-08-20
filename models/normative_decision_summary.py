"""Immutable user-facing data contract for normative sizing decisions."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class NormativeDecisionAssumptionSnapshot:
  motor_efficiency: float
  operating_hours_per_day: float
  duty_cycle: float
  effective_powered_hours_per_day: float
  usable_energy_fraction: float
  reserve_fraction: float
  motor_unit_cost_per_total_installed_kw: float
  battery_unit_cost_per_nominal_kwh: float
  motor_system_multiplier: float


@dataclass(frozen=True)
class NormativeDecisionSummary:
  vessel_id: str
  vessel_type: str
  selected_speed_knots: float
  profile_version: str
  methodology_status: str
  validation_status: str
  intended_use: str
  preliminary_only: bool
  externally_validated: bool
  twin_motor_configuration: bool
  min_envelope_installed_mechanical_power_kw: float
  reference_estimate_installed_mechanical_power_kw: float
  max_envelope_installed_mechanical_power_kw: float
  reference_electrical_input_power_kw: float
  min_envelope_daily_propulsion_energy_kwh: float
  reference_estimate_daily_propulsion_energy_kwh: float
  max_envelope_daily_propulsion_energy_kwh: float
  min_envelope_nominal_battery_capacity_kwh: float
  reference_estimate_nominal_battery_capacity_kwh: float
  max_envelope_nominal_battery_capacity_kwh: float
  currency: str
  min_envelope_propulsion_system_cost: float
  reference_estimate_propulsion_system_cost: float
  max_envelope_propulsion_system_cost: float
  assumptions: NormativeDecisionAssumptionSnapshot
  limitation_ids: tuple[str, ...]

  def __post_init__(self):
    for name in (
        "vessel_id",
        "vessel_type",
        "profile_version",
        "methodology_status",
        "validation_status",
        "intended_use",
        "currency",
    ):
      if not getattr(self, name):
        raise ValueError(f"{name} must not be empty")
    if self.preliminary_only is not True:
      raise ValueError("normative decision summaries must remain preliminary")
    if self.externally_validated is not False:
      raise ValueError("normative decision summaries are not externally validated")
    if not self.limitation_ids or any(not item for item in self.limitation_ids):
      raise ValueError("limitation_ids must contain explicit entries")

    power = (
        self.min_envelope_installed_mechanical_power_kw,
        self.reference_estimate_installed_mechanical_power_kw,
        self.max_envelope_installed_mechanical_power_kw,
    )
    energy = (
        self.min_envelope_daily_propulsion_energy_kwh,
        self.reference_estimate_daily_propulsion_energy_kwh,
        self.max_envelope_daily_propulsion_energy_kwh,
    )
    battery = (
        self.min_envelope_nominal_battery_capacity_kwh,
        self.reference_estimate_nominal_battery_capacity_kwh,
        self.max_envelope_nominal_battery_capacity_kwh,
    )
    cost = (
        self.min_envelope_propulsion_system_cost,
        self.reference_estimate_propulsion_system_cost,
        self.max_envelope_propulsion_system_cost,
    )
    numeric = (
        self.selected_speed_knots,
        self.reference_electrical_input_power_kw,
        *power,
        *energy,
        *battery,
        *cost,
    )
    if any(not isfinite(value) or value <= 0 for value in numeric):
      raise ValueError("decision summary numeric values must be finite and positive")
    if any(
        not group[0] <= group[1] <= group[2]
        for group in (power, energy, battery, cost)
    ):
      raise ValueError("decision summary envelopes must be ordered")
