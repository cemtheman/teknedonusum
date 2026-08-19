from dataclasses import dataclass
from enum import Enum
from math import isfinite


class GeometryDataSource(str, Enum):
  COMMISSION_CRITERION = "commission_criterion"
  PROJECT_CONFIG = "project_config"
  PRELIMINARY_ASSUMPTION = "preliminary_assumption"
  CALCULATED = "calculated"


@dataclass(frozen=True)
class GeometryValue:
  value: float
  source: GeometryDataSource

  def __post_init__(self):
    if not isfinite(self.value):
      raise ValueError("geometry value must be finite")


@dataclass(frozen=True)
class PreliminaryVesselGeometry:
  loa_m: GeometryValue
  lwl_m: GeometryValue
  beam_m: GeometryValue
  draft_m: GeometryValue
  displacement_t: GeometryValue
  wetted_surface_area_m2: GeometryValue
  demi_hull_beam_m: GeometryValue | None = None
  hull_centerline_spacing_m: GeometryValue | None = None

  def __post_init__(self):
    required_positive_fields = (
        ("loa_m", self.loa_m),
        ("lwl_m", self.lwl_m),
        ("beam_m", self.beam_m),
        ("draft_m", self.draft_m),
        ("displacement_t", self.displacement_t),
        ("wetted_surface_area_m2", self.wetted_surface_area_m2),
    )
    for field_name, geometry_value in required_positive_fields:
      if geometry_value.value <= 0:
        raise ValueError(f"{field_name} must be positive")

    if self.lwl_m.value > self.loa_m.value:
      raise ValueError("lwl_m must not exceed loa_m")

    optional_positive_fields = (
        ("demi_hull_beam_m", self.demi_hull_beam_m),
        ("hull_centerline_spacing_m", self.hull_centerline_spacing_m),
    )
    for field_name, geometry_value in optional_positive_fields:
      if geometry_value is not None and geometry_value.value <= 0:
        raise ValueError(f"{field_name} must be positive when provided")
