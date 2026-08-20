"""Immutable cruise-power result for normative preliminary sizing."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class CruisePowerEnvelopeResult:
  vessel_id: str
  speed_knots: float
  speed_power_exponent: float
  min_cruise_mechanical_power_kw: float
  reference_cruise_mechanical_power_kw: float
  max_cruise_mechanical_power_kw: float
  motor_efficiency: float
  min_cruise_electrical_power_kw: float
  reference_cruise_electrical_power_kw: float
  max_cruise_electrical_power_kw: float

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")
    if not isfinite(self.speed_knots) or self.speed_knots <= 0:
      raise ValueError("speed_knots must be finite and positive")
    if not isfinite(self.speed_power_exponent) or self.speed_power_exponent <= 0:
      raise ValueError("speed_power_exponent must be finite and positive")
    if not isfinite(self.motor_efficiency) or not 0 < self.motor_efficiency <= 1:
      raise ValueError(
          "motor_efficiency must be finite, positive, and at most one"
      )

    mechanical = (
        self.min_cruise_mechanical_power_kw,
        self.reference_cruise_mechanical_power_kw,
        self.max_cruise_mechanical_power_kw,
    )
    electrical = (
        self.min_cruise_electrical_power_kw,
        self.reference_cruise_electrical_power_kw,
        self.max_cruise_electrical_power_kw,
    )

    if any(
        not isfinite(value) or value <= 0
        for value in mechanical + electrical
    ):
      raise ValueError("cruise power values must be finite and positive")

    if not mechanical[0] <= mechanical[1] <= mechanical[2]:
      raise ValueError("cruise mechanical power values must be ordered")
    if not electrical[0] <= electrical[1] <= electrical[2]:
      raise ValueError("cruise electrical power values must be ordered")