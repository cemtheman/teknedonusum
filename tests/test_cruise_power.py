from dataclasses import FrozenInstanceError

import pytest

from calculations.cruise_power import calculate_cruise_power_envelope


def test_result_is_immutable():
  result = calculate_cruise_power_envelope("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.speed_knots = 8.0


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected_reference"),
    (
        ("v1", 6.0, 60.0 * (0.6 ** 3.30)),
        ("v1", 8.0, 60.0 * (0.8 ** 3.30)),
        ("v1", 10.0, 60.0),
        ("v2", 6.0, 65.0 * (0.6 ** 2.85)),
        ("v2", 8.0, 65.0 * (0.8 ** 2.85)),
        ("v2", 10.0, 65.0),
        ("v3", 6.0, 75.0 * (0.6 ** 2.85)),
        ("v3", 8.0, 75.0 * (0.8 ** 2.85)),
        ("v3", 10.0, 75.0),
    ),
)
def test_reference_cruise_power(
    vessel_id,
    speed_knots,
    expected_reference,
):
  result = calculate_cruise_power_envelope(vessel_id, speed_knots)

  assert result.reference_cruise_mechanical_power_kw == pytest.approx(
      expected_reference
  )
  assert result.reference_cruise_electrical_power_kw == pytest.approx(
      expected_reference / 0.95
  )


def test_v1_six_knot_sanity_check():
  result = calculate_cruise_power_envelope("v1", 6.0)

  assert result.reference_cruise_mechanical_power_kw == pytest.approx(
      11.11860691775547
  )
  assert result.reference_cruise_electrical_power_kw == pytest.approx(
      11.703796755532073
  )


@pytest.mark.parametrize("speed_knots", (4.5, 11.0))
def test_speed_outside_profile_is_rejected(speed_knots):
  with pytest.raises(ValueError, match="within profile range"):
    calculate_cruise_power_envelope("v1", speed_knots)


@pytest.mark.parametrize("vessel_id", ("", "v4", "V1"))
def test_unknown_vessel_is_rejected(vessel_id):
  with pytest.raises(ValueError, match="vessel_id"):
    calculate_cruise_power_envelope(vessel_id, 6.0)
