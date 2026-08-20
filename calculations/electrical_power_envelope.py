"""Convert installed mechanical-power envelopes to electrical input power."""

from math import isfinite

from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
from models.electrical_power_envelope import ElectricalInputPowerEnvelopeResult
from models.power_envelope import InstalledMechanicalPowerEnvelopeResult


def convert_to_electrical_input_power_envelope(
    mechanical_envelope: InstalledMechanicalPowerEnvelopeResult,
    motor_efficiency: float = (
        V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.motor_efficiency
    ),
) -> ElectricalInputPowerEnvelopeResult:
  """Apply motor efficiency once to each installed mechanical-power bound."""
  if not isinstance(
      mechanical_envelope,
      InstalledMechanicalPowerEnvelopeResult,
  ):
    raise TypeError(
        "mechanical_envelope must be an "
        "InstalledMechanicalPowerEnvelopeResult"
    )
  if not isfinite(motor_efficiency) or not 0 < motor_efficiency <= 1:
    raise ValueError("motor_efficiency must be finite, positive, and at most one")

  minimum = mechanical_envelope.min_installed_mechanical_power_kw
  reference = mechanical_envelope.reference_installed_power_kw
  maximum = mechanical_envelope.max_installed_mechanical_power_kw
  if not minimum <= reference <= maximum:
    raise ValueError("mechanical power values must be ordered")

  return ElectricalInputPowerEnvelopeResult(
      speed_knots=mechanical_envelope.speed_knots,
      min_installed_mechanical_power_kw=minimum,
      reference_installed_mechanical_power_kw=reference,
      max_installed_mechanical_power_kw=maximum,
      motor_efficiency=motor_efficiency,
      min_electrical_input_power_kw=minimum / motor_efficiency,
      reference_electrical_input_power_kw=reference / motor_efficiency,
      max_electrical_input_power_kw=maximum / motor_efficiency,
  )
