from dataclasses import FrozenInstanceError

import pytest

from calculations.cruise_power import calculate_cruise_power_envelope
from calculations.route_energy import (
    calculate_route_propulsion_energy_envelope,
)


def route(vessel_id, speed_knots, daily_distance_nm=35.0):
  cruise_power = calculate_cruise_power_envelope(
      vessel_id,
      speed_knots,
  )
  return calculate_route_propulsion_energy_envelope(
      cruise_power,
      daily_distance_nm,
  )


def test_result_is_immutable():
  result = route("v1", 6.0)

  with pytest.raises(FrozenInstanceError):
    result.daily_distance_nm = 40.0


@pytest.mark.parametrize(
    ("speed_knots", "expected_hours"),
    (
        (6.0, 35.0 / 6.0),
        (8.0, 35.0 / 8.0),
        (10.0, 35.0 / 10.0),
    ),
)
def test_route_duration_is_distance_divided_by_speed(
    speed_knots,
    expected_hours,
):
  result = route("v1", speed_knots)

  assert result.cruise_hours_per_day == pytest.approx(expected_hours)


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected_energy"),
    (
        ("v1", 6.0, 68.27214774060376),
        ("v1", 8.0, 132.31304356564246),
        ("v1", 10.0, 221.0526315789474),
        ("v2", 6.0, 93.07597813521893),
        ("v2", 8.0, 158.4799303412363),
        ("v2", 10.0, 239.4736842105263),
        ("v3", 6.0, 107.3953593867911),
        ("v3", 8.0, 182.86145808604186),
        ("v3", 10.0, 276.3157894736842),
    ),
)
def test_reference_route_energy(
    vessel_id,
    speed_knots,
    expected_energy,
):
  result = route(vessel_id, speed_knots)

  assert result.reference_daily_propulsion_energy_kwh == pytest.approx(
      expected_energy
  )


def test_v1_six_knot_sanity_check():
  result = route("v1", 6.0)

  assert result.cruise_hours_per_day == pytest.approx(5.833333333333333)
  assert result.reference_cruise_electrical_power_kw == pytest.approx(
      11.703796755532073
  )
  assert result.reference_daily_propulsion_energy_kwh == pytest.approx(
      68.27214774060376
  )


@pytest.mark.parametrize(
    "daily_distance_nm",
    (0.0, -1.0, float("nan"), float("inf")),
)
def test_invalid_daily_distance_is_rejected(daily_distance_nm):
  cruise_power = calculate_cruise_power_envelope("v1", 6.0)

  with pytest.raises(ValueError, match="daily_distance_nm"):
    calculate_route_propulsion_energy_envelope(
        cruise_power,
        daily_distance_nm,
    )