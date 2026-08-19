import pytest

from calculations.hydrodynamics import (
    calculate_effective_power_kw,
    calculate_frictional_resistance,
    calculate_froude_number,
    calculate_ittc_friction_coefficient,
    calculate_reynolds_number,
    calculate_total_resistance,
    calculate_viscous_resistance,
    knots_to_mps,
)


@pytest.mark.parametrize(
    ("speed_knots", "expected_mps"),
    [(6.0, 3.086664), (10.0, 5.14444)],
)
def test_knots_to_mps(speed_knots, expected_mps):
  assert knots_to_mps(speed_knots) == pytest.approx(expected_mps)


@pytest.mark.parametrize(
    ("speed_knots", "expected_froude"),
    [
        (6.0, 0.29192856556133584),
        (10.0, 0.4865476092688931),
    ],
)
def test_froude_number(speed_knots, expected_froude):
  result = calculate_froude_number(speed_knots, waterline_length_m=11.4)
  assert result == pytest.approx(expected_froude)


@pytest.mark.parametrize(
    ("speed_knots", "expected_reynolds"),
    [(6.0, 35187969.6), (10.0, 58646616.000000015)],
)
def test_reynolds_number(speed_knots, expected_reynolds):
  result = calculate_reynolds_number(
      speed_knots,
      waterline_length_m=11.4,
      kinematic_viscosity_m2_s=1.0e-6,
  )
  assert result == pytest.approx(expected_reynolds)


def test_ittc_friction_coefficient():
  result = calculate_ittc_friction_coefficient(35187969.6)
  assert result == pytest.approx(0.002438034214431361)


def test_frictional_resistance():
  result = calculate_frictional_resistance(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      water_density_kg_m3=1000.0,
  )
  assert result == pytest.approx(348.4253689773023)


def test_zero_speed_frictional_resistance():
  result = calculate_frictional_resistance(
      speed_knots=0.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
  )
  assert result == 0.0


def test_negative_speed_is_rejected():
  with pytest.raises(ValueError):
    knots_to_mps(-1.0)


@pytest.mark.parametrize("waterline_length_m", [0.0, -1.0])
def test_invalid_waterline_length_is_rejected(waterline_length_m):
  with pytest.raises(ValueError):
    calculate_froude_number(6.0, waterline_length_m)


@pytest.mark.parametrize("wetted_surface_area_m2", [0.0, -1.0])
def test_invalid_wetted_surface_area_is_rejected(wetted_surface_area_m2):
  with pytest.raises(ValueError):
    calculate_frictional_resistance(6.0, 11.4, wetted_surface_area_m2)


@pytest.mark.parametrize("kinematic_viscosity_m2_s", [0.0, -1.0])
def test_invalid_kinematic_viscosity_is_rejected(kinematic_viscosity_m2_s):
  with pytest.raises(ValueError):
    calculate_reynolds_number(6.0, 11.4, kinematic_viscosity_m2_s)


@pytest.mark.parametrize("water_density_kg_m3", [0.0, -1.0])
def test_invalid_water_density_is_rejected(water_density_kg_m3):
  with pytest.raises(ValueError):
    calculate_frictional_resistance(
        6.0,
        11.4,
        30.0,
        water_density_kg_m3=water_density_kg_m3,
    )


@pytest.mark.parametrize("reynolds_number", [0.0, -1.0])
def test_invalid_reynolds_number_is_rejected(reynolds_number):
  with pytest.raises(ValueError):
    calculate_ittc_friction_coefficient(reynolds_number)


def test_viscous_resistance():
  result = calculate_viscous_resistance(
      speed_knots=6.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
      form_factor=0.15,
  )
  assert result == pytest.approx(400.6891743238976)


def test_total_resistance():
  result = calculate_total_resistance(
      viscous_resistance_n=400.0,
      residual_resistance_n=250.0,
      appendage_resistance_n=35.0,
  )
  assert result == pytest.approx(685.0)


def test_total_resistance_default_appendage():
  result = calculate_total_resistance(
      viscous_resistance_n=400.0,
      residual_resistance_n=250.0,
  )
  assert result == pytest.approx(650.0)


def test_effective_power():
  result = calculate_effective_power_kw(
      total_resistance_n=1000.0,
      speed_knots=6.0,
  )
  assert result == pytest.approx(3.086664)


def test_zero_speed_effective_power():
  result = calculate_effective_power_kw(
      total_resistance_n=1000.0,
      speed_knots=0.0,
  )
  assert result == 0.0


def test_negative_form_factor_is_rejected():
  with pytest.raises(ValueError):
    calculate_viscous_resistance(6.0, 11.4, 30.0, -0.1)


def test_negative_viscous_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_total_resistance(-1.0, 0.0)


def test_negative_residual_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_total_resistance(0.0, -1.0)


def test_negative_appendage_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_total_resistance(0.0, 0.0, -1.0)


def test_negative_total_resistance_is_rejected():
  with pytest.raises(ValueError):
    calculate_effective_power_kw(-1.0, 6.0)


def test_negative_speed_for_effective_power_is_rejected():
  with pytest.raises(ValueError):
    calculate_effective_power_kw(1000.0, -1.0)
