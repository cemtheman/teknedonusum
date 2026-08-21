from dataclasses import FrozenInstanceError

import pytest

from calculations.power_envelope import (
    interpolate_installed_mechanical_power_envelope,
)
from config.normative_power_envelopes import NORMATIVE_POWER_ENVELOPES
from models.power_envelope import NormativePowerEnvelope, PowerEnvelopeAnchor


EXPECTED_ANCHORS = {
    "v1": (
        (5.0, 20.0, 40.0),
        (6.0, 20.0, 40.0),
        (8.0, 30.0, 55.0),
        (10.0, 45.0, 75.0),
    ),
    "v2": (
        (5.0, 20.0, 40.0),
        (6.0, 20.0, 40.0),
        (8.0, 30.0, 55.0),
        (10.0, 50.0, 80.0),
    ),
    "v3": (
        (5.0, 25.0, 45.0),
        (6.0, 25.0, 45.0),
        (8.0, 40.0, 65.0),
        (10.0, 60.0, 90.0),
    ),
}


def profile(*points):
  anchors = tuple(PowerEnvelopeAnchor(*point) for point in points)
  return NormativePowerEnvelope(
      vessel_id="test",
      vessel_type="test vessel",
      profile_version="test",
      assumption_status="normative preliminary market envelope",
      provenance="test source basis",
      valid_speed_min_knots=anchors[0].speed_knots,
      valid_speed_max_knots=anchors[-1].speed_knots,
      extrapolation_allowed=False,
      anchors=anchors,
  )


def test_models_are_immutable():
  result = profile((6.0, 20.0, 40.0), (10.0, 45.0, 75.0))

  with pytest.raises(FrozenInstanceError):
    result.vessel_id = "changed"
  with pytest.raises(FrozenInstanceError):
    result.anchors[0].speed_knots = 7.0


@pytest.mark.parametrize("vessel_id", ("v1", "v2", "v3"))
@pytest.mark.parametrize("anchor_index", (0, 1, 2, 3))
def test_exact_normative_anchors(vessel_id, anchor_index):
  expected = EXPECTED_ANCHORS[vessel_id][anchor_index]
  anchor = NORMATIVE_POWER_ENVELOPES[vessel_id].anchors[anchor_index]
  result = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      expected[0],
  )

  assert (
      anchor.speed_knots,
      anchor.min_installed_mechanical_power_kw,
      anchor.max_installed_mechanical_power_kw,
  ) == expected
  assert result.min_installed_mechanical_power_kw == expected[1]
  assert result.max_installed_mechanical_power_kw == expected[2]


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "minimum", "maximum"),
    (
        ("v1", 5.5, 20.0, 40.0),
        ("v2", 5.5, 20.0, 40.0),
        ("v3", 5.5, 25.0, 45.0),
        ("v1", 7.0, 25.0, 47.5),
        ("v1", 9.0, 37.5, 65.0),
        ("v2", 7.0, 25.0, 47.5),
        ("v2", 9.0, 40.0, 67.5),
        ("v3", 7.0, 32.5, 55.0),
        ("v3", 9.0, 50.0, 77.5),
    ),
)
def test_linear_interpolation(vessel_id, speed_knots, minimum, maximum):
  result = interpolate_installed_mechanical_power_envelope(
      NORMATIVE_POWER_ENVELOPES[vessel_id],
      speed_knots,
  )

  assert result.min_installed_mechanical_power_kw == minimum
  assert result.max_installed_mechanical_power_kw == maximum
  assert (
      result.min_installed_mechanical_power_kw
      <= result.reference_installed_power_kw
      <= result.max_installed_mechanical_power_kw
  )


@pytest.mark.parametrize(
    "point",
    ((6.0, -1.0, 40.0), (6.0, 20.0, -1.0), (6.0, 41.0, 40.0)),
)
def test_anchor_rejects_invalid_power(point):
  with pytest.raises(ValueError):
    PowerEnvelopeAnchor(*point)


def test_profile_rejects_unordered_speeds():
  with pytest.raises(ValueError, match="strictly increasing"):
    profile((8.0, 30.0, 55.0), (6.0, 20.0, 40.0))


@pytest.mark.parametrize("speed_knots", (4.5, 11.0))
def test_interpolation_rejects_extrapolation(speed_knots):
  with pytest.raises(ValueError, match="within profile range"):
    interpolate_installed_mechanical_power_envelope(
        NORMATIVE_POWER_ENVELOPES["v1"],
        speed_knots,
    )


def test_registry_coverage_and_metadata():
  assert tuple(NORMATIVE_POWER_ENVELOPES) == ("v1", "v2", "v3")
  for vessel_id, result in NORMATIVE_POWER_ENVELOPES.items():
    assert result.vessel_id == vessel_id
    assert result.assumption_status == "normative preliminary market envelope"
    assert "not manufacturer-certified" in result.provenance
    assert result.profile_version == "v0.2-speed-floor-5"
    assert result.valid_speed_min_knots == 5.0
    assert result.valid_speed_max_knots == 10.0
    assert result.extrapolation_allowed is False
