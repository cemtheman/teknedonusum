from dataclasses import (
  FrozenInstanceError,
  fields,
  replace,
)
from datetime import date, datetime, timedelta, timezone

import pytest

from models.phase1_dataset import Phase1DataSet
from models.phase1_supply_demand_capacity import (
  ActivityGroup,
  AvailabilityBasis,
  CapacitySnapshot,
  EnergyDemandResult,
  InputBasis,
  OperationalDemandInput,
  SupplyAvailabilityProfile,
  SupplyPoint,
  VerificationStatus,
  VesselInventory,
)


NOW = datetime(
  2026,
  8,
  25,
  12,
  0,
  tzinfo=timezone.utc,
)


def _vessel(
  vessel_id="vessel-1",
  plate_number="T-001",
):
  return VesselInventory(
    vessel_id=vessel_id,
    plate_number=plate_number,
    vessel_name="Martı",
    owner_name="Ali Arslan",
    vessel_type="Yolcu Motoru",
    activity_group=ActivityGroup.COMMERCIAL,
    length_m=11.8,
    beam_m=3.5,
    cooperative_id="cooperative-1",
    verification_status=VerificationStatus.FIELD_VERIFIED,
  )


def _demand_input(
  demand_input_id="demand-1",
  vessel_id="vessel-1",
):
  return OperationalDemandInput(
    demand_input_id=demand_input_id,
    vessel_id=vessel_id,
    measurement_date=date(2026, 8, 25),
    service_speed_kn=6.0,
    route_distance_nm_day=35.0,
    service_hours_day=7.0,
    operating_days_year=180,
    installed_mechanical_power_kw=45.0,
    auxiliary_energy_kwh_day=8.0,
    reserve_fraction=0.20,
    input_basis=InputBasis.MEASURED,
    valid_from=NOW,
  )


def _demand_result(
  demand_result_id="result-1",
  demand_input_id="demand-1",
):
  return EnergyDemandResult(
    demand_result_id=demand_result_id,
    demand_input_id=demand_input_id,
    methodology_version="phase1-v1",
    propulsion_energy_kwh_day=120.0,
    total_energy_kwh_day=128.0,
    peak_power_kw=45.0,
    annual_energy_kwh=23040.0,
    calculated_at=NOW,
  )


def _supply_point(
  supply_point_id="supply-1",
):
  return SupplyPoint(
    supply_point_id=supply_point_id,
    site_name="Dalyan İskele",
    latitude=36.834,
    longitude=28.642,
    connection_type="Şebeke",
    operational_status="Ön inceleme",
    operator_name="Muğla Büyükşehir Belediyesi",
  )


def _supply_profile(
  supply_profile_id="profile-1",
  supply_point_id="supply-1",
):
  return SupplyAvailabilityProfile(
    supply_profile_id=supply_profile_id,
    supply_point_id=supply_point_id,
    interval_start=NOW,
    interval_end=NOW + timedelta(hours=1),
    available_power_kw=100.0,
    energy_limit_kwh=100.0,
    availability_basis=AvailabilityBasis.ESTIMATED,
    valid_from=NOW,
  )


def _capacity_snapshot(
  capacity_snapshot_id="capacity-1",
  supply_point_id="supply-1",
):
  return CapacitySnapshot(
    capacity_snapshot_id=capacity_snapshot_id,
    supply_point_id=supply_point_id,
    observed_at=NOW,
    contracted_power_kw=120.0,
    transformer_power_kva=160.0,
    firm_capacity_kw=100.0,
    reserved_capacity_kw=20.0,
    simultaneous_unit_limit=4,
    source_document="Saha tespit formu",
  )


def _valid_dataset(**overrides):
  values = {
    "vessels": (_vessel(),),
    "demand_inputs": (_demand_input(),),
    "demand_results": (_demand_result(),),
    "supply_points": (_supply_point(),),
    "supply_profiles": (_supply_profile(),),
    "capacity_snapshots": (_capacity_snapshot(),),
  }
  values.update(overrides)
  return Phase1DataSet(**values)


def test_dataset_accepts_valid_references():
  dataset = _valid_dataset()

  assert len(dataset.vessels) == 1
  assert len(dataset.demand_inputs) == 1
  assert len(dataset.demand_results) == 1
  assert len(dataset.supply_points) == 1
  assert len(dataset.supply_profiles) == 1
  assert len(dataset.capacity_snapshots) == 1


