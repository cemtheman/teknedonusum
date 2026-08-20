"""Immutable assumptions and results for propulsion energy envelopes."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class OperationalEnergyAssumption:
  operating_hours_per_day: float
  duty_cycle: float
  assumption_status: str
  provenance: str

  def __post_init__(self):
    if (
        not isfinite(self.operating_hours_per_day)
        or not 0 < self.operating_hours_per_day <= 24
    ):
      raise ValueError(
          "operating_hours_per_day must be finite, positive, and at most 24"
      )
    if not isfinite(self.duty_cycle) or not 0 < self.duty_cycle <= 1:
      raise ValueError("duty_cycle must be finite, positive, and at most one")
    if not self.assumption_status:
      raise ValueError("assumption_status must not be empty")
    if not self.provenance:
      raise ValueError("provenance must not be empty")


@dataclass(frozen=True)
class DailyPropulsionElectricalEnergyEnvelopeResult:
  vessel_id: str
  speed_knots: float
  min_electrical_input_power_kw: float
  reference_electrical_input_power_kw: float
  max_electrical_input_power_kw: float
  operating_hours_per_day: float
  duty_cycle: float
  effective_powered_hours_per_day: float
  min_daily_electrical_energy_kwh: float
  reference_daily_electrical_energy_kwh: float
  max_daily_electrical_energy_kwh: float

  def __post_init__(self):
    if not self.vessel_id:
      raise ValueError("vessel_id must not be empty")
    if not isfinite(self.speed_knots) or self.speed_knots < 0:
      raise ValueError("speed_knots must be finite and non-negative")
    if (
        not isfinite(self.operating_hours_per_day)
        or not 0 < self.operating_hours_per_day <= 24
    ):
      raise ValueError(
          "operating_hours_per_day must be finite, positive, and at most 24"
      )
    if not isfinite(self.duty_cycle) or not 0 < self.duty_cycle <= 1:
      raise ValueError("duty_cycle must be finite, positive, and at most one")
    if (
        not isfinite(self.effective_powered_hours_per_day)
        or not 0 < self.effective_powered_hours_per_day
        <= self.operating_hours_per_day
    ):
      raise ValueError(
          "effective powered hours must be positive and not exceed "
          "operating hours"
      )

    power = (
        self.min_electrical_input_power_kw,
        self.reference_electrical_input_power_kw,
        self.max_electrical_input_power_kw,
    )
    energy = (
        self.min_daily_electrical_energy_kwh,
        self.reference_daily_electrical_energy_kwh,
        self.max_daily_electrical_energy_kwh,
    )
    if any(not isfinite(value) or value <= 0 for value in power + energy):
      raise ValueError("power and energy values must be finite and positive")
    if not power[0] <= power[1] <= power[2]:
      raise ValueError("electrical power values must be ordered")
    if not energy[0] <= energy[1] <= energy[2]:
      raise ValueError("daily electrical energy values must be ordered")
