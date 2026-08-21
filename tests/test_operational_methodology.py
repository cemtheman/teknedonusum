import pytest

from config.operational_methodology import (
    PRELIMINARY_SPEED_POWER_METHOD,
    RESISTANCE_CHAIN_METHOD,
    cruise_methodology_for_speed,
    cruise_methodology_label_tr,
)


@pytest.mark.parametrize("speed_knots", (5.0, 5.5, 6.0))
def test_low_speed_band_uses_resistance_chain(speed_knots):
  assert cruise_methodology_for_speed(speed_knots) == RESISTANCE_CHAIN_METHOD
  assert cruise_methodology_label_tr(speed_knots) == (
      "Direnç tabanlı ön seyir hesabı"
  )


@pytest.mark.parametrize("speed_knots", (6.5, 10.0))
def test_upper_speed_band_uses_preliminary_speed_power(speed_knots):
  assert (
      cruise_methodology_for_speed(speed_knots)
      == PRELIMINARY_SPEED_POWER_METHOD
  )
  assert cruise_methodology_label_tr(speed_knots) == (
      "Piyasa referanslı ön güç ölçeklemesi"
  )


@pytest.mark.parametrize("speed_knots", (4.5, 10.5))
def test_methodology_rejects_unsupported_speed(speed_knots):
  with pytest.raises(ValueError, match="supported operating range"):
    cruise_methodology_for_speed(speed_knots)
