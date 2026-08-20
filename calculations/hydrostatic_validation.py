"""Consistency validation for complete normative hydrostatic profiles."""

from math import isclose, isfinite


RELATIVE_TOLERANCE = 1.0e-6
ABSOLUTE_TOLERANCE = 1.0e-9


def _require_non_empty(field_name, value):
  if not isinstance(value, str) or not value.strip():
    raise ValueError(f"{field_name} must not be empty")


def _require_positive(field_name, value):
  if not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
    raise ValueError(f"{field_name} must be a positive finite number")


def _require_finite(field_name, value):
  if not isinstance(value, (int, float)) or not isfinite(value):
    raise ValueError(f"{field_name} must be finite")


def _require_fraction(field_name, value):
  if (
      not isinstance(value, (int, float))
      or not isfinite(value)
      or not 0 < value <= 1
  ):
    raise ValueError(f"{field_name} must be greater than zero and at most one")


def _require_bool(field_name, value):
  if not isinstance(value, bool):
    raise ValueError(f"{field_name} must be a boolean")


def _require_longitudinal_fraction(field_name, value):
  _require_finite(field_name, value)
  if not -0.5 <= value <= 0.5:
    raise ValueError(f"{field_name} must lie within the waterline length")


def _validate_provenance(profile):
  provenance = profile.provenance
  required_strings = {
      "profile_id": provenance.profile_id,
      "profile_version": provenance.profile_version,
      "vessel_id": provenance.vessel_id,
      "assumption_status": provenance.assumption_status,
      "external_validation_status": provenance.external_validation_status,
      "hull_family": provenance.hull_family,
      "loading_condition": provenance.loading_condition,
      "geometry_revision": provenance.geometry_revision,
      "hydrostatics_revision": provenance.hydrostatics_revision,
      "source.method": provenance.source.method,
      "calibration.version": provenance.calibration.version,
      "calibration.basis": provenance.calibration.basis,
      "calibration.coefficient_definition": (
          provenance.calibration.coefficient_definition
      ),
      "calibration.wetted_surface_basis": (
          provenance.calibration.wetted_surface_basis
      ),
      "calibration.friction_line": provenance.calibration.friction_line,
      "calibration.form_factor_treatment": (
          provenance.calibration.form_factor_treatment
      ),
  }
  for field_name, value in required_strings.items():
    _require_non_empty(field_name, value)

  if provenance.vessel_id != profile.vessel_id:
    raise ValueError("provenance vessel_id must match profile vessel_id")
  if provenance.profile_version != profile.profile_version:
    raise ValueError("provenance profile_version must match profile profile_version")
  if provenance.hull_family != profile.hull_family:
    raise ValueError("provenance hull_family must match profile hull_family")
  if provenance.loading_condition != profile.loading_condition:
    raise ValueError(
        "provenance loading_condition must match profile loading_condition"
    )

  domain = provenance.method_domain
  _require_finite("valid_froude_min", domain.valid_froude_min)
  _require_positive("valid_froude_max", domain.valid_froude_max)
  if domain.valid_froude_min < 0:
    raise ValueError("valid_froude_min must be non-negative")
  if domain.valid_froude_min >= domain.valid_froude_max:
    raise ValueError("valid Froude range must be strictly increasing")
  _require_bool("production_approved", provenance.production_approved)
  _require_bool(
      "externally_validated",
      provenance.validation.externally_validated,
  )
  if provenance.production_approved and not provenance.validation.externally_validated:
    raise ValueError("production approval requires external validation")


def _validate_common(profile, geometry_fields, mass_field, volume_field, area_fields):
  required_strings = {
      "vessel_id": profile.vessel_id,
      "profile_version": profile.profile_version,
      "loading_condition": profile.loading_condition,
      "hull_family": profile.hull_family,
      "section_shape": profile.section_shape,
      "stern_type": profile.stern_type,
  }
  for field_name, value in required_strings.items():
    _require_non_empty(field_name, value)

  _require_positive("water_density_kg_m3", profile.water_density_kg_m3)
  for field_name in geometry_fields:
    _require_positive(field_name, getattr(profile, field_name))
  _require_positive(mass_field, getattr(profile, mass_field))
  _require_positive(volume_field, getattr(profile, volume_field))
  for field_name in area_fields:
    _require_positive(field_name, getattr(profile, field_name))
  _require_fraction("prismatic_coefficient", profile.prismatic_coefficient)

  expected_volume = (
      getattr(profile, mass_field) * 1000.0 / profile.water_density_kg_m3
  )
  if not isclose(
      getattr(profile, volume_field),
      expected_volume,
      rel_tol=RELATIVE_TOLERANCE,
      abs_tol=ABSOLUTE_TOLERANCE,
  ):
    raise ValueError("displacement mass and volume are inconsistent")

  _validate_provenance(profile)


def _validate_coefficients(block_coefficient, midship_coefficient, prismatic):
  if not 0 < block_coefficient <= 1:
    raise ValueError(
        "derived block coefficient must be greater than zero and at most one"
    )
  if not 0 < midship_coefficient <= 1:
    raise ValueError(
        "derived midship coefficient must be greater than zero and at most one"
    )
  if block_coefficient > prismatic + ABSOLUTE_TOLERANCE:
    raise ValueError("derived block coefficient must not exceed prismatic coefficient")


