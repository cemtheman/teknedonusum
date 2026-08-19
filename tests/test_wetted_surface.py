import pytest

from calculations.resistance_sensitivity import calculate_resistance_sensitivity
from calculations.wetted_surface import (
    CATAMARAN_CROSS_CHECK_ONLY,
    MONOHULL_PRELIMINARY_CHECK,
    check_wetted_surface_sanity,
    estimate_preliminary_wetted_surface_area_m2,
)
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY


def test_v1_preliminary_wetted_surface_estimate():
  result = check_wetted_surface_sanity(PRELIMINARY_VESSEL_GEOMETRY["v1"])

  assert result.assumed_wetted_surface_area_m2 == 30.0
  assert result.estimated_wetted_surface_area_m2 == pytest.approx(
      27.451155769230766
  )
  assert result.hull_type == "monohull"
  assert result.applicability == MONOHULL_PRELIMINARY_CHECK


def test_relative_difference_uses_assumed_area_as_reference():
  result = check_wetted_surface_sanity(PRELIMINARY_VESSEL_GEOMETRY["v1"])

  assert result.relative_difference_fraction == pytest.approx(
      abs(27.451155769230766 - 30.0) / 30.0
  )


@pytest.mark.parametrize(
    ("lwl_m", "draft_m", "displacement_t"),
    [
        (0.0, 0.65, 9.22),
        (11.4, 0.0, 9.22),
        (11.4, 0.65, 0.0),
        (-11.4, 0.65, 9.22),
        (float("nan"), 0.65, 9.22),
    ],
)
def test_invalid_estimator_geometry_is_rejected(
    lwl_m,
    draft_m,
    displacement_t,
):
  with pytest.raises(ValueError):
    estimate_preliminary_wetted_surface_area_m2(
        lwl_m,
        draft_m,
        displacement_t,
    )


@pytest.mark.parametrize("vessel_id", ["v2", "v3"])
def test_catamaran_estimate_is_cross_check_only(vessel_id):
  result = check_wetted_surface_sanity(
      PRELIMINARY_VESSEL_GEOMETRY[vessel_id]
  )

  assert result.hull_type == "catamaran"
  assert result.applicability == CATAMARAN_CROSS_CHECK_ONLY


def test_resistance_baseline_still_uses_assumed_wetted_surface():
  geometry = PRELIMINARY_VESSEL_GEOMETRY["v1"]
  sanity = check_wetted_surface_sanity(geometry)
  resistance = calculate_resistance_sensitivity(
      geometry=geometry,
      speed_knots=10.0,
      form_factor=0.15,
      residual_resistance_n=1500.0,
      appendage_resistance_n=100.0,
  )

  assert sanity.estimated_wetted_surface_area_m2 != 30.0
  assert geometry.wetted_surface_area_m2.value == 30.0
  assert resistance.frictional_resistance_n == pytest.approx(
      894.8322878011685
  )
  assert resistance.viscous_resistance_n == pytest.approx(
      1029.0571309713437
  )
  assert resistance.total_resistance_n == pytest.approx(
      2629.0571309713437
  )
  assert resistance.effective_power_kw == pytest.approx(13.52502666685422)
