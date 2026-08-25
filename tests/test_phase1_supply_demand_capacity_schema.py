from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from models.phase1_supply_demand_capacity import (
  AvailabilityBasis,
  CapacitySnapshot,
  EnergyDemandResult,
  InputBasis,
  OperationalDemandInput,
  SupplyAvailabilityProfile,
  SupplyPoint,
)


START = datetime(2026, 8, 25, 8, 0, tzinfo=timezone.utc)
END = START + timedelta(hours=4)


def _valid_demand(**overrides):
  values = {
    "demand_input_id": "demand-001",
    "vessel_id": "MCK-0001",
    "measurement_date": START.date(),
    "service_speed_kn": 6.0,
    "route_distance_nm_day": 35.0,
    "service_hours_day": 8.0,
    "operating_days_year": 180,
    "installed_mechanical_power_kw": 22.0,
    "auxiliary_energy_kwh_day": 4.5,
    "reserve_fraction": 0.20,
    "input_basis": InputBasis.DECLARED,
    "valid_from": START,
    "valid_to": None,
  }
  values.update(overrides)
  return OperationalDemandInput(**values)


def _valid_supply_point(**overrides):
  values = {
    "supply_point_id": "supply-001",
    "site_name": "Dalyan İskele Alanı",
    "latitude": 36.8340,
    "longitude": 28.6440,
    "connection_type": "Saha doğrulaması gerekli",
    "operational_status": "Planlanan",
    "operator_name": "Muğla Büyükşehir Belediyesi",
    "field_verified_at": None,
  }
  values.update(overrides)
  return SupplyPoint(**values)


def _valid_supply_profile(**overrides):
  values = {
    "supply_profile_id": "profile-001",
    "supply_point_id": "supply-001",
    "interval_start": START,
    "interval_end": END,
    "available_power_kw": 120.0,
    "energy_limit_kwh": None,
    "availability_basis": AvailabilityBasis.ESTIMATED,
    "valid_from": START,
    "valid_to": None,
  }
  values.update(overrides)
  return SupplyAvailabilityProfile(**values)


def _valid_capacity_snapshot(**overrides):
  values = {
    "capacity_snapshot_id": "capacity-001",
    "supply_point_id": "supply-001",
    "observed_at": START,
    "contracted_power_kw": 150.0,
    "transformer_power_kva": 250.0,
    "firm_capacity_kw": 120.0,
    "reserved_capacity_kw": 35.0,
    "simultaneous_unit_limit": None,
    "source_document": "Sentetik kapasite kaydı",
  }
  values.update(overrides)
  return CapacitySnapshot(**values)


def test_operational_demand_input_accepts_valid_phase1_values():
  demand = _valid_demand()

  assert demand.vessel_id == "MCK-0001"
  assert demand.service_speed_kn == pytest.approx(6.0)
  assert demand.route_distance_nm_day == pytest.approx(35.0)
  assert demand.input_basis is InputBasis.DECLARED


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("service_speed_kn", 0.0),
    ("route_distance_nm_day", -0.1),
    ("service_hours_day", -0.1),
    ("service_hours_day", 24.1),
    ("operating_days_year", -1),
    ("operating_days_year", 367),
    ("installed_mechanical_power_kw", 0.0),
    ("auxiliary_energy_kwh_day", -0.1),
    ("reserve_fraction", -0.01),
    ("reserve_fraction", 1.01),
  ],
)
def test_operational_demand_input_rejects_invalid_numeric_values(
  field_name,
  invalid_value,
):
  with pytest.raises(ValueError):
    _valid_demand(**{field_name: invalid_value})


@pytest.mark.parametrize(
  "field_name",
  [
    "demand_input_id",
    "vessel_id",
  ],
)
def test_operational_demand_input_rejects_blank_identifiers(field_name):
  with pytest.raises(ValueError):
    _valid_demand(**{field_name: "  "})


def test_operational_demand_input_requires_enum_input_basis():
  with pytest.raises(ValueError):
    _valid_demand(input_basis="declared")


def test_operational_demand_input_requires_timezone_aware_validity():
  with pytest.raises(ValueError):
    _valid_demand(valid_from=datetime(2026, 8, 25, 8, 0))


def test_operational_demand_input_rejects_invalid_validity_interval():
  with pytest.raises(ValueError):
    _valid_demand(
      valid_from=END,
      valid_to=START,
    )


def test_energy_demand_result_keeps_calculated_values_separate():
  result = EnergyDemandResult(
    demand_result_id="result-001",
    demand_input_id="demand-001",
    methodology_version="v0.2",
    propulsion_energy_kwh_day=72.0,
    total_energy_kwh_day=91.8,
    peak_power_kw=22.0,
    annual_energy_kwh=16524.0,
    calculated_at=START,
  )

  assert result.demand_input_id == "demand-001"
  assert result.methodology_version == "v0.2"
  assert result.total_energy_kwh_day == pytest.approx(91.8)


