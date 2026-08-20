"""Immutable normative hydrostatic profile models.

These models describe complete engineering data packages. Unknown hydrostatic
values are not defaulted: a vessel profile is instantiated only after every
required primitive has an explicit, traceable value.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileSource:
  method: str
  publication_or_dataset: str | None
  dataset_version: str | None = None
  model_or_table_identifiers: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodDomain:
  valid_froude_min: float
  valid_froude_max: float
  extrapolation_allowed: bool = False


@dataclass(frozen=True)
class CalibrationMetadata:
  version: str
  basis: str
  coefficient_definition: str
  wetted_surface_basis: str
  friction_line: str
  form_factor_treatment: str
  appendages_included: bool
  shallow_water_included: bool
  interference_included: bool


@dataclass(frozen=True)
class ExternalValidationMetadata:
  externally_validated: bool
  source: str | None = None
  version: str | None = None


@dataclass(frozen=True)
class ProfileProvenance:
  profile_id: str
  profile_version: str
  vessel_id: str
  assumption_status: str
  external_validation_status: str
  production_approved: bool
  hull_family: str
  parent_or_reference_hull: str | None
  loading_condition: str
  geometry_revision: str
  hydrostatics_revision: str
  source: ProfileSource
  method_domain: MethodDomain
  calibration: CalibrationMetadata
  validation: ExternalValidationMetadata
  known_limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormativeMonohullHydrostaticProfile:
  vessel_id: str
  profile_version: str
  loading_condition: str
  water_density_kg_m3: float
  loa_m: float
  lwl_m: float
  bwl_m: float
  draft_m: float
  displacement_mass_t: float
  displacement_volume_m3: float
  wetted_surface_area_m2: float
  prismatic_coefficient: float
  lcb_fraction_from_midship: float
  hull_family: str
  section_shape: str
  stern_type: str
  transom_immersed_at_rest: bool
  provenance: ProfileProvenance
  waterplane_coefficient: float | None = None
  lcf_fraction_from_midship: float | None = None
  immersed_transom_area_m2: float | None = None
  entrance_half_angle_deg: float | None = None

  def __post_init__(self):
    from calculations.hydrostatic_validation import validate_monohull_profile

    validate_monohull_profile(self)

  @property
  def block_coefficient(self) -> float:
    return self.displacement_volume_m3 / (
        self.lwl_m * self.bwl_m * self.draft_m
    )

  @property
  def midship_coefficient(self) -> float:
    return self.block_coefficient / self.prismatic_coefficient

  @property
  def length_displacement_ratio(self) -> float:
    return self.lwl_m / self.displacement_volume_m3 ** (1.0 / 3.0)

  @property
  def length_beam_ratio(self) -> float:
    return self.lwl_m / self.bwl_m

  @property
  def beam_draft_ratio(self) -> float:
    return self.bwl_m / self.draft_m


@dataclass(frozen=True)
class NormativeCatamaranHydrostaticProfile:
  vessel_id: str
  profile_version: str
  loading_condition: str
  water_density_kg_m3: float
  demi_hull_count: int
  symmetric_demi_hulls: bool
  equal_displacement_distribution: bool
  longitudinal_stagger_fraction: float
  wet_deck_immersed_at_rest: bool
  loa_m: float
  overall_beam_m: float
  hull_centerline_spacing_m: float
  demi_hull_lwl_m: float
  demi_hull_bwl_m: float
  draft_m: float
  total_displacement_mass_t: float
  total_displacement_volume_m3: float
  total_wetted_surface_area_m2: float
  demi_hull_wetted_surface_area_m2: float
  prismatic_coefficient: float
  demi_hull_lcb_fraction_from_midship: float
  hull_family: str
  section_shape: str
  stern_type: str
  transom_immersed_at_rest: bool
  provenance: ProfileProvenance
  wet_deck_clearance_m: float | None = None
  waterplane_coefficient: float | None = None
  entrance_half_angle_deg: float | None = None

  def __post_init__(self):
    from calculations.hydrostatic_validation import validate_catamaran_profile

    validate_catamaran_profile(self)

  @property
  def demi_hull_displacement_volume_m3(self) -> float:
    return self.total_displacement_volume_m3 / self.demi_hull_count

  @property
  def demi_hull_block_coefficient(self) -> float:
    return self.demi_hull_displacement_volume_m3 / (
        self.demi_hull_lwl_m * self.demi_hull_bwl_m * self.draft_m
    )

  @property
  def demi_hull_midship_coefficient(self) -> float:
    return self.demi_hull_block_coefficient / self.prismatic_coefficient

  @property
  def spacing_length_ratio(self) -> float:
    return self.hull_centerline_spacing_m / self.demi_hull_lwl_m

  @property
  def inner_waterline_clearance_m(self) -> float:
    return self.hull_centerline_spacing_m - self.demi_hull_bwl_m

  @property
  def demi_hull_length_displacement_ratio(self) -> float:
    return (
        self.demi_hull_lwl_m
        / self.demi_hull_displacement_volume_m3 ** (1.0 / 3.0)
    )

  @property
  def demi_hull_length_beam_ratio(self) -> float:
    return self.demi_hull_lwl_m / self.demi_hull_bwl_m

  @property
  def demi_hull_beam_draft_ratio(self) -> float:
    return self.demi_hull_bwl_m / self.draft_m
