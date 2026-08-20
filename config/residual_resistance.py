"""Normative preliminary residual-resistance profiles for V1, V2, and V3.

The coefficients are explicit engineering assumptions for the v0.2 methodology
and are not verified model-test, CFD, designer, or sea-trial data. The profiles
are not connected to the production resistance/power chain yet.
"""

from models.residual_resistance import (
    ResidualResistanceAnchor,
    ResidualResistanceProfile,
)


def _anchors(*points):
  return tuple(
      ResidualResistanceAnchor(
          froude_number=froude_number,
          residual_resistance_coefficient=coefficient,
      )
      for froude_number, coefficient in points
  )


NORMATIVE_RESIDUAL_RESISTANCE_PROFILES = {
    "v1": ResidualResistanceProfile(
        vessel_id="v1",
        description="V1 12 m monohull normative preliminary profile",
        anchors=_anchors(
            (0.18, 0.016),
            (0.30, 0.030),
            (0.40, 0.050),
            (0.50, 0.080),
        ),
    ),
    "v2": ResidualResistanceProfile(
        vessel_id="v2",
        description="V2 13.5 m catamaran normative preliminary profile",
        anchors=_anchors(
            (0.18, 0.012),
            (0.30, 0.023),
            (0.40, 0.039),
            (0.50, 0.062),
        ),
    ),
    "v3": ResidualResistanceProfile(
        vessel_id="v3",
        description="V3 14 m catamaran normative preliminary profile",
        anchors=_anchors(
            (0.18, 0.014),
            (0.30, 0.026),
            (0.40, 0.043),
            (0.50, 0.068),
        ),
    ),
}
