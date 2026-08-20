"""Standalone normative residual-resistance interpolation.

This module deliberately does not participate in the production power chain.
It supplies the v0.2 residual-resistance methodology for controlled evaluation
before a separate integration decision is made.
"""

from math import isfinite

from calculations.hydrodynamics import (
    calculate_froude_number,
    calculate_residual_resistance,
)
from models.residual_resistance import ResidualResistanceProfile


def interpolate_residual_resistance_coefficient(
    profile: ResidualResistanceProfile,
    froude_number: float,
) -> float:
  """Linearly interpolate C_R and reject extrapolation."""
  if not isinstance(profile, ResidualResistanceProfile):
    raise TypeError("profile must be a ResidualResistanceProfile")
  if not isfinite(froude_number) or froude_number < 0:
    raise ValueError("froude_number must be finite and non-negative")

  minimum = profile.anchors[0].froude_number
  maximum = profile.anchors[-1].froude_number
  if not minimum <= froude_number <= maximum:
    raise ValueError(
        f"froude_number must be within profile range [{minimum}, {maximum}]"
    )

  for anchor in profile.anchors:
    if froude_number == anchor.froude_number:
      return anchor.residual_resistance_coefficient

  for lower, upper in zip(profile.anchors, profile.anchors[1:]):
    if lower.froude_number < froude_number < upper.froude_number:
      position = (
          (froude_number - lower.froude_number)
          / (upper.froude_number - lower.froude_number)
      )
      return lower.residual_resistance_coefficient + position * (
          upper.residual_resistance_coefficient
          - lower.residual_resistance_coefficient
      )

  raise RuntimeError("profile interpolation interval was not found")


def calculate_profile_residual_resistance(
    profile: ResidualResistanceProfile,
    speed_knots: float,
    waterline_length_m: float,
    wetted_surface_area_m2: float,
) -> float:
  """Calculate residual force from a profile, guaranteeing zero at zero speed."""
  if speed_knots < 0:
    raise ValueError("speed_knots must be non-negative")
  if waterline_length_m <= 0:
    raise ValueError("waterline_length_m must be positive")
  if wetted_surface_area_m2 <= 0:
    raise ValueError("wetted_surface_area_m2 must be positive")
  if not isinstance(profile, ResidualResistanceProfile):
    raise TypeError("profile must be a ResidualResistanceProfile")
  if speed_knots == 0:
    return 0.0

  froude_number = calculate_froude_number(speed_knots, waterline_length_m)
  coefficient = interpolate_residual_resistance_coefficient(
      profile,
      froude_number,
  )
  return calculate_residual_resistance(
      coefficient,
      speed_knots,
      wetted_surface_area_m2,
  )
