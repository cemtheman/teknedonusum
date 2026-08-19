"""Preliminary installed-power sensitivity-band scenario evaluation.

Residual-resistance and propulsive-efficiency inputs are supplied scenarios, not
established physical bounds or a probability model. The resulting scenario minimum
and scenario maximum describe only the provided sensitivity band and do not select
a final motor.
"""

from dataclasses import dataclass

from calculations.propulsion import calculate_direct_drive_propulsion_power
from calculations.resistance_sensitivity import calculate_resistance_sensitivity
from models.geometry import PreliminaryVesselGeometry


@dataclass(frozen=True)
class PowerSensitivityPoint:
  residual_resistance_n: float
  propulsive_efficiency: float
  effective_power_kw: float
  motor_output_power_kw: float
  electrical_input_power_kw: float
  installed_power_kw: float


@dataclass(frozen=True)
class PowerSensitivityBand:
  speed_knots: float
  form_factor: float
  appendage_resistance_n: float
  motor_efficiency: float
  design_margin_fraction: float
  points: tuple[PowerSensitivityPoint, ...]
  minimum_installed_power_kw: float
  maximum_installed_power_kw: float


def calculate_power_sensitivity_band(
    geometry: PreliminaryVesselGeometry,
    speed_knots: float,
    form_factor: float,
    residual_resistance_values_n,
    propulsive_efficiency_values,
    appendage_resistance_n: float,
    motor_efficiency: float,
    design_margin_fraction: float,
) -> PowerSensitivityBand:
  residual_values = tuple(residual_resistance_values_n)
  efficiency_values = tuple(propulsive_efficiency_values)
  if not residual_values:
    raise ValueError("residual_resistance_values_n must not be empty")
  if not efficiency_values:
    raise ValueError("propulsive_efficiency_values must not be empty")

  points = []
  for residual_resistance_n in residual_values:
    for propulsive_efficiency in efficiency_values:
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
      points.append(
          PowerSensitivityPoint(
              residual_resistance_n=residual_resistance_n,
              propulsive_efficiency=propulsive_efficiency,
              effective_power_kw=resistance.effective_power_kw,
              motor_output_power_kw=propulsion.motor_output_power_kw,
              electrical_input_power_kw=propulsion.electrical_input_power_kw,
              installed_power_kw=propulsion.installed_power_kw,
          )
      )

  points_tuple = tuple(points)
  installed_values = tuple(point.installed_power_kw for point in points_tuple)
  return PowerSensitivityBand(
      speed_knots=speed_knots,
      form_factor=form_factor,
      appendage_resistance_n=appendage_resistance_n,
      motor_efficiency=motor_efficiency,
      design_margin_fraction=design_margin_fraction,
      points=points_tuple,
      minimum_installed_power_kw=min(installed_values),
      maximum_installed_power_kw=max(installed_values),
  )
