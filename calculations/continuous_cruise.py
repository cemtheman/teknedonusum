"""Physics-based low-speed continuous-cruise power chain.

This module deliberately does not use the legacy V^3.3 / V^2.85 speed-power
laws or the 10-knot installed-power envelope. Residual and appendage resistance
must be supplied explicitly until a defensible calibrated prediction method is
selected.
"""

from calculations.hydrodynamics import (
    calculate_effective_power_kw,
    calculate_frictional_resistance,
    calculate_froude_number,
    calculate_reynolds_number,
    calculate_total_resistance,
    calculate_viscous_resistance,
)
from models.continuous_cruise import (
    ContinuousCruisePowerResult,
    SolarOnlyObservationBound,
)


def calculate_continuous_cruise_power(
    *,
    speed_knots,
    waterline_length_m,
    wetted_surface_area_m2,
    form_factor,
    residual_resistance_n,
    appendage_resistance_n,
    propulsive_efficiency,
    motor_efficiency,
):
  """Calculate continuous cruise power from transparent resistance components."""
  if speed_knots <= 0:
    raise ValueError("speed_knots must be positive")
  if waterline_length_m <= 0:
    raise ValueError("waterline_length_m must be positive")
  if wetted_surface_area_m2 <= 0:
    raise ValueError("wetted_surface_area_m2 must be positive")
  if form_factor < 0:
    raise ValueError("form_factor must be non-negative")
  if residual_resistance_n < 0:
    raise ValueError("residual_resistance_n must be non-negative")
  if appendage_resistance_n < 0:
    raise ValueError("appendage_resistance_n must be non-negative")
  if not 0 < propulsive_efficiency <= 1:
    raise ValueError("propulsive_efficiency must be in (0, 1]")
  if not 0 < motor_efficiency <= 1:
    raise ValueError("motor_efficiency must be in (0, 1]")

  froude = calculate_froude_number(speed_knots, waterline_length_m)
  reynolds = calculate_reynolds_number(speed_knots, waterline_length_m)
  frictional = calculate_frictional_resistance(
      speed_knots,
      waterline_length_m,
      wetted_surface_area_m2,
  )
  viscous = calculate_viscous_resistance(
      speed_knots,
      waterline_length_m,
      wetted_surface_area_m2,
      form_factor,
  )
  total = calculate_total_resistance(
      viscous,
      residual_resistance_n,
      appendage_resistance_n,
  )
  effective_kw = calculate_effective_power_kw(total, speed_knots)
  shaft_kw = effective_kw / propulsive_efficiency
  electrical_kw = shaft_kw / motor_efficiency

  return ContinuousCruisePowerResult(
      speed_knots=float(speed_knots),
      froude_number=froude,
      reynolds_number=reynolds,
      frictional_resistance_n=frictional,
      viscous_resistance_n=viscous,
      residual_resistance_n=float(residual_resistance_n),
      appendage_resistance_n=float(appendage_resistance_n),
      total_resistance_n=total,
      effective_power_kw=effective_kw,
      shaft_power_kw=shaft_kw,
      electrical_input_power_kw=electrical_kw,
      propulsive_efficiency=float(propulsive_efficiency),
      motor_efficiency=float(motor_efficiency),
  )


def infer_solar_only_observation_bound(
    *,
    installed_pv_kwp,
    specific_pv_power_kw_per_kwp,
):
  """Convert observed solar-only operation into an electrical-power upper bound.

  This is a validation constraint, not a resistance prediction. If propulsion
  was observed without battery discharge, propulsion electrical demand at that
  instant cannot have exceeded available PV power.
  """
  installed_pv_kwp = float(installed_pv_kwp)
  specific_pv_power_kw_per_kwp = float(specific_pv_power_kw_per_kwp)

  if installed_pv_kwp <= 0:
    raise ValueError("installed_pv_kwp must be positive")
  if specific_pv_power_kw_per_kwp < 0:
    raise ValueError("specific_pv_power_kw_per_kwp must be non-negative")

  solar_kw = installed_pv_kwp * specific_pv_power_kw_per_kwp

  return SolarOnlyObservationBound(
      installed_pv_kwp=installed_pv_kwp,
      specific_pv_power_kw_per_kwp=specific_pv_power_kw_per_kwp,
      observed_solar_available_kw=solar_kw,
      maximum_electrical_propulsion_power_kw=solar_kw,
  )
