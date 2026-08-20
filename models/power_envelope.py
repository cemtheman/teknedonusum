"""Immutable normative preliminary market-power envelope models."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PowerEnvelopeAnchor:
  speed_knots: float
  min_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float

  def __post_init__(self):
    if not isfinite(self.speed_knots) or self.speed_knots <= 0:
      raise ValueError("speed_knots must be finite and positive")
    for name, value in (
        (
            "min_installed_mechanical_power_kw",
            self.min_installed_mechanical_power_kw,
        ),
        (
            "max_installed_mechanical_power_kw",
            self.max_installed_mechanical_power_kw,
        ),
    ):
      if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    if (
        self.min_installed_mechanical_power_kw
        > self.max_installed_mechanical_power_kw
    ):
      raise ValueError("minimum installed power must not exceed maximum")


@dataclass(frozen=True)
class NormativePowerEnvelope:
  vessel_id: str
  vessel_type: str
  profile_version: str
  assumption_status: str
  provenance: str
  valid_speed_min_knots: float
  valid_speed_max_knots: float
  extrapolation_allowed: bool
  anchors: tuple[PowerEnvelopeAnchor, ...]

  def __post_init__(self):
    for name in (
        "vessel_id",
        "vessel_type",
        "profile_version",
        "assumption_status",
        "provenance",
    ):
      if not getattr(self, name):
        raise ValueError(f"{name} must not be empty")
    if self.extrapolation_allowed:
      raise ValueError("normative power envelopes must reject extrapolation")
    if len(self.anchors) < 2:
      raise ValueError("anchors must contain at least two points")

    speeds = tuple(anchor.speed_knots for anchor in self.anchors)
    if any(
        current <= previous
        for previous, current in zip(speeds, speeds[1:])
    ):
      raise ValueError("anchor speeds must be strictly increasing")
    if (
        self.valid_speed_min_knots != speeds[0]
        or self.valid_speed_max_knots != speeds[-1]
    ):
      raise ValueError("valid speed range must match the anchor range")


@dataclass(frozen=True)
class InstalledMechanicalPowerEnvelopeResult:
  speed_knots: float
  min_installed_mechanical_power_kw: float
  max_installed_mechanical_power_kw: float
  reference_installed_power_kw: float
