"""v0.2 cruise-power methodology selection by supported operating speed."""

from config.operational_speed import (
    MAX_OPERATION_SPEED_KNOTS,
    MIN_OPERATION_SPEED_KNOTS,
)

RESISTANCE_CHAIN_METHOD = "resistance_chain"
PRELIMINARY_SPEED_POWER_METHOD = "preliminary_speed_power"
RESISTANCE_CHAIN_MAX_SPEED_KNOTS = 6.0

METHOD_LABELS_TR = {
    RESISTANCE_CHAIN_METHOD: "Direnç tabanlı ön seyir hesabı",
    PRELIMINARY_SPEED_POWER_METHOD: "Piyasa referanslı ön güç ölçeklemesi",
}


def cruise_methodology_for_speed(speed_knots):
  """Return the v0.2 cruise-power methodology for a supported speed."""
  speed_knots = float(speed_knots)
  if not MIN_OPERATION_SPEED_KNOTS <= speed_knots <= MAX_OPERATION_SPEED_KNOTS:
    raise ValueError("speed_knots must be within supported operating range")
  if speed_knots <= RESISTANCE_CHAIN_MAX_SPEED_KNOTS:
    return RESISTANCE_CHAIN_METHOD
  return PRELIMINARY_SPEED_POWER_METHOD


def cruise_methodology_label_tr(speed_knots):
  return METHOD_LABELS_TR[cruise_methodology_for_speed(speed_knots)]
