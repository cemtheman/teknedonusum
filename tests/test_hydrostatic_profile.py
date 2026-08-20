from dataclasses import FrozenInstanceError, replace

import pytest

from config.normative_hydrostatic_profiles import (
    NORMATIVE_HYDROSTATIC_PROFILES,
    PENDING_NORMATIVE_HYDROSTATIC_PROFILE_IDS,
)
from models.hydrostatic_profile import (
    CalibrationMetadata,
    ExternalValidationMetadata,
    MethodDomain,
    NormativeCatamaranHydrostaticProfile,
    NormativeMonohullHydrostaticProfile,
    ProfileProvenance,
    ProfileSource,
)


def provenance(vessel_id="v1", profile_version="draft-1", hull_family="test"):
  return ProfileProvenance(
      profile_id=f"{vessel_id}-hydrostatics",
      profile_version=profile_version,
      vessel_id=vessel_id,
      assumption_status="normative_preliminary_assumption",
      external_validation_status="not_validated",
      production_approved=False,
      hull_family=hull_family,
      parent_or_reference_hull=None,
      loading_condition="design_load",
      geometry_revision="test-geometry-1",
      hydrostatics_revision="test-hydrostatics-1",
      source=ProfileSource(method="test_fixture", publication_or_dataset=None),
      method_domain=MethodDomain(0.18, 0.50, extrapolation_allowed=False),
      calibration=CalibrationMetadata(
          version="not_calibrated",
          basis="test_fixture",
          coefficient_definition="R_R / (0.5 rho V^2 S)",
          wetted_surface_basis="test_fixture",
          friction_line="ITTC-1957",
          form_factor_treatment="not_selected",
          appendages_included=False,
          shallow_water_included=False,
          interference_included=False,
      ),
      validation=ExternalValidationMetadata(externally_validated=False),
      known_limitations=("test fixture only",),
  )


def monohull(**changes):
  values = {
      "vessel_id": "v1",
      "profile_version": "draft-1",
      "loading_condition": "design_load",
      "water_density_kg_m3": 1000.0,
      "loa_m": 12.0,
      "lwl_m": 11.4,
      "bwl_m": 3.0,
      "draft_m": 0.8,
      "displacement_mass_t": 9.12,
      "displacement_volume_m3": 9.12,
      "wetted_surface_area_m2": 30.0,
      "prismatic_coefficient": 0.60,
      "lcb_fraction_from_midship": -0.03,
      "hull_family": "test",
      "section_shape": "round_bilge",
      "stern_type": "transom",
      "transom_immersed_at_rest": True,
      "provenance": provenance(),
  }
  values.update(changes)
  return NormativeMonohullHydrostaticProfile(**values)


def catamaran(**changes):
  values = {
      "vessel_id": "v2",
      "profile_version": "draft-1",
      "loading_condition": "design_load",
      "water_density_kg_m3": 1000.0,
      "demi_hull_count": 2,
      "symmetric_demi_hulls": True,
      "equal_displacement_distribution": True,
      "longitudinal_stagger_fraction": 0.0,
      "wet_deck_immersed_at_rest": False,
      "loa_m": 13.5,
      "overall_beam_m": 4.2,
      "hull_centerline_spacing_m": 3.0,
      "demi_hull_lwl_m": 12.8,
      "demi_hull_bwl_m": 1.0,
      "draft_m": 0.8,
      "total_displacement_mass_t": 10.24,
      "total_displacement_volume_m3": 10.24,
      "total_wetted_surface_area_m2": 34.0,
      "demi_hull_wetted_surface_area_m2": 17.0,
      "prismatic_coefficient": 0.60,
      "demi_hull_lcb_fraction_from_midship": -0.03,
      "hull_family": "test",
      "section_shape": "round_bilge",
      "stern_type": "transom",
      "transom_immersed_at_rest": True,
      "provenance": provenance(vessel_id="v2"),
  }
  values.update(changes)
  return NormativeCatamaranHydrostaticProfile(**values)