@pytest.mark.parametrize(
  "field_name",
  [
    "propulsion_energy_kwh_day",
    "total_energy_kwh_day",
    "peak_power_kw",
    "annual_energy_kwh",
  ],
)
def test_energy_demand_result_rejects_negative_values(field_name):
  values = {
    "demand_result_id": "result-001",
    "demand_input_id": "demand-001",
    "methodology_version": "v0.2",
    "propulsion_energy_kwh_day": 72.0,
    "total_energy_kwh_day": 91.8,
    "peak_power_kw": 22.0,
    "annual_energy_kwh": 16524.0,
    "calculated_at": START,
  }
  values[field_name] = -0.1

  with pytest.raises(ValueError):
    EnergyDemandResult(**values)


def test_energy_demand_result_cannot_be_lower_than_propulsion_energy():
  with pytest.raises(ValueError):
    EnergyDemandResult(
      demand_result_id="result-001",
      demand_input_id="demand-001",
      methodology_version="v0.2",
      propulsion_energy_kwh_day=72.0,
      total_energy_kwh_day=71.9,
      peak_power_kw=22.0,
      annual_energy_kwh=12942.0,
      calculated_at=START,
    )


def test_supply_point_accepts_valid_location_data():
  point = _valid_supply_point()

  assert point.supply_point_id == "supply-001"
  assert point.latitude == pytest.approx(36.8340)
  assert point.longitude == pytest.approx(28.6440)


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("latitude", -90.1),
    ("latitude", 90.1),
    ("longitude", -180.1),
    ("longitude", 180.1),
  ],
)
def test_supply_point_rejects_invalid_coordinates(
  field_name,
  invalid_value,
):
  with pytest.raises(ValueError):
    _valid_supply_point(**{field_name: invalid_value})


@pytest.mark.parametrize(
  "field_name",
  [
    "supply_point_id",
    "site_name",
    "connection_type",
    "operational_status",
    "operator_name",
  ],
)
def test_supply_point_rejects_blank_required_text(field_name):
  with pytest.raises(ValueError):
    _valid_supply_point(**{field_name: "  "})


def test_supply_availability_profile_accepts_nullable_energy_limit():
  profile = _valid_supply_profile()

  assert profile.energy_limit_kwh is None
  assert profile.available_power_kw == pytest.approx(120.0)


def test_supply_availability_profile_requires_positive_optional_energy_limit():
  with pytest.raises(ValueError):
    _valid_supply_profile(energy_limit_kwh=0.0)


def test_supply_availability_profile_rejects_reversed_interval():
  with pytest.raises(ValueError):
    _valid_supply_profile(
      interval_start=END,
      interval_end=START,
    )


def test_supply_availability_profile_requires_enum_basis():
  with pytest.raises(ValueError):
    _valid_supply_profile(availability_basis="estimated")


def test_capacity_snapshot_calculates_usable_capacity():
  snapshot = _valid_capacity_snapshot()

  assert snapshot.usable_capacity_kw == pytest.approx(85.0)


def test_capacity_snapshot_rejects_reserved_capacity_above_firm_capacity():
  with pytest.raises(ValueError):
    _valid_capacity_snapshot(
      firm_capacity_kw=120.0,
      reserved_capacity_kw=120.1,
    )


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("contracted_power_kw", -0.1),
    ("transformer_power_kva", -0.1),
    ("firm_capacity_kw", -0.1),
    ("reserved_capacity_kw", -0.1),
    ("simultaneous_unit_limit", -1),
  ],
)
def test_capacity_snapshot_rejects_negative_values(
  field_name,
  invalid_value,
):
  with pytest.raises(ValueError):
    _valid_capacity_snapshot(**{field_name: invalid_value})


def test_phase1_schema_records_are_immutable():
  demand = _valid_demand()

  with pytest.raises(FrozenInstanceError):
    demand.service_speed_kn = 7.0


def test_phase1_schema_contains_no_decision_or_ranking_fields():
  forbidden_fields = {
    "priority",
    "rank",
    "score",
    "sequence",
    "assigned_unit",
    "assigned_supply_point",
  }

  for model in (
    OperationalDemandInput,
    EnergyDemandResult,
    SupplyPoint,
    SupplyAvailabilityProfile,
    CapacitySnapshot,
  ):
    model_fields = {field.name for field in fields(model)}
    assert model_fields.isdisjoint(forbidden_fields)