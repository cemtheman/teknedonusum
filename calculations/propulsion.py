"""Direct-drive preliminary electric propulsion power chain.

``effective_power_kw`` is hull effective power. ``motor_output_power_kw`` is the
mechanical output required at the motor shaft after propulsive-efficiency losses.
``electrical_input_power_kw`` is the power required from the electrical system
after motor efficiency. ``installed_power_kw`` is the motor mechanical-output
requirement plus design margin; it is not a manufacturer nameplate recommendation.

A separate gearbox/transmission efficiency is intentionally not modeled. Transient
torque, manoeuvring, bollard pull, cooling derating, class requirements, propeller
matching, motor thermal limits, controller/inverter limits, and shaft/bearing detail
losses are outside this preliminary model's scope.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PropulsionPowerResult:
  effective_power_kw: float
  propulsive_efficiency: float
  motor_efficiency: float
  design_margin_fraction: float
  motor_output_power_kw: float
  electrical_input_power_kw: float
  installed_power_kw: float


def calculate_direct_drive_propulsion_power(
    effective_power_kw: float,
    propulsive_efficiency: float,
    motor_efficiency: float,
    design_margin_fraction: float = 0.0,
) -> PropulsionPowerResult:
  if not effective_power_kw >= 0:
    raise ValueError("effective_power_kw must be non-negative")
  if not 0 < propulsive_efficiency <= 1:
    raise ValueError("propulsive_efficiency must be greater than zero and at most one")
  if not 0 < motor_efficiency <= 1:
    raise ValueError("motor_efficiency must be greater than zero and at most one")
  if not design_margin_fraction >= 0:
    raise ValueError("design_margin_fraction must be non-negative")

  motor_output_power_kw = effective_power_kw / propulsive_efficiency
  electrical_input_power_kw = motor_output_power_kw / motor_efficiency
  installed_power_kw = motor_output_power_kw * (1.0 + design_margin_fraction)

  return PropulsionPowerResult(
      effective_power_kw=effective_power_kw,
      propulsive_efficiency=propulsive_efficiency,
      motor_efficiency=motor_efficiency,
      design_margin_fraction=design_margin_fraction,
      motor_output_power_kw=motor_output_power_kw,
      electrical_input_power_kw=electrical_input_power_kw,
      installed_power_kw=installed_power_kw,
  )
