"""Immutable inputs for normative residual-resistance profiles."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ResidualResistanceAnchor:
  froude_number: float
  residual_resistance_coefficient: float

  def __post_init__(self):
    if not isfinite(self.froude_number) or self.froude_number < 0:
      raise ValueError("froude_number must be finite and non-negative")
    if (
        not isfinite(self.residual_resistance_coefficient)
        or self.residual_resistance_coefficient < 0
    ):
      raise ValueError(
          "residual_resistance_coefficient must be finite and non-negative"
      )


@dataclass(frozen=True)
class ResidualResistanceProfile:
  vessel_id: str
  description: str
  anchors: tuple[ResidualResistanceAnchor, ...]

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")
    if not self.description:
      raise ValueError("description must not be empty")
    if len(self.anchors) < 2:
      raise ValueError("anchors must contain at least two points")

    froude_numbers = tuple(anchor.froude_number for anchor in self.anchors)
    if any(
        current <= previous
        for previous, current in zip(froude_numbers, froude_numbers[1:])
    ):
      raise ValueError("anchor Froude numbers must be strictly increasing")
