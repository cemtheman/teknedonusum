"""Estimate cruise power separately from installed motor capacity."""

from math import isfinite

from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.cruise_power import CruisePowerEnvelopeResult


SPEED_POWER_EXPONENTS = {
    "v1": 3.30,
    "v2": 2.85,
    "v3": 2.85,
}

REFERENCE_SPEED_KNOTS = 10.0


def calculate_cruise_power_envelope(
    vessel_id: str,
    speed_knots: float,
    motor_efficiency: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.motor_efficiency
    ),
) -> CruisePowerEnvelopeResult:
  """Scale the 10-knot market-power reference to the selected cruise speed."""
  if vessel_id not in NORMATIVE_POWER_ENVELOPES:
    raise ValueError("vessel_id must be one of v1, v2, or v3")
  if not isfinite(speed_knots) or speed_knots <= 0:
    raise ValueError("speed_knots must be finite and positive")
  if not isfinite(motor_efficiency) or not 0 < motor_efficiency <= 1:
    raise ValueError(
        "motor_efficiency must be finite, positive, and at most one"
    )

  profile = NORMATIVE_POWER_ENVELOPES[vessel_id]
  if not (
      profile.valid_speed_min_knots
      <= speed_knots
      <= profile.valid_speed_max_knots
  ):
    raise ValueError(
        "speed_knots must be within profile range "
        f"[{profile.valid_speed_min_knots}, "
        f"{profile.valid_speed_max_knots}]"
    )

  reference_anchor = profile.anchors[-1]
  if reference_anchor.speed_knots != REFERENCE_SPEED_KNOTS:
    raise ValueError("power profile must contain a 10-knot reference anchor")

  exponent = SPEED_POWER_EXPONENTS[vessel_id]
  speed_factor = (speed_knots / REFERENCE_SPEED_KNOTS) ** exponent

  minimum = (
      reference_anchor.min_installed_mechanical_power_kw * speed_factor
  )
  maximum = (
      reference_anchor.max_installed_mechanical_power_kw * speed_factor
  )
  reference = (minimum + maximum) / 2.0

  return CruisePowerEnvelopeResult(
      vessel_id=vessel_id,
      speed_knots=speed_knots,
      speed_power_exponent=exponent,
      min_cruise_mechanical_power_kw=minimum,
      reference_cruise_mechanical_power_kw=reference,
      max_cruise_mechanical_power_kw=maximum,
      motor_efficiency=motor_efficiency,
      min_cruise_electrical_power_kw=minimum / motor_efficiency,
      reference_cruise_electrical_power_kw=reference / motor_efficiency,
      max_cruise_electrical_power_kw=maximum / motor_efficiency,
  )