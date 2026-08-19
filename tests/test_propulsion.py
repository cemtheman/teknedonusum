import pytest

from calculations.propulsion import calculate_direct_drive_propulsion_power


def test_ten_knot_baseline():
  # PE is from the Commit 18 example; its residual resistance is not verified.
  # 0.60 is preliminary propulsive efficiency, 0.95 matches the commission's
  # minimum-efficiency test input, and 0.15 is preliminary design margin. These
  # are not verified final-vessel design values.
  result = calculate_direct_drive_propulsion_power(
      effective_power_kw=13.52502666685422,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
      design_margin_fraction=0.15,
  )

  assert result.motor_output_power_kw == pytest.approx(22.5417111114237)
  assert result.electrical_input_power_kw == pytest.approx(23.728116959393372)
  assert result.installed_power_kw == pytest.approx(25.922967778137256)


def test_six_knot_baseline():
  # PE is from the Commit 18 example; its residual resistance is not verified.
  # Efficiency and margin inputs are preliminary test assumptions, not verified
  # final-vessel design values.
  result = calculate_direct_drive_propulsion_power(
      effective_power_kw=2.9344580495752988,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
      design_margin_fraction=0.15,
  )

  assert result.motor_output_power_kw == pytest.approx(4.890763415958832)
  assert result.electrical_input_power_kw == pytest.approx(5.14817201679877)
  assert result.installed_power_kw == pytest.approx(5.624377928352656)


def test_no_margin_installed_power_equals_motor_output():
  result = calculate_direct_drive_propulsion_power(
      effective_power_kw=10.0,
      propulsive_efficiency=0.60,
      motor_efficiency=0.95,
  )
  assert result.installed_power_kw == result.motor_output_power_kw


def test_lower_propulsive_efficiency_increases_all_downstream_power():
  low_efficiency = calculate_direct_drive_propulsion_power(10.0, 0.50, 0.95, 0.15)
  high_efficiency = calculate_direct_drive_propulsion_power(10.0, 0.65, 0.95, 0.15)

  assert low_efficiency.motor_output_power_kw > high_efficiency.motor_output_power_kw
  assert (
      low_efficiency.electrical_input_power_kw
      > high_efficiency.electrical_input_power_kw
  )
  assert low_efficiency.installed_power_kw > high_efficiency.installed_power_kw


def test_motor_efficiency_changes_only_electrical_input_power():
  low_efficiency = calculate_direct_drive_propulsion_power(10.0, 0.60, 0.90, 0.15)
  high_efficiency = calculate_direct_drive_propulsion_power(10.0, 0.60, 0.95, 0.15)

  assert (
      low_efficiency.electrical_input_power_kw
      > high_efficiency.electrical_input_power_kw
  )
  assert low_efficiency.motor_output_power_kw == high_efficiency.motor_output_power_kw
  assert low_efficiency.installed_power_kw == high_efficiency.installed_power_kw


def test_design_margin_changes_only_installed_power():
  no_margin = calculate_direct_drive_propulsion_power(10.0, 0.60, 0.95, 0.0)
  high_margin = calculate_direct_drive_propulsion_power(10.0, 0.60, 0.95, 0.20)

  assert high_margin.installed_power_kw > no_margin.installed_power_kw
  assert high_margin.motor_output_power_kw == no_margin.motor_output_power_kw
  assert high_margin.electrical_input_power_kw == no_margin.electrical_input_power_kw


def test_zero_effective_power():
  result = calculate_direct_drive_propulsion_power(0.0, 0.60, 0.95, 0.15)

  assert result.effective_power_kw == 0.0
  assert result.propulsive_efficiency == 0.60
  assert result.motor_efficiency == 0.95
  assert result.design_margin_fraction == 0.15
  assert result.motor_output_power_kw == 0.0
  assert result.electrical_input_power_kw == 0.0
  assert result.installed_power_kw == 0.0


def test_negative_effective_power_is_rejected():
  with pytest.raises(ValueError):
    calculate_direct_drive_propulsion_power(-1.0, 0.60, 0.95)


@pytest.mark.parametrize("propulsive_efficiency", [0.0, -0.1, 1.1])
def test_invalid_propulsive_efficiency_is_rejected(propulsive_efficiency):
  with pytest.raises(ValueError):
    calculate_direct_drive_propulsion_power(10.0, propulsive_efficiency, 0.95)


@pytest.mark.parametrize("motor_efficiency", [0.0, -0.1, 1.1])
def test_invalid_motor_efficiency_is_rejected(motor_efficiency):
  with pytest.raises(ValueError):
    calculate_direct_drive_propulsion_power(10.0, 0.60, motor_efficiency)


def test_negative_design_margin_is_rejected():
  with pytest.raises(ValueError):
    calculate_direct_drive_propulsion_power(10.0, 0.60, 0.95, -0.1)
