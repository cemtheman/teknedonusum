from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime

import pytest

from models.phase1_journey_demand import JourneyDemandPeriod
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


def _journey_demand(**overrides):
  values = {
    "journey_demand_id": "YD-2025-05",
    "period_label": "Mayıs 2025",
    "route_id": "ROTA-DALYAN-IZTUZU",
    "route_name": "Dalyan–İztuzu",
    "period_start": date(2025, 5, 1),
    "period_end": date(2025, 5, 31),
    "round_trip_passenger_demand": 65000,
    "peak_factor": 1.35,
    "input_basis": InputBasis.ASSUMED,
    "verification_status": VerificationStatus.SYNTHETIC,
  }
  values.update(overrides)
  return JourneyDemandPeriod(**values)


def test_journey_demand_preserves_mockup_inputs():
  demand = _journey_demand()

  assert demand.journey_demand_id == "YD-2025-05"
  assert demand.route_id == "ROTA-DALYAN-IZTUZU"
  assert demand.period_start == date(2025, 5, 1)
  assert demand.period_end == date(2025, 5, 31)
  assert demand.round_trip_passenger_demand == 65000
  assert demand.peak_factor == 1.35
  assert demand.input_basis is InputBasis.ASSUMED
  assert demand.verification_status is VerificationStatus.SYNTHETIC


def test_journey_demand_derives_excel_values_from_raw_inputs():
  demand = _journey_demand()

  assert demand.service_days == 31
  assert demand.passenger_leg_demand == 130000
  assert demand.average_daily_round_trip == pytest.approx(
    2096.7741935483873
  )
  assert demand.peak_daily_round_trip == 2831


def test_journey_demand_is_frozen():
  demand = _journey_demand()

  with pytest.raises(FrozenInstanceError):
    demand.peak_factor = 1.4


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("period_start", "2025-05-01"),
    ("period_end", "2025-05-31"),
    ("period_start", datetime(2025, 5, 1, 0, 0)),
    ("period_end", datetime(2025, 5, 31, 0, 0)),
  ],
)
def test_period_boundaries_require_date_only(
  field_name,
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı",
  ):
    _journey_demand(**{field_name: invalid_value})


def test_period_end_cannot_precede_period_start():
  with pytest.raises(
    ValueError,
    match="period_end alanı period_start",
  ):
    _journey_demand(
      period_start=date(2025, 5, 2),
      period_end=date(2025, 5, 1),
    )


@pytest.mark.parametrize(
  "field_name",
  [
    "journey_demand_id",
    "period_label",
    "route_id",
    "route_name",
  ],
)
def test_required_text_fields_cannot_be_blank(field_name):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı",
  ):
    _journey_demand(**{field_name: " "})


@pytest.mark.parametrize(
  "invalid_value",
  [
    -1,
    65000.0,
    True,
    "65000",
  ],
)
def test_round_trip_passenger_demand_requires_non_negative_integer(
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match="round_trip_passenger_demand alanı",
  ):
    _journey_demand(
      round_trip_passenger_demand=invalid_value
    )


@pytest.mark.parametrize(
  "invalid_value",
  [
    0.99,
    0,
    float("nan"),
    float("inf"),
    True,
    "1.35",
  ],
)
def test_peak_factor_requires_finite_number_at_least_one(
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match="peak_factor alanı",
  ):
    _journey_demand(peak_factor=invalid_value)


def test_input_basis_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="InputBasis türünde",
  ):
    _journey_demand(input_basis="assumed")


def test_verification_status_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="VerificationStatus türünde",
  ):
    _journey_demand(verification_status="synthetic")


def test_schema_excludes_assignment_energy_revenue_and_decisions():
  field_names = {
    field.name
    for field in fields(JourneyDemandPeriod)
  }

  forbidden_fields = {
    "vessel_id",
    "vessel_count",
    "trip_count",
    "boat_transport_share",
    "energy_demand_kwh",
    "supply_point_id",
    "road_vehicle_entry_fee_try",
    "parking_revenue_try",
    "conversion_priority",
    "optimization_result",
  }

  assert field_names.isdisjoint(forbidden_fields)
