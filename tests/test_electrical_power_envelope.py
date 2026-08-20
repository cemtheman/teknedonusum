from dataclasses import FrozenInstanceError

import pytest

from calculations.electrical_power_envelope import (
    convert_to_electrical_input_power_envelope,
)
from calculations.power_envelope import (
    interpolate_installed_mechanical_power_envelope,
)
from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS


def converted(vessel_id, speed_knots, motor_efficiency=0.95):
  mechanical = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      speed_knots,
  )
  return convert_to_electrical_input_power_envelope(
      mechanical,
      motor_efficiency,
  )


def test_result_is_immutable():
  result = converted("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.motor_efficiency = 0.90


def test_default_efficiency_uses_preliminary_scenario_source():
  mechanical = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES["v1"],
      6.0,
  )
  result = convert_to_electrical_input_power_envelope(mechanical)

  assert result.motor_efficiency == (
      V1_PRELIMINARY_SCENARIO_ASSUMPTIONS.motor_efficiency
  )
  assert result.max_electrical_input_power_kw == pytest.approx(40.0 / 0.95)


@pytest.mark.parametrize(
    (
        "vessel_id",
        "speed_knots",
        "mechanical",
        "electrical",
    ),
    (
        ("v1", 6.0, (20.0, 30.0, 40.0), (20 / .95, 30 / .95, 40 / .95)),
        ("v2", 8.0, (30.0, 42.5, 55.0), (30 / .95, 42.5 / .95, 55 / .95)),
        ("v3", 10.0, (60.0, 75.0, 90.0), (60 / .95, 75 / .95, 90 / .95)),
    ),
)
def test_normative_envelope_conversion(
    vessel_id,
    speed_knots,
    mechanical,
    electrical,
):
  result = converted(vessel_id, speed_knots)

  assert (
      result.min_installed_mechanical_power_kw,
      result.reference_installed_mechanical_power_kw,
      result.max_installed_mechanical_power_kw,
  ) == mechanical
  assert result.min_electrical_input_power_kw == pytest.approx(electrical[0])
  assert result.reference_electrical_input_power_kw == pytest.approx(electrical[1])
  assert result.max_electrical_input_power_kw == pytest.approx(electrical[2])
  assert (
      result.min_electrical_input_power_kw
      <= result.reference_electrical_input_power_kw
      <= result.max_electrical_input_power_kw
  )


def test_efficiency_one_is_identity():
  result = converted("v2", 8.0, motor_efficiency=1.0)

  assert result.min_electrical_input_power_kw == 30.0
  assert result.reference_electrical_input_power_kw == 42.5
  assert result.max_electrical_input_power_kw == 55.0


@pytest.mark.parametrize(
    "motor_efficiency",
    (0.0, -0.01, 1.01, float("nan"), float("inf")),
)
def test_invalid_motor_efficiency_is_rejected(motor_efficiency):
  mechanical = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES["v1"],
      6.0,
  )

  with pytest.raises(ValueError, match="motor_efficiency"):
    convert_to_electrical_input_power_envelope(
        mechanical,
        motor_efficiency,
    )
