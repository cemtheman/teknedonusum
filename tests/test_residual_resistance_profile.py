from dataclasses import FrozenInstanceError

import pytest

from calculations.residual_resistance import (
    calculate_profile_residual_resistance,
    interpolate_residual_resistance_coefficient,
)
from calculations.hydrodynamics import calculate_froude_number
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from config.residual_resistance import NORMATIVE_RESIDUAL_RESISTANCE_PROFILES
from models.residual_resistance import (
    ResidualResistanceAnchor,
    ResidualResistanceProfile,
)


def profile(*points):
  return ResidualResistanceProfile(
      vessel_id="test",
      description="test profile",
      anchors=tuple(ResidualResistanceAnchor(*point) for point in points),
  )


def test_profile_and_anchors_are_immutable():
  result = profile((0.2, 0.01), (0.4, 0.05))

  with pytest.raises(FrozenInstanceError):
    result.vessel_id = "changed"
  with pytest.raises(FrozenInstanceError):
    result.anchors[0].froude_number = 0.3


def test_profile_requires_two_strictly_increasing_anchors():
  with pytest.raises(ValueError, match="at least two"):
    profile((0.2, 0.01))
  with pytest.raises(ValueError, match="strictly increasing"):
    profile((0.2, 0.01), (0.2, 0.02))
  with pytest.raises(ValueError, match="strictly increasing"):
    profile((0.3, 0.01), (0.2, 0.02))


@pytest.mark.parametrize(
    ("point", "message"),
    (
        ((float("nan"), 0.01), "froude_number"),
        ((0.2, float("inf")), "residual_resistance_coefficient"),
        ((-0.1, 0.01), "froude_number"),
        ((0.2, -0.01), "residual_resistance_coefficient"),
    ),
)
def test_anchor_rejects_non_finite_and_negative_values(point, message):
  with pytest.raises(ValueError, match=message):
    ResidualResistanceAnchor(*point)


@pytest.mark.parametrize(
    ("froude_number", "coefficient"),
    ((0.2, 0.01), (0.3, 0.03), (0.4, 0.05)),
)
def test_coefficient_interpolates_anchors_and_midpoint(
    froude_number,
    coefficient,
):
  result = interpolate_residual_resistance_coefficient(
      profile((0.2, 0.01), (0.4, 0.05)),
      froude_number,
  )

  assert result == pytest.approx(coefficient)


@pytest.mark.parametrize("froude_number", (0.199, 0.401))
def test_coefficient_rejects_extrapolation(froude_number):
  with pytest.raises(ValueError, match="within profile range"):
    interpolate_residual_resistance_coefficient(
        profile((0.2, 0.01), (0.4, 0.05)),
        froude_number,
    )


@pytest.mark.parametrize("froude_number", (float("nan"), float("inf"), -0.1))
def test_coefficient_rejects_invalid_froude_number(froude_number):
  with pytest.raises(ValueError, match="finite and non-negative"):
    interpolate_residual_resistance_coefficient(
        profile((0.2, 0.01), (0.4, 0.05)),
        froude_number,
    )


def test_profile_force_uses_interpolated_coefficient():
  result = calculate_profile_residual_resistance(
      profile((0.2, 0.01), (0.4, 0.05)),
      speed_knots=6.0,
      waterline_length_m=10.794823069488563,
      wetted_surface_area_m2=30.0,
  )

  assert result == pytest.approx(4287.372592003199)


def test_zero_speed_guarantees_zero_without_extrapolation():
  result = calculate_profile_residual_resistance(
      profile((0.2, 0.01), (0.4, 0.05)),
      speed_knots=0.0,
      waterline_length_m=11.4,
      wetted_surface_area_m2=30.0,
  )

  assert result == 0.0


def test_normative_profiles_cover_v1_v2_v3():
  assert tuple(NORMATIVE_RESIDUAL_RESISTANCE_PROFILES) == ("v1", "v2", "v3")
  assert all(
      key == value.vessel_id
      for key, value in NORMATIVE_RESIDUAL_RESISTANCE_PROFILES.items()
  )


@pytest.mark.parametrize("speed_knots", (4.0, 10.0))
def test_normative_profiles_cover_configured_speed_limits(speed_knots):
  for vessel_id, profile_value in NORMATIVE_RESIDUAL_RESISTANCE_PROFILES.items():
    geometry = PRELIMINARY_VESSEL_GEOMETRY[vessel_id]
    froude_number = calculate_froude_number(
        speed_knots,
        geometry.lwl_m.value,
    )

    assert interpolate_residual_resistance_coefficient(
        profile_value,
        froude_number,
    ) >= 0
