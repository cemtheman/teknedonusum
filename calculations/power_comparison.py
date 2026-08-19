"""Scenario comparison between legacy and preliminary propulsion power results.

Legacy power and preliminary installed power come from different model assumptions.
The preliminary result is sensitive to supplied residual resistance and efficiency
inputs. This module does not validate either model or decide which is correct; it
only provides scenario comparison, and its result is not a final motor selection.
"""

from dataclasses import dataclass

from calculations.propulsion import calculate_direct_drive_propulsion_power
from calculations.resistance_sensitivity import calculate_resistance_sensitivity
from calculations.vessel_physics import calc_calibrated_vessel_physics
from models.geometry import PreliminaryVesselGeometry


@dataclass(frozen=True)
class PowerComparisonResult:
  speed_knots: float
  legacy_power_kw: float
  effective_power_kw: float
  motor_output_power_kw: float
  electrical_input_power_kw: float
  installed_power_kw: float
  legacy_minus_installed_kw: float
  legacy_to_installed_ratio: float


def compare_legacy_and_preliminary_power(
    spec,
    geometry: PreliminaryVesselGeometry,
    speed_knots: float,
    daily_miles: float,
    sun_hours: float,
    form_factor: float,
    residual_resistance_n: float,
    appendage_resistance_n: float,
    propulsive_efficiency: float,
    motor_efficiency: float,
    design_margin_fraction: float,
) -> PowerComparisonResult:
  legacy = calc_calibrated_vessel_physics(
      spec,
      speed_knots,
      daily_miles,
      sun_hours,
  )
  legacy_power_kw = legacy.max_power

  resistance = calculate_resistance_sensitivity(
      geometry=geometry,
      speed_knots=speed_knots,
      form_factor=form_factor,
      residual_resistance_n=residual_resistance_n,
      appendage_resistance_n=appendage_resistance_n,
  )
  propulsion = calculate_direct_drive_propulsion_power(
      effective_power_kw=resistance.effective_power_kw,
      propulsive_efficiency=propulsive_efficiency,
      motor_efficiency=motor_efficiency,
      design_margin_fraction=design_margin_fraction,
  )

  legacy_minus_installed_kw = legacy_power_kw - propulsion.installed_power_kw
  legacy_to_installed_ratio = (
      legacy_power_kw / propulsion.installed_power_kw
      if propulsion.installed_power_kw != 0
      else float("inf")
  )

  return PowerComparisonResult(
      speed_knots=speed_knots,
      legacy_power_kw=legacy_power_kw,
      effective_power_kw=resistance.effective_power_kw,
      motor_output_power_kw=propulsion.motor_output_power_kw,
      electrical_input_power_kw=propulsion.electrical_input_power_kw,
      installed_power_kw=propulsion.installed_power_kw,
      legacy_minus_installed_kw=legacy_minus_installed_kw,
      legacy_to_installed_ratio=legacy_to_installed_ratio,
  )
