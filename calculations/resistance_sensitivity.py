"""Preliminary resistance sensitivity and calibration-support calculations.

This module evaluates supplied scenarios; it is not a verified resistance
prediction. Residual resistance is an external calibrated input and is not
estimated, interpolated, or derived from Froude number here. Effective power is
not shaft power, electrical input power, or an installed motor rating.
"""

from dataclasses import dataclass

from calculations.hydrodynamics import (
    calculate_effective_power_kw,
    calculate_frictional_resistance,
    calculate_froude_number,
    calculate_total_resistance,
    calculate_viscous_resistance,
)
from models.geometry import PreliminaryVesselGeometry


@dataclass(frozen=True)
class ResistanceSensitivityResult:
  speed_knots: float
  froude_number: float
  frictional_resistance_n: float
  form_factor: float
  viscous_resistance_n: float
  residual_resistance_n: float
  appendage_resistance_n: float
  total_resistance_n: float
  effective_power_kw: float


def calculate_resistance_sensitivity(
    geometry: PreliminaryVesselGeometry,
    speed_knots: float,
    form_factor: float,
    residual_resistance_n: float,
    appendage_resistance_n: float = 0.0,
) -> ResistanceSensitivityResult:
  if not isinstance(geometry, PreliminaryVesselGeometry):
    raise TypeError("geometry must be a PreliminaryVesselGeometry")

  waterline_length_m = geometry.lwl_m.value
  wetted_surface_area_m2 = geometry.wetted_surface_area_m2.value

  froude_number = calculate_froude_number(speed_knots, waterline_length_m)
  frictional_resistance_n = calculate_frictional_resistance(
      speed_knots,
      waterline_length_m,
      wetted_surface_area_m2,
  )
  viscous_resistance_n = calculate_viscous_resistance(
      speed_knots,
      waterline_length_m,
      wetted_surface_area_m2,
      form_factor,
  )
  total_resistance_n = calculate_total_resistance(
      viscous_resistance_n,
      residual_resistance_n,
      appendage_resistance_n,
  )
  effective_power_kw = calculate_effective_power_kw(
      total_resistance_n,
      speed_knots,
  )

  return ResistanceSensitivityResult(
      speed_knots=speed_knots,
      froude_number=froude_number,
      frictional_resistance_n=frictional_resistance_n,
      form_factor=form_factor,
      viscous_resistance_n=viscous_resistance_n,
      residual_resistance_n=residual_resistance_n,
      appendage_resistance_n=appendage_resistance_n,
      total_resistance_n=total_resistance_n,
      effective_power_kw=effective_power_kw,
  )
