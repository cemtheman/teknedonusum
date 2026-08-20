"""Interpolation for standalone normative market-power envelopes."""

from math import isfinite

from models.power_envelope import (
    InstalledMechanicalPowerEnvelopeResult,
    NormativePowerEnvelope,
)


def interpolate_installed_mechanical_power_envelope(
    profile: NormativePowerEnvelope,
    speed_knots: float,
) -> InstalledMechanicalPowerEnvelopeResult:
  """Linearly interpolate both envelope bounds without extrapolation."""
  if not isinstance(profile, NormativePowerEnvelope):
    raise TypeError("profile must be a NormativePowerEnvelope")
  if not isfinite(speed_knots) or speed_knots < 0:
    raise ValueError("speed_knots must be finite and non-negative")
  if not (
      profile.valid_speed_min_knots
      <= speed_knots
      <= profile.valid_speed_max_knots
  ):
    raise ValueError(
        "speed_knots must be within profile range "
        f"[{profile.valid_speed_min_knots}, {profile.valid_speed_max_knots}]"
    )

  for anchor in profile.anchors:
    if speed_knots == anchor.speed_knots:
      minimum = anchor.min_installed_mechanical_power_kw
      maximum = anchor.max_installed_mechanical_power_kw
      break
  else:
    for lower, upper in zip(profile.anchors, profile.anchors[1:]):
      if lower.speed_knots < speed_knots < upper.speed_knots:
        position = (
            (speed_knots - lower.speed_knots)
            / (upper.speed_knots - lower.speed_knots)
        )
        minimum = lower.min_installed_mechanical_power_kw + position * (
            upper.min_installed_mechanical_power_kw
            - lower.min_installed_mechanical_power_kw
        )
        maximum = lower.max_installed_mechanical_power_kw + position * (
            upper.max_installed_mechanical_power_kw
            - lower.max_installed_mechanical_power_kw
        )
        break
    else:
      raise RuntimeError("profile interpolation interval was not found")

  return InstalledMechanicalPowerEnvelopeResult(
      speed_knots=speed_knots,
      min_installed_mechanical_power_kw=minimum,
      max_installed_mechanical_power_kw=maximum,
      reference_installed_power_kw=(minimum + maximum) / 2.0,
  )
