"""Normative preliminary market-power envelopes for V1, V2, and V3.

These bands are preliminary market sanity-check assumptions. They are not
manufacturer-certified performance curves, sea-trial data, or hydrodynamically
validated power requirements, and they are not connected to the production
power chain.
"""

from types import MappingProxyType

from models.power_envelope import NormativePowerEnvelope, PowerEnvelopeAnchor


ASSUMPTION_STATUS = "normative preliminary market envelope"
SOURCE_BASIS = (
    "Preliminary market sanity-check bands; not manufacturer-certified, "
    "sea-trial, or hydrodynamically validated data"
)


def _profile(vessel_id, vessel_type, *points):
  anchors = tuple(PowerEnvelopeAnchor(*point) for point in points)
  return NormativePowerEnvelope(
      vessel_id=vessel_id,
      vessel_type=vessel_type,
      profile_version="v0.2-speed-floor-5",
      assumption_status=ASSUMPTION_STATUS,
      provenance=SOURCE_BASIS,
      valid_speed_min_knots=anchors[0].speed_knots,
      valid_speed_max_knots=anchors[-1].speed_knots,
      extrapolation_allowed=False,
      anchors=anchors,
  )


# The 5-kn anchor deliberately preserves the existing 6-kn installed-power
# floor. It extends the supported operating domain without reducing the
# installed motor envelope.
NORMATIVE_POWER_ENVELOPES = MappingProxyType({
    "v1": _profile(
        "v1",
        "12 m monohull",
        (5.0, 20.0, 40.0),
        (6.0, 20.0, 40.0),
        (8.0, 30.0, 55.0),
        (10.0, 45.0, 75.0),
    ),
    "v2": _profile(
        "v2",
        "13.5 m narrow catamaran",
        (5.0, 20.0, 40.0),
        (6.0, 20.0, 40.0),
        (8.0, 30.0, 55.0),
        (10.0, 50.0, 80.0),
    ),
    "v3": _profile(
        "v3",
        "14 m narrow catamaran",
        (5.0, 25.0, 45.0),
        (6.0, 25.0, 45.0),
        (8.0, 40.0, 65.0),
        (10.0, 60.0, 90.0),
    ),
})
