"""Preliminary calm-water hydrodynamic fundamentals for Köyceğiz–Dalyan vessel studies.

This preliminary unrestricted calm-water framework calculates ITTC-1957-based
frictional resistance, form-factor-corrected friction as viscous resistance, and
total resistance. Residual resistance is an externally supplied/calibrated input,
and appendage resistance is an externally supplied input. Total resistance is the
sum of the viscous, residual, and appendage components.

The framework does not include empirical wave/residual prediction, shallow-water
correction, channel-bank effects, catamaran interference, propeller/shaft
efficiency, or installed motor power prediction.
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


def calculate_viscous_resistance(
    speed_knots,
    waterline_length_m,
    wetted_surface_area_m2,
    form_factor,
    water_density_kg_m3=WATER_DENSITY_KG_M3,
    kinematic_viscosity_m2_s=KINEMATIC_VISCOSITY_M2_S,
):
  # Required user/calibration input; not a commission-defined default value.
  if form_factor < 0:
    raise ValueError("form_factor must be non-negative")

  frictional_resistance_n = calculate_frictional_resistance(
      speed_knots,
      waterline_length_m,
      wetted_surface_area_m2,
      water_density_kg_m3,
      kinematic_viscosity_m2_s,
  )
  return (1.0 + form_factor) * frictional_resistance_n


def calculate_residual_resistance_coefficient(
    residual_resistance_n,
    speed_knots,
    wetted_surface_area_m2,
    water_density_kg_m3=WATER_DENSITY_KG_M3,
):
  """Represent a supplied residual-resistance force as a coefficient.

  This conversion utility uses wetted surface as its reference area. It does not
  predict C_R from Froude number and does not implement Holtrop, Delft,
  model-test interpolation, CFD fitting, or any empirical wave/residual model.
  """
  if residual_resistance_n < 0:
    raise ValueError("residual_resistance_n must be non-negative")
  if speed_knots <= 0:
    raise ValueError("speed_knots must be positive")
  if wetted_surface_area_m2 <= 0:
    raise ValueError("wetted_surface_area_m2 must be positive")
  if water_density_kg_m3 <= 0:
    raise ValueError("water_density_kg_m3 must be positive")

  speed_m_s = knots_to_mps(speed_knots)
  reference_force_n = (
      0.5 * water_density_kg_m3 * speed_m_s**2 * wetted_surface_area_m2
  )
  return residual_resistance_n / reference_force_n


def calculate_residual_resistance(
    residual_resistance_coefficient,
    speed_knots,
    wetted_surface_area_m2,
    water_density_kg_m3=WATER_DENSITY_KG_M3,
):
  """Convert a supplied residual-resistance coefficient back to force.

  Wetted surface is the coefficient reference area. This representation utility
  does not infer the coefficient from Froude number or implement Holtrop, Delft,
  model-test interpolation, CFD fitting, or an empirical residual prediction.
  """
  if residual_resistance_coefficient < 0:
    raise ValueError(
        "residual_resistance_coefficient must be non-negative"
    )
  if speed_knots < 0:
    raise ValueError("speed_knots must be non-negative")
  if wetted_surface_area_m2 <= 0:
    raise ValueError("wetted_surface_area_m2 must be positive")
  if water_density_kg_m3 <= 0:
    raise ValueError("water_density_kg_m3 must be positive")
  if speed_knots == 0:
    return 0.0

  speed_m_s = knots_to_mps(speed_knots)
  return (
      residual_resistance_coefficient
      * 0.5
      * water_density_kg_m3
      * speed_m_s**2
      * wetted_surface_area_m2
  )


def calculate_total_resistance(
    viscous_resistance_n,
    residual_resistance_n,
    appendage_resistance_n=0.0,
):
  if viscous_resistance_n < 0:
    raise ValueError("viscous_resistance_n must be non-negative")
  if residual_resistance_n < 0:
    raise ValueError("residual_resistance_n must be non-negative")
  if appendage_resistance_n < 0:
    raise ValueError("appendage_resistance_n must be non-negative")

  return (
      viscous_resistance_n
      + residual_resistance_n
      + appendage_resistance_n
  )


def calculate_effective_power_kw(total_resistance_n, speed_knots):
  if total_resistance_n < 0:
    raise ValueError("total_resistance_n must be non-negative")

  speed_m_s = knots_to_mps(speed_knots)
  return total_resistance_n * speed_m_s / 1000.0