def test_dataset_is_frozen():
  dataset = _valid_dataset()

  with pytest.raises(FrozenInstanceError):
    dataset.vessels = ()


def test_dataset_rejects_duplicate_vessel_ids():
  second_vessel = replace(
    _vessel(),
    plate_number="T-002",
  )

  with pytest.raises(
    ValueError,
    match="Tekrarlanan vessel_id: vessel-1",
  ):
    _valid_dataset(
      vessels=(
        _vessel(),
        second_vessel,
      )
    )


def test_dataset_rejects_duplicate_plate_numbers():
  second_vessel = replace(
    _vessel(),
    vessel_id="vessel-2",
  )

  with pytest.raises(
    ValueError,
    match="Tekrarlanan plate_number: T-001",
  ):
    _valid_dataset(
      vessels=(
        _vessel(),
        second_vessel,
      )
    )


def test_dataset_rejects_orphan_demand_input():
  with pytest.raises(
    ValueError,
    match="bilinmeyen vessel_id içeriyor: missing-vessel",
  ):
    _valid_dataset(
      demand_inputs=(
        _demand_input(
          vessel_id="missing-vessel"
        ),
      )
    )


def test_dataset_rejects_duplicate_demand_input_ids():
  with pytest.raises(
    ValueError,
    match="Tekrarlanan demand_input_id: demand-1",
  ):
    _valid_dataset(
      demand_inputs=(
        _demand_input(),
        _demand_input(),
      )
    )


def test_dataset_rejects_orphan_demand_result():
  with pytest.raises(
    ValueError,
    match=(
      "bilinmeyen demand_input_id içeriyor: "
      "missing-demand"
    ),
  ):
    _valid_dataset(
      demand_results=(
        _demand_result(
          demand_input_id="missing-demand"
        ),
      )
    )


def test_dataset_rejects_duplicate_demand_result_ids():
  with pytest.raises(
    ValueError,
    match="Tekrarlanan demand_result_id: result-1",
  ):
    _valid_dataset(
      demand_results=(
        _demand_result(),
        _demand_result(),
      )
    )


def test_dataset_rejects_duplicate_supply_point_ids():
  with pytest.raises(
    ValueError,
    match="Tekrarlanan supply_point_id: supply-1",
  ):
    _valid_dataset(
      supply_points=(
        _supply_point(),
        _supply_point(),
      )
    )


def test_dataset_rejects_orphan_supply_profile():
  with pytest.raises(
    ValueError,
    match=(
      "bilinmeyen supply_point_id içeriyor: "
      "missing-supply"
    ),
  ):
    _valid_dataset(
      supply_profiles=(
        _supply_profile(
          supply_point_id="missing-supply"
        ),
      )
    )


def test_dataset_rejects_duplicate_supply_profile_ids():
  with pytest.raises(
    ValueError,
    match="Tekrarlanan supply_profile_id: profile-1",
  ):
    _valid_dataset(
      supply_profiles=(
        _supply_profile(),
        _supply_profile(),
      )
    )


def test_dataset_rejects_orphan_capacity_snapshot():
  with pytest.raises(
    ValueError,
    match=(
      "bilinmeyen supply_point_id içeriyor: "
      "missing-supply"
    ),
  ):
    _valid_dataset(
      capacity_snapshots=(
        _capacity_snapshot(
          supply_point_id="missing-supply"
        ),
      )
    )


def test_dataset_rejects_duplicate_capacity_snapshot_ids():
  with pytest.raises(
    ValueError,
    match=(
      "Tekrarlanan capacity_snapshot_id: capacity-1"
    ),
  ):
    _valid_dataset(
      capacity_snapshots=(
        _capacity_snapshot(),
        _capacity_snapshot(),
      )
    )


def test_dataset_has_no_decision_or_optimization_fields():
  field_names = {
    field.name
    for field in fields(Phase1DataSet)
  }

  forbidden_fields = {
    "vessel_supply_assignments",
    "conversion_priorities",
    "recommended_propulsion",
    "rankings",
    "optimization_result",
  }

  assert field_names.isdisjoint(forbidden_fields)