from dataclasses import (
  FrozenInstanceError,
  fields,
)

import pytest

from models.phase1_route_service_activity import (
  RouteServiceActivityPeriod,
)
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


def _activity(**overrides):
  values = {
    "service_activity_id": "RSA-2025-04",
    "journey_demand_id": "YD-2025-04",
    "route_id": "ROTA-DALYAN-IZTUZU",
    "total_vessel_round_trips": 2100,
    "input_basis": InputBasis.DECLARED,
    "verification_status": (
      VerificationStatus.REQUIRES_FIELD_VERIFICATION
    ),
    "source_note": (
      "Nisan 2025 rota toplamı sentetik hizmet faaliyeti."
    ),
  }
  values.update(overrides)
  return RouteServiceActivityPeriod(**values)


def test_activity_preserves_route_period_total():
  activity = _activity()

  assert activity.service_activity_id == "RSA-2025-04"
  assert activity.journey_demand_id == "YD-2025-04"
  assert activity.route_id == "ROTA-DALYAN-IZTUZU"
  assert activity.total_vessel_round_trips == 2100
  assert activity.input_basis is InputBasis.DECLARED
  assert (
    activity.verification_status
    is VerificationStatus.REQUIRES_FIELD_VERIFICATION
  )


def test_activity_is_frozen():
  activity = _activity()

  with pytest.raises(FrozenInstanceError):
    activity.total_vessel_round_trips = 2000


def test_activity_schema_is_strictly_route_aggregate():
  assert [
    field.name
    for field in fields(RouteServiceActivityPeriod)
  ] == [
    "service_activity_id",
    "journey_demand_id",
    "route_id",
    "total_vessel_round_trips",
    "input_basis",
    "verification_status",
    "source_note",
  ]


@pytest.mark.parametrize(
  "field_name",
  [
    "service_activity_id",
    "journey_demand_id",
    "route_id",
    "source_note",
  ],
)
def test_required_text_fields_cannot_be_blank(field_name):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı",
  ):
    _activity(**{field_name: " "})


@pytest.mark.parametrize(
  "invalid_value",
  [
    -1,
    1.5,
    True,
    "2100",
  ],
)
def test_total_vessel_round_trips_requires_non_negative_integer(
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match="total_vessel_round_trips alanı",
  ):
    _activity(total_vessel_round_trips=invalid_value)


def test_zero_round_trips_is_preserved_as_raw_observation():
  activity = _activity(total_vessel_round_trips=0)

  assert activity.total_vessel_round_trips == 0


def test_input_basis_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="InputBasis türünde",
  ):
    _activity(input_basis="declared")


def test_verification_status_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="VerificationStatus türünde",
  ):
    _activity(
      verification_status="requires_field_verification"
    )


def test_activity_schema_excludes_boat_capacity_and_decisions():
  field_names = {
    field.name
    for field in fields(RouteServiceActivityPeriod)
  }

  assert field_names.isdisjoint({
    "vessel_id",
    "cooperative_id",
    "passenger_capacity",
    "load_factor",
    "required_vessel_count",
    "capacity_sufficiency",
    "fleet_assignment",
    "energy_demand_kwh",
    "revenue_try",
    "optimization_result",
  })
