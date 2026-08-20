import pytest

from calculations.battery_capacity_envelope import (
    calculate_route_based_battery_capacity_envelope,
)
from calculations.cruise_power import calculate_cruise_power_envelope
from calculations.route_energy import (
    calculate_route_propulsion_energy_envelope,
)


def battery(vessel_id, speed_knots, daily_distance_nm=35.0):
  cruise_power = calculate_cruise_power_envelope(
      vessel_id,
      speed_knots,
  )
  route_energy = calculate_route_propulsion_energy_envelope(
      cruise_power,
      daily_distance_nm,
  )
  return calculate_route_based_battery_capacity_envelope(route_energy)


def test_v1_six_knot_route_based_battery():
  result = battery("v1", 6.0)

  assert result.reference_daily_energy_kwh == pytest.approx(
      68.27214774060376
  )
  assert result.effective_usable_energy_fraction == pytest.approx(0.72)
  assert result.reference_nominal_battery_capacity_kwh == pytest.approx(
      68.27214774060376 / 0.72
  )


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots"),
    (
        ("v1", 6.0),
        ("v1", 8.0),
        ("v1", 10.0),
        ("v2", 6.0),
        ("v2", 8.0),
        ("v2", 10.0),
        ("v3", 6.0),
        ("v3", 8.0),
        ("v3", 10.0),
    ),
)
def test_route_based_capacity_exceeds_daily_energy(
    vessel_id,
    speed_knots,
):
  result = battery(vessel_id, speed_knots)

  assert result.reference_nominal_battery_capacity_kwh > (
      result.reference_daily_energy_kwh
  )
  assert result.reference_nominal_battery_capacity_kwh == pytest.approx(
      result.reference_daily_energy_kwh / 0.72
  )


def test_existing_battery_semantics_are_not_changed():
  result = battery("v1", 6.0)

  assert result.usable_soc_fraction == pytest.approx(0.90)
  assert result.reserve_fraction == pytest.approx(0.20)
  assert result.effective_usable_energy_fraction == pytest.approx(0.72)