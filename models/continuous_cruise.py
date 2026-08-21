"""Transparent continuous-cruise resistance and power result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ContinuousCruisePowerResult:
  speed_knots: float
  froude_number: float
  reynolds_number: float
  frictional_resistance_n: float
  viscous_resistance_n: float
  residual_resistance_n: float
  appendage_resistance_n: float
  total_resistance_n: float
  effective_power_kw: float
  shaft_power_kw: float
  electrical_input_power_kw: float
  propulsive_efficiency: float
  motor_efficiency: float

  def __post_init__(self):
    positive = (
        self.speed_knots,
        self.reynolds_number,
        self.propulsive_efficiency,
        self.motor_efficiency,
    )
    if any(not isfinite(value) or value <= 0 for value in positive):
      raise ValueError("continuous-cruise positive values must be finite and positive")

    non_negative = (
        self.froude_number,
        self.frictional_resistance_n,
        self.viscous_resistance_n,
        self.residual_resistance_n,
        self.appendage_resistance_n,
        self.total_resistance_n,
        self.effective_power_kw,
        self.shaft_power_kw,
        self.electrical_input_power_kw,
    )
    if any(not isfinite(value) or value < 0 for value in non_negative):
      raise ValueError(
          "continuous-cruise resistance and power values must be finite "
          "and non-negative"
      )


@dataclass(frozen=True)
class SolarOnlyObservationBound:
  installed_pv_kwp: float
  specific_pv_power_kw_per_kwp: float
  observed_solar_available_kw: float
  maximum_electrical_propulsion_power_kw: float
