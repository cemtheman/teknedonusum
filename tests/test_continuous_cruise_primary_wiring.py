import pytest
from calculations.continuous_cruise_envelope import calculate_v1_continuous_cruise_envelope

def test_v1_six_knot_reference_is_about_seven_kw_electrical():
    minimum, reference, maximum = calculate_v1_continuous_cruise_envelope(6.0)
    assert minimum.electrical_input_power_kw < reference.electrical_input_power_kw < maximum.electrical_input_power_kw
    assert reference.electrical_input_power_kw == pytest.approx(7.04, rel=5e-3)
    assert reference.electrical_input_power_kw < 11.0

def test_v1_calibration_is_limited_to_continuous_cruise_band():
    with pytest.raises(ValueError):
        calculate_v1_continuous_cruise_envelope(10.0)