def test_valid_monohull_profile_is_immutable_and_derives_values():
  result = monohull()

  assert result.block_coefficient == pytest.approx(1.0 / 3.0)
  assert result.midship_coefficient == pytest.approx(5.0 / 9.0)
  assert result.length_displacement_ratio == pytest.approx(5.456404669)
  assert result.length_beam_ratio == pytest.approx(3.8)
  assert result.beam_draft_ratio == pytest.approx(3.75)
  with pytest.raises(FrozenInstanceError):
    result.bwl_m = 3.1


def test_valid_catamaran_profile_derives_values():
  result = catamaran()

  assert result.demi_hull_displacement_volume_m3 == pytest.approx(5.12)
  assert result.demi_hull_block_coefficient == pytest.approx(0.5)
  assert result.demi_hull_midship_coefficient == pytest.approx(5.0 / 6.0)
  assert result.spacing_length_ratio == pytest.approx(0.234375)
  assert result.inner_waterline_clearance_m == pytest.approx(2.0)
  assert result.demi_hull_length_displacement_ratio == pytest.approx(7.426542134)
  assert result.demi_hull_length_beam_ratio == pytest.approx(12.8)
  assert result.demi_hull_beam_draft_ratio == pytest.approx(1.25)


@pytest.mark.parametrize("coefficient", (0.0, -0.1, 1.01))
def test_invalid_prismatic_coefficient_is_rejected(coefficient):
  with pytest.raises(ValueError, match="prismatic_coefficient"):
    monohull(prismatic_coefficient=coefficient)


def test_impossible_block_and_midship_coefficients_are_rejected():
  with pytest.raises(ValueError, match="block coefficient"):
    monohull(displacement_mass_t=30.0, displacement_volume_m3=30.0)
  with pytest.raises(ValueError, match="midship coefficient"):
    monohull(prismatic_coefficient=0.30)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (("lwl_m", 0.0), ("bwl_m", -1.0), ("draft_m", 0.0)),
)
def test_non_positive_monohull_geometry_is_rejected(field_name, value):
  with pytest.raises(ValueError, match=field_name):
    monohull(**{field_name: value})


def test_displacement_mass_and_volume_must_be_consistent():
  assert monohull(displacement_volume_m3=9.120005).displacement_volume_m3 == (
      9.120005
  )
  with pytest.raises(ValueError, match="mass and volume"):
    monohull(displacement_volume_m3=9.0)


def test_catamaran_wetted_surface_must_match_dry_demi_hulls():
  with pytest.raises(ValueError, match="total wetted surface"):
    catamaran(total_wetted_surface_area_m2=35.0)


@pytest.mark.parametrize("spacing", (1.0, 0.9))
def test_catamaran_spacing_must_leave_inner_clearance(spacing):
  with pytest.raises(ValueError, match="spacing"):
    catamaran(hull_centerline_spacing_m=spacing)


@pytest.mark.parametrize(
    "changes",
    (
        {"demi_hull_count": 3},
        {"symmetric_demi_hulls": False},
        {"equal_displacement_distribution": False},
        {"longitudinal_stagger_fraction": 0.1},
    ),
)
def test_invalid_catamaran_topology_is_rejected(changes):
  with pytest.raises(ValueError):
    catamaran(**changes)


def test_provenance_is_immutable_and_must_match_profile():
  result = provenance()
  with pytest.raises(FrozenInstanceError):
    result.profile_version = "changed"
  with pytest.raises(ValueError, match="vessel_id"):
    monohull(provenance=replace(result, vessel_id="v2"))


def test_production_approval_requires_external_validation():
  invalid = replace(provenance(), production_approved=True)
  with pytest.raises(ValueError, match="external validation"):
    monohull(provenance=invalid)


def test_unknown_project_values_do_not_receive_fake_defaults():
  assert PENDING_NORMATIVE_HYDROSTATIC_PROFILE_IDS == ("v1", "v2", "v3")
  assert dict(NORMATIVE_HYDROSTATIC_PROFILES) == {}
  with pytest.raises(TypeError):
    NORMATIVE_HYDROSTATIC_PROFILES["v1"] = monohull()
