from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from models.geometry import (
    GeometryDataSource,
    PreliminaryVesselGeometry,
)


GEOMETRY_FIELD_NAMES = (
    "loa_m",
    "lwl_m",
    "beam_m",
    "draft_m",
    "displacement_t",
    "wetted_surface_area_m2",
    "demi_hull_beam_m",
    "hull_centerline_spacing_m",
)


def all_geometry_values():
  for geometry in PRELIMINARY_VESSEL_GEOMETRY.values():
    for field_name in GEOMETRY_FIELD_NAMES:
      geometry_value = getattr(geometry, field_name)
      if geometry_value is not None:
        yield geometry_value


def test_geometry_mapping_key_order():
  assert list(PRELIMINARY_VESSEL_GEOMETRY) == ["v1", "v2", "v3"]


def test_all_geometry_entries_use_geometry_model():
  assert all(
      isinstance(geometry, PreliminaryVesselGeometry)
      for geometry in PRELIMINARY_VESSEL_GEOMETRY.values()
  )


def test_project_config_sources():
  for geometry in PRELIMINARY_VESSEL_GEOMETRY.values():
    assert geometry.loa_m.source is GeometryDataSource.PROJECT_CONFIG
    assert geometry.beam_m.source is GeometryDataSource.PROJECT_CONFIG


def test_preliminary_assumption_sources():
  for geometry in PRELIMINARY_VESSEL_GEOMETRY.values():
    assert geometry.lwl_m.source is GeometryDataSource.PRELIMINARY_ASSUMPTION
    assert geometry.draft_m.source is GeometryDataSource.PRELIMINARY_ASSUMPTION
    assert (
        geometry.displacement_t.source
        is GeometryDataSource.PRELIMINARY_ASSUMPTION
    )
    assert (
        geometry.wetted_surface_area_m2.source
        is GeometryDataSource.PRELIMINARY_ASSUMPTION
    )


def test_v1_geometry_values():
  geometry = PRELIMINARY_VESSEL_GEOMETRY["v1"]
  assert geometry.loa_m.value == 12.0
  assert geometry.lwl_m.value == 11.4
  assert geometry.beam_m.value == 3.8
  assert geometry.draft_m.value == 0.65
  assert geometry.displacement_t.value == 9.22
  assert geometry.wetted_surface_area_m2.value == 30.0
  assert geometry.demi_hull_beam_m is None
  assert geometry.hull_centerline_spacing_m is None


def test_v2_geometry_values_and_catamaran_sources():
  geometry = PRELIMINARY_VESSEL_GEOMETRY["v2"]
  assert geometry.loa_m.value == 13.5
  assert geometry.lwl_m.value == 12.8
  assert geometry.beam_m.value == 4.2
  assert geometry.draft_m.value == 0.60
  assert geometry.displacement_t.value == 11.36
  assert geometry.wetted_surface_area_m2.value == 34.0
  assert geometry.demi_hull_beam_m.value == 1.15
  assert geometry.hull_centerline_spacing_m.value == 3.05
  assert (
      geometry.demi_hull_beam_m.source
      is GeometryDataSource.PRELIMINARY_ASSUMPTION
  )
  assert (
      geometry.hull_centerline_spacing_m.source
      is GeometryDataSource.PRELIMINARY_ASSUMPTION
  )


def test_v3_geometry_values_and_catamaran_sources():
  geometry = PRELIMINARY_VESSEL_GEOMETRY["v3"]
  assert geometry.loa_m.value == 14.0
  assert geometry.lwl_m.value == 13.3
  assert geometry.beam_m.value == 4.5
  assert geometry.draft_m.value == 0.70
  assert geometry.displacement_t.value == 15.22
  assert geometry.wetted_surface_area_m2.value == 40.0
  assert geometry.demi_hull_beam_m.value == 1.25
  assert geometry.hull_centerline_spacing_m.value == 3.25
  assert (
      geometry.demi_hull_beam_m.source
      is GeometryDataSource.PRELIMINARY_ASSUMPTION
  )
  assert (
      geometry.hull_centerline_spacing_m.source
      is GeometryDataSource.PRELIMINARY_ASSUMPTION
  )


def test_no_commission_criterion_sources():
  count = sum(
      value.source is GeometryDataSource.COMMISSION_CRITERION
      for value in all_geometry_values()
  )
  assert count == 0


def test_no_calculated_sources():
  count = sum(
      value.source is GeometryDataSource.CALCULATED
      for value in all_geometry_values()
  )
  assert count == 0
