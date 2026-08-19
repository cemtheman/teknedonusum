from dataclasses import FrozenInstanceError

import pytest

from models.geometry import (
    GeometryDataSource,
    GeometryValue,
    PreliminaryVesselGeometry,
)


def geometry_value(value, source=GeometryDataSource.PRELIMINARY_ASSUMPTION):
  return GeometryValue(value=value, source=source)


def sample_geometry(**overrides):
  # Test-fixture values only; these are not verified project geometry.
  values = {
      "loa_m": geometry_value(12.0, GeometryDataSource.PROJECT_CONFIG),
      "lwl_m": geometry_value(11.4),
      "beam_m": geometry_value(3.8),
      "draft_m": geometry_value(0.65),
      "displacement_t": geometry_value(9.22),
      "wetted_surface_area_m2": geometry_value(30.0),
  }
  values.update(overrides)
  return PreliminaryVesselGeometry(**values)


def test_geometry_data_source_values():
  assert GeometryDataSource.COMMISSION_CRITERION.value == "commission_criterion"
  assert GeometryDataSource.PROJECT_CONFIG.value == "project_config"
  assert GeometryDataSource.PRELIMINARY_ASSUMPTION.value == "preliminary_assumption"
  assert GeometryDataSource.CALCULATED.value == "calculated"


def test_geometry_value_accepts_finite_float():
  result = geometry_value(12.0)
  assert result.value == 12.0


def test_geometry_value_accepts_negative_finite_float():
  result = geometry_value(-1.0)
  assert result.value == -1.0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_geometry_value_rejects_non_finite_float(value):
  with pytest.raises(ValueError):
    geometry_value(value)


def test_geometry_value_is_frozen():
  result = geometry_value(12.0)
  with pytest.raises(FrozenInstanceError):
    result.value = 13.0


def test_valid_monohull_like_geometry():
  result = sample_geometry()
  assert result.loa_m.source is GeometryDataSource.PROJECT_CONFIG
  assert result.lwl_m.source is GeometryDataSource.PRELIMINARY_ASSUMPTION
  assert result.demi_hull_beam_m is None
  assert result.hull_centerline_spacing_m is None


def test_preliminary_vessel_geometry_is_frozen():
  result = sample_geometry()
  with pytest.raises(FrozenInstanceError):
    result.loa_m = geometry_value(13.0)


def test_lwl_greater_than_loa_is_rejected():
  with pytest.raises(ValueError):
    sample_geometry(lwl_m=geometry_value(12.1))


@pytest.mark.parametrize(
    "field_name",
    [
        "loa_m",
        "lwl_m",
        "beam_m",
        "draft_m",
        "displacement_t",
        "wetted_surface_area_m2",
    ],
)
@pytest.mark.parametrize("invalid_value", [0.0, -1.0])
def test_required_physical_field_must_be_positive(field_name, invalid_value):
  with pytest.raises(ValueError):
    sample_geometry(**{field_name: geometry_value(invalid_value)})


def test_optional_catamaran_fields_accept_none():
  result = sample_geometry(
      demi_hull_beam_m=None,
      hull_centerline_spacing_m=None,
  )
  assert result.demi_hull_beam_m is None
  assert result.hull_centerline_spacing_m is None


def test_optional_catamaran_fields_accept_positive_values():
  result = sample_geometry(
      demi_hull_beam_m=geometry_value(1.2),
      hull_centerline_spacing_m=geometry_value(3.0),
  )
  assert result.demi_hull_beam_m.value == 1.2
  assert result.hull_centerline_spacing_m.value == 3.0


@pytest.mark.parametrize(
    "field_name",
    ["demi_hull_beam_m", "hull_centerline_spacing_m"],
)
@pytest.mark.parametrize("invalid_value", [0.0, -1.0])
def test_optional_catamaran_field_must_be_positive_when_provided(
    field_name,
    invalid_value,
):
  with pytest.raises(ValueError):
    sample_geometry(**{field_name: geometry_value(invalid_value)})


@pytest.mark.parametrize(
    "field_name",
    ["demi_hull_beam_m", "hull_centerline_spacing_m"],
)
def test_optional_catamaran_fields_may_be_provided_independently(field_name):
  result = sample_geometry(**{field_name: geometry_value(1.0)})
  assert getattr(result, field_name).value == 1.0
