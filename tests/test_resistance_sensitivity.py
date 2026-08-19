import pytest

from calculations.resistance_sensitivity import (
    ResistanceSensitivityResult,
    calculate_resistance_sensitivity,
)
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY


V1_GEOMETRY = PRELIMINARY_VESSEL_GEOMETRY["v1"]


def test_six_knot_baseline_scenario():
  # Scenario inputs are sensitivity fixtures, not verified vessel resistance data.
  result = calculate_resistance_sensitivity(
      geometry=V1_GEOMETRY,
      speed_knots=6.0,
      form_factor=0.15,
      residual_resistance_n=500.0,
      appendage_resistance_n=50.0,
  )

  assert isinstance(result, ResistanceSensitivityResult)
  assert result.froude_number == pytest.approx(0.29192856556133584)
  assert result.frictional_resistance_n == pytest.approx(348.4253689773023)
  assert result.viscous_resistance_n == pytest.approx(400.6891743238976)
  assert result.residual_resistance_n == 500.0
  assert result.residual_resistance_coefficient == pytest.approx(
      0.0034986462403519525
  )
  assert result.total_resistance_n == pytest.approx(950.6891743238975)
  assert result.effective_power_kw == pytest.approx(2.9344580495752988)


def test_ten_knot_baseline_scenario():
  # Scenario inputs are sensitivity fixtures, not verified vessel resistance data.
  result = calculate_resistance_sensitivity(
      geometry=V1_GEOMETRY,
      speed_knots=10.0,
      form_factor=0.15,
      residual_resistance_n=1500.0,
      appendage_resistance_n=100.0,
  )

  assert result.froude_number == pytest.approx(0.4865476092688931)
  assert result.frictional_resistance_n == pytest.approx(894.8322878011685)
  assert result.viscous_resistance_n == pytest.approx(1029.0571309713437)
  assert result.residual_resistance_n == 1500.0
  assert result.residual_resistance_coefficient == pytest.approx(
      0.003778537939580108
  )
  assert result.total_resistance_n == pytest.approx(2629.0571309713437)
  assert result.effective_power_kw == pytest.approx(13.52502666685422)


def test_higher_residual_increases_total_resistance_and_effective_power():
  low_residual = calculate_resistance_sensitivity(
      V1_GEOMETRY,
      speed_knots=6.0,
      form_factor=0.15,
      residual_resistance_n=500.0,
  )
  high_residual = calculate_resistance_sensitivity(
      V1_GEOMETRY,
      speed_knots=6.0,
      form_factor=0.15,
      residual_resistance_n=1500.0,
  )

  assert high_residual.total_resistance_n > low_residual.total_resistance_n
  assert high_residual.effective_power_kw > low_residual.effective_power_kw


def test_higher_form_factor_increases_viscous_and_total_resistance():
  low_form_factor = calculate_resistance_sensitivity(
      V1_GEOMETRY,
      speed_knots=6.0,
      form_factor=0.0,
      residual_resistance_n=500.0,
  )
  high_form_factor = calculate_resistance_sensitivity(
      V1_GEOMETRY,
      speed_knots=6.0,
      form_factor=0.20,
      residual_resistance_n=500.0,
  )

  assert (
      high_form_factor.viscous_resistance_n
      > low_form_factor.viscous_resistance_n
  )
  assert high_form_factor.total_resistance_n > low_form_factor.total_resistance_n


def test_zero_speed_preserves_external_resistance_but_has_zero_power():
  result = calculate_resistance_sensitivity(
      V1_GEOMETRY,
      speed_knots=0.0,
      form_factor=0.15,
      residual_resistance_n=500.0,
      appendage_resistance_n=50.0,
  )

  assert result.froude_number == 0.0
  assert result.frictional_resistance_n == 0.0
  assert result.viscous_resistance_n == 0.0
  assert result.residual_resistance_n == 500.0
  assert result.residual_resistance_coefficient is None
  assert result.total_resistance_n == pytest.approx(550.0)
  assert result.effective_power_kw == 0.0


def test_invalid_geometry_type_is_rejected():
  with pytest.raises(TypeError):
    calculate_resistance_sensitivity(object(), 6.0, 0.15, 500.0)


def test_negative_speed_is_rejected():
  with pytest.raises(ValueError):
    calculate_resistance_sensitivity(V1_GEOMETRY, -1.0, 0.15, 500.0)


def test_negative_form_factor_is_rejected():
  with pytest.raises(ValueError):
    calculate_resistance_sensitivity(V1_GEOMETRY, 6.0, -0.1, 500.0)


def test_negative_residual_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_resistance_sensitivity(V1_GEOMETRY, 6.0, 0.15, -1.0)


def test_negative_appendage_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_resistance_sensitivity(V1_GEOMETRY, 6.0, 0.15, 500.0, -1.0)
