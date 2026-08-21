import pytest

from calculations.continuous_cruise_envelope import (
    calculate_continuous_cruise_envelope,
)
from calculations.normative_sizing import calculate_normative_sizing


@pytest.mark.parametrize(
    ("vessel_id", "expected_electrical_kw"),
    (
        ("v1", 7.043492016798769),
        ("v2", 6.70),
        ("v3", 7.65),
    ),
)
def test_six_knot_reference_uses_resistance_chain_for_all_vessels(
    vessel_id,
    expected_electrical_kw,
):
  result = calculate_normative_sizing(vessel_id, 6.0, 35.0)

  assert result.reference_electrical_input_power_kw == pytest.approx(
      expected_electrical_kw,
      rel=0.01,
  )


def test_v2_v3_low_speed_path_no_longer_uses_legacy_speed_power_exponent():
  for vessel_id in ("v2", "v3"):
    result = calculate_normative_sizing(vessel_id, 6.0, 35.0)
    minimum, reference, maximum = calculate_continuous_cruise_envelope(
        vessel_id,
        6.0,
    )

    assert result.reference_cruise_mechanical_power_kw == pytest.approx(
        reference.shaft_power_kw
    )
    assert result.reference_electrical_input_power_kw == pytest.approx(
        reference.electrical_input_power_kw
    )
    assert result.min_cruise_mechanical_power_kw == pytest.approx(
        minimum.shaft_power_kw
    )
    assert result.max_cruise_mechanical_power_kw == pytest.approx(
        maximum.shaft_power_kw
    )


def test_v2_v3_installed_power_envelopes_are_not_changed():
  v2 = calculate_normative_sizing("v2", 6.0, 35.0)
  v3 = calculate_normative_sizing("v3", 6.0, 35.0)

  assert v2.reference_installed_mechanical_power_kw == pytest.approx(30.0)
  assert v3.reference_installed_mechanical_power_kw == pytest.approx(35.0)
