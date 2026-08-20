"""Immutable export-ready contract for normative vessel comparison."""

from dataclasses import dataclass
from math import isfinite


EXPECTED_NORMATIVE_VESSEL_IDS = ("v1", "v2", "v3")


@dataclass(frozen=True)
class NormativeComparisonAssumptionSnapshot:
  motor_efficiency: float
  operating_hours_per_day: float
  duty_cycle: float
  effective_powered_hours_per_day: float
  usable_energy_fraction: float
  reserve_fraction: float
  motor_unit_cost_per_total_installed_kw: float
  battery_unit_cost_per_nominal_kwh: float

  def __post_init__(self):
    fractions = (
        self.motor_efficiency,
        self.duty_cycle,
        self.usable_energy_fraction,
    )
    if any(not isfinite(value) or not 0 < value <= 1 for value in fractions):
      raise ValueError("common assumption fractions must be within zero and one")
    if not isfinite(self.reserve_fraction) or not 0 <= self.reserve_fraction < 1:
      raise ValueError("reserve_fraction must be finite and within zero and one")
    positive = (
        self.operating_hours_per_day,
        self.effective_powered_hours_per_day,
        self.motor_unit_cost_per_total_installed_kw,
        self.battery_unit_cost_per_nominal_kwh,
    )
    if any(not isfinite(value) or value <= 0 for value in positive):
      raise ValueError("common assumption values must be finite and positive")
    if self.effective_powered_hours_per_day > self.operating_hours_per_day:
      raise ValueError("effective powered hours cannot exceed operating hours")


@dataclass(frozen=True)
class NormativeVesselComparisonRow:
  vessel_id: str
  vessel_type: str
  passenger_capacity: int
  selected_speed_knots: float
  profile_version: str
  methodology_status: str
  validation_status: str
  intended_use: str
  preliminary_only: bool
  externally_validated: bool
  twin_motor_configuration: bool
  motor_system_multiplier: float
  min_installed_mechanical_power_kw: float
  reference_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float
  min_daily_propulsion_energy_kwh: float
  reference_daily_propulsion_energy_kwh: float
  max_daily_propulsion_energy_kwh: float
  min_nominal_battery_capacity_kwh: float
  reference_nominal_battery_capacity_kwh: float
  max_nominal_battery_capacity_kwh: float
  currency: str
  min_propulsion_system_cost: float
  reference_propulsion_system_cost: float
  max_propulsion_system_cost: float
  assumptions: NormativeComparisonAssumptionSnapshot

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
    if self.passenger_capacity <= 0:
      raise ValueError("passenger_capacity must be positive")
    if not isfinite(self.selected_speed_knots) or not (
        6.0 <= self.selected_speed_knots <= 10.0
    ):
      raise ValueError("selected_speed_knots must be within 6–10 knots")
    if self.preliminary_only is not True:
      raise ValueError("comparison rows must remain preliminary")
    if self.externally_validated is not False:
      raise ValueError("comparison rows are not externally validated")

    groups = (
        (
            self.min_installed_mechanical_power_kw,
            self.reference_installed_mechanical_power_kw,
            self.max_installed_mechanical_power_kw,
        ),
        (
            self.min_daily_propulsion_energy_kwh,
            self.reference_daily_propulsion_energy_kwh,
            self.max_daily_propulsion_energy_kwh,
        ),
        (
            self.min_nominal_battery_capacity_kwh,
            self.reference_nominal_battery_capacity_kwh,
            self.max_nominal_battery_capacity_kwh,
        ),
        (
            self.min_propulsion_system_cost,
            self.reference_propulsion_system_cost,
            self.max_propulsion_system_cost,
        ),
    )
    numeric = (
        self.selected_speed_knots,
        self.motor_system_multiplier,
        *(value for group in groups for value in group),
    )
    if any(not isfinite(value) or value <= 0 for value in numeric):
      raise ValueError("comparison row numeric values must be finite and positive")
    if any(not group[0] <= group[1] <= group[2] for group in groups):
      raise ValueError("comparison row envelopes must be ordered")


@dataclass(frozen=True)
class NormativeVesselComparisonResult:
  selected_speed_knots: float
  currency: str
  assumptions: NormativeComparisonAssumptionSnapshot
  rows: tuple[NormativeVesselComparisonRow, ...]

  def __post_init__(self):
    if not isfinite(self.selected_speed_knots) or not (
        6.0 <= self.selected_speed_knots <= 10.0
    ):
      raise ValueError("selected_speed_knots must be within 6–10 knots")
    if not self.currency:
      raise ValueError("currency must not be empty")
    ids = tuple(row.vessel_id for row in self.rows)
    if ids != EXPECTED_NORMATIVE_VESSEL_IDS:
      raise ValueError("rows must contain ordered, unique v1, v2, and v3 coverage")
    if any(row.selected_speed_knots != self.selected_speed_knots for row in self.rows):
      raise ValueError("all rows must use the selected comparison speed")
    if any(row.currency != self.currency for row in self.rows):
      raise ValueError("all rows must use the comparison currency")
    if any(row.assumptions != self.assumptions for row in self.rows):
      raise ValueError("all rows must use common normative assumptions")
