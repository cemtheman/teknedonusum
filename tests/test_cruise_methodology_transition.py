import pytest

from calculations.continuous_cruise_envelope import (
    calculate_continuous_cruise_envelope,
)
from calculations.cruise_power import calculate_cruise_power_envelope
from calculations.normative_sizing import calculate_normative_sizing


@pytest.mark.parametrize("speed_knots", (5.0, 5.5, 6.0))
@pytest.mark.parametrize("vessel_id", ("v1", "v2", "v3"))
def test_normative_sizing_uses_resistance_chain_through_six_knots(
    vessel_id,
    speed_knots,
):
  sizing = calculate_normative_sizing(vessel_id, speed_knots)
  _, reference, _ = calculate_continuous_cruise_envelope(
      vessel_id,
      speed_knots,
  )

  assert sizing.reference_electrical_input_power_kw == pytest.approx(
      reference.electrical_input_power_kw
  )


@pytest.mark.parametrize("speed_knots", (6.5, 10.0))
@pytest.mark.parametrize("vessel_id", ("v1", "v2", "v3"))
def test_normative_sizing_uses_preliminary_speed_power_above_six_knots(
    vessel_id,
    speed_knots,
):
  sizing = calculate_normative_sizing(vessel_id, speed_knots)
  legacy = calculate_cruise_power_envelope(vessel_id, speed_knots)

  assert sizing.reference_electrical_input_power_kw == pytest.approx(
      legacy.reference_cruise_electrical_power_kw
  )