def _validate_optional_characterization(profile, field_names):
  for field_name in field_names:
    value = getattr(profile, field_name)
    if value is not None:
      if field_name == "waterplane_coefficient":
        _require_fraction(field_name, value)
      else:
        _require_positive(field_name, value)


def validate_monohull_profile(profile):
  _validate_common(
      profile,
      geometry_fields=("loa_m", "lwl_m", "bwl_m", "draft_m"),
      mass_field="displacement_mass_t",
      volume_field="displacement_volume_m3",
      area_fields=("wetted_surface_area_m2",),
  )
  if profile.lwl_m > profile.loa_m:
    raise ValueError("lwl_m must not exceed loa_m")
  _require_bool("transom_immersed_at_rest", profile.transom_immersed_at_rest)
  _require_longitudinal_fraction(
      "lcb_fraction_from_midship",
      profile.lcb_fraction_from_midship,
  )
  if profile.lcf_fraction_from_midship is not None:
    _require_longitudinal_fraction(
        "lcf_fraction_from_midship",
        profile.lcf_fraction_from_midship,
    )
  _validate_optional_characterization(
      profile,
      (
          "waterplane_coefficient",
          "immersed_transom_area_m2",
          "entrance_half_angle_deg",
      ),
  )
  _validate_coefficients(
      profile.block_coefficient,
      profile.midship_coefficient,
      profile.prismatic_coefficient,
  )


def validate_catamaran_profile(profile):
  _validate_common(
      profile,
      geometry_fields=(
          "loa_m",
          "overall_beam_m",
          "hull_centerline_spacing_m",
          "demi_hull_lwl_m",
          "demi_hull_bwl_m",
          "draft_m",
      ),
      mass_field="total_displacement_mass_t",
      volume_field="total_displacement_volume_m3",
      area_fields=(
          "total_wetted_surface_area_m2",
          "demi_hull_wetted_surface_area_m2",
      ),
  )
  if not isinstance(profile.demi_hull_count, int) or profile.demi_hull_count != 2:
    raise ValueError("demi_hull_count must equal two")
  if profile.symmetric_demi_hulls is not True:
    raise ValueError("demi-hulls must be symmetric")
  if profile.equal_displacement_distribution is not True:
    raise ValueError("demi-hulls must have equal displacement distribution")
  _require_bool("wet_deck_immersed_at_rest", profile.wet_deck_immersed_at_rest)
  _require_bool("transom_immersed_at_rest", profile.transom_immersed_at_rest)
  _require_finite(
      "longitudinal_stagger_fraction",
      profile.longitudinal_stagger_fraction,
  )
  if profile.longitudinal_stagger_fraction != 0:
    raise ValueError("longitudinal_stagger_fraction must be zero")
  if profile.demi_hull_lwl_m > profile.loa_m:
    raise ValueError("demi_hull_lwl_m must not exceed loa_m")
  _require_longitudinal_fraction(
      "demi_hull_lcb_fraction_from_midship",
      profile.demi_hull_lcb_fraction_from_midship,
  )
  _validate_optional_characterization(
      profile,
      (
          "wet_deck_clearance_m",
          "waterplane_coefficient",
          "entrance_half_angle_deg",
      ),
  )

  if profile.hull_centerline_spacing_m <= profile.demi_hull_bwl_m:
    raise ValueError("hull centerline spacing must exceed demi-hull BWL")
  if profile.overall_beam_m + ABSOLUTE_TOLERANCE < (
      profile.hull_centerline_spacing_m + profile.demi_hull_bwl_m
  ):
    raise ValueError("overall beam contradicts demi-hull beam and spacing")
  if not profile.wet_deck_immersed_at_rest and not isclose(
      profile.total_wetted_surface_area_m2,
      2.0 * profile.demi_hull_wetted_surface_area_m2,
      rel_tol=RELATIVE_TOLERANCE,
      abs_tol=ABSOLUTE_TOLERANCE,
  ):
    raise ValueError(
        "dry wet-deck requires total wetted surface to equal two demi-hulls"
    )
  if profile.wet_deck_immersed_at_rest and profile.total_wetted_surface_area_m2 < (
      2.0 * profile.demi_hull_wetted_surface_area_m2 - ABSOLUTE_TOLERANCE
  ):
    raise ValueError(
        "immersed wet-deck total wetted surface cannot be below demi-hull sum"
    )

  expected_total_volume = profile.demi_hull_displacement_volume_m3 * 2.0
  if not isclose(
      profile.total_displacement_volume_m3,
      expected_total_volume,
      rel_tol=RELATIVE_TOLERANCE,
      abs_tol=ABSOLUTE_TOLERANCE,
  ):
    raise ValueError("total displacement volume must equal two demi-hull volumes")
  _validate_coefficients(
      profile.demi_hull_block_coefficient,
      profile.demi_hull_midship_coefficient,
      profile.prismatic_coefficient,
  )
