from dataclasses import dataclass


@dataclass(frozen=True)
class CommissionTechnicalConstraints:
  minimum_loa_m: float
  maximum_loa_m: float
  allowed_passenger_capacities: tuple[int, ...]
  minimum_required_speed_knots: float
  minimum_navigation_range_nm: float
  minimum_motor_efficiency: float
  minimum_battery_capacity_kwh: float
  minimum_roof_length_fraction_of_loa: float

  def __post_init__(self):
    if not self.minimum_loa_m > 0:
      raise ValueError("minimum_loa_m must be positive")
    if not self.maximum_loa_m >= self.minimum_loa_m:
      raise ValueError("maximum_loa_m must not be less than minimum_loa_m")
    if not self.allowed_passenger_capacities:
      raise ValueError("allowed_passenger_capacities must not be empty")
    if any(capacity <= 0 for capacity in self.allowed_passenger_capacities):
      raise ValueError("allowed passenger capacities must be positive")
    if not self.minimum_required_speed_knots > 0:
      raise ValueError("minimum_required_speed_knots must be positive")
    if not self.minimum_navigation_range_nm > 0:
      raise ValueError("minimum_navigation_range_nm must be positive")
    if not 0 < self.minimum_motor_efficiency <= 1:
      raise ValueError("minimum_motor_efficiency must be greater than zero and at most one")
    if not self.minimum_battery_capacity_kwh > 0:
      raise ValueError("minimum_battery_capacity_kwh must be positive")
    if not 0 < self.minimum_roof_length_fraction_of_loa <= 1:
      raise ValueError(
          "minimum_roof_length_fraction_of_loa must be greater than zero and at most one"
      )
