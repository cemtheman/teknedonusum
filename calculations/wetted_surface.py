"""Preliminary wetted-surface geometry sanity checks.

The estimator in this module is only a preliminary geometry sanity check. It is
not a hydrostatic or lines-plan-derived wetted surface and must be replaced when
actual hydrostatics, designer data, model tests, or CFD results become available.
In particular, the estimate is not an authoritative prediction for catamarans.
"""

from dataclasses import dataclass
from math import isfinite

from calculations.hydrodynamics import WATER_DENSITY_KG_M3
from models.geometry import PreliminaryVesselGeometry


MONOHULL_PRELIMINARY_CHECK = "preliminary_monohull_sanity_check"
CATAMARAN_CROSS_CHECK_ONLY = "cross_check_only"


@dataclass(frozen=True)
class WettedSurfaceSanityResult:
  """Comparison of an assumed wetted area with a preliminary estimate."""

  assumed_wetted_surface_area_m2: float
  estimated_wetted_surface_area_m2: float
  relative_difference_fraction: float
  hull_type: str
  applicability: str


def estimate_preliminary_wetted_surface_area_m2(
    lwl_m: float,
    draft_m: float,
    displacement_t: float,
) -> float:
  """Estimate monohull wetted area for a preliminary geometry sanity check.

  This Denny-Mumford-style estimate is not derived from hydrostatics or a lines
  plan. Replace it with actual hydrostatics, designer data, or CFD when those
  sources become available.
  """
  inputs = {
      "lwl_m": lwl_m,
      "draft_m": draft_m,
      "displacement_t": displacement_t,
  }
  for field_name, value in inputs.items():
    if not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
      raise ValueError(f"{field_name} must be a positive finite number")

  displacement_volume_m3 = (
      displacement_t * 1000.0 / WATER_DENSITY_KG_M3
  )
  return 1.025 * (
      1.7 * lwl_m * draft_m + displacement_volume_m3 / draft_m
  )


def check_wetted_surface_sanity(
    geometry: PreliminaryVesselGeometry,
) -> WettedSurfaceSanityResult:
  """Compare the configured assumption with the preliminary area estimate.

  Catamaran geometry is explicitly returned as ``cross_check_only`` because the
  estimator is not applicable as an authoritative multihull prediction. The
  configured assumed area remains the resistance-model input in every case.
  """
  if not isinstance(geometry, PreliminaryVesselGeometry):
    raise TypeError("geometry must be a PreliminaryVesselGeometry")

  assumed_area_m2 = geometry.wetted_surface_area_m2.value
  estimated_area_m2 = estimate_preliminary_wetted_surface_area_m2(
      lwl_m=geometry.lwl_m.value,
      draft_m=geometry.draft_m.value,
      displacement_t=geometry.displacement_t.value,
  )
  is_catamaran = geometry.demi_hull_beam_m is not None

  return WettedSurfaceSanityResult(
      assumed_wetted_surface_area_m2=assumed_area_m2,
      estimated_wetted_surface_area_m2=estimated_area_m2,
      relative_difference_fraction=(
          abs(estimated_area_m2 - assumed_area_m2) / assumed_area_m2
      ),
      hull_type="catamaran" if is_catamaran else "monohull",
      applicability=(
          CATAMARAN_CROSS_CHECK_ONLY
          if is_catamaran
          else MONOHULL_PRELIMINARY_CHECK
      ),
  )
