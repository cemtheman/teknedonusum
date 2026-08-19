"""Preliminary calm-water hydrodynamic fundamentals for Köyceğiz–Dalyan vessel studies.

These are unrestricted calm water preliminary calculations. The resistance model
contains only the frictional component; it excludes wave/residual resistance,
appendages, shallow-water effects, and catamaran interference.
"""

import math


# Freshwater assumptions used by the preliminary hydrodynamic model.
WATER_DENSITY_KG_M3 = 1000.0
KINEMATIC_VISCOSITY_M2_S = 1.0e-6
GRAVITY_M_S2 = 9.80665
KNOT_TO_M_S = 0.514444


def knots_to_mps(speed_knots):
  if speed_knots < 0:
    raise ValueError("speed_knots must be non-negative")

  return speed_knots * KNOT_TO_M_S


def calculate_froude_number(speed_knots, waterline_length_m):
  if waterline_length_m <= 0:
    raise ValueError("waterline_length_m must be positive")

  speed_m_s = knots_to_mps(speed_knots)
  return speed_m_s / math.sqrt(GRAVITY_M_S2 * waterline_length_m)


def calculate_reynolds_number(
    speed_knots,
    waterline_length_m,
    kinematic_viscosity_m2_s=KINEMATIC_VISCOSITY_M2_S,
):
  if waterline_length_m <= 0:
    raise ValueError("waterline_length_m must be positive")
  if kinematic_viscosity_m2_s <= 0:
    raise ValueError("kinematic_viscosity_m2_s must be positive")

  speed_m_s = knots_to_mps(speed_knots)
  return speed_m_s * waterline_length_m / kinematic_viscosity_m2_s


def calculate_ittc_friction_coefficient(reynolds_number):
  if reynolds_number <= 0:
    raise ValueError("reynolds_number must be positive")

  return 0.075 / (math.log10(reynolds_number) - 2.0) ** 2


def calculate_frictional_resistance(
    speed_knots,
    waterline_length_m,
    wetted_surface_area_m2,
    water_density_kg_m3=WATER_DENSITY_KG_M3,
    kinematic_viscosity_m2_s=KINEMATIC_VISCOSITY_M2_S,
):
  if speed_knots < 0:
    raise ValueError("speed_knots must be non-negative")
  if waterline_length_m <= 0:
    raise ValueError("waterline_length_m must be positive")
  if wetted_surface_area_m2 <= 0:
    raise ValueError("wetted_surface_area_m2 must be positive")
  if water_density_kg_m3 <= 0:
    raise ValueError("water_density_kg_m3 must be positive")
  if kinematic_viscosity_m2_s <= 0:
    raise ValueError("kinematic_viscosity_m2_s must be positive")
  if speed_knots == 0:
    return 0.0

  speed_m_s = knots_to_mps(speed_knots)
  reynolds_number = calculate_reynolds_number(
      speed_knots,
      waterline_length_m,
      kinematic_viscosity_m2_s,
  )
  friction_coefficient = calculate_ittc_friction_coefficient(reynolds_number)
  return (
      0.5
      * water_density_kg_m3
      * speed_m_s**2
      * wetted_surface_area_m2
      * friction_coefficient
  )
