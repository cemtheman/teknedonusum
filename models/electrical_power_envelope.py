"""Immutable mechanical-to-electrical power-envelope conversion result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ElectricalInputPowerEnvelopeResult:
  speed_knots: float
  min_installed_mechanical_power_kw: float
  reference_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float
  motor_efficiency: float
  min_electrical_input_power_kw: float
  reference_electrical_input_power_kw: float
  max_electrical_input_power_kw: float

  def __post_init__(self):
    if not isfinite(self.speed_knots) or self.speed_knots < 0:
      raise ValueError("speed_knots must be finite and non-negative")
    if not isfinite(self.motor_efficiency) or not 0 < self.motor_efficiency <= 1:
      raise ValueError("motor_efficiency must be finite, positive, and at most one")

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
    if any(not isfinite(value) or value < 0 for value in mechanical + electrical):
      raise ValueError("power values must be finite and non-negative")
    if not mechanical[0] <= mechanical[1] <= mechanical[2]:
      raise ValueError("mechanical power values must be ordered")
    if not electrical[0] <= electrical[1] <= electrical[2]:
      raise ValueError("electrical power values must be ordered")
