from dataclasses import FrozenInstanceError, fields
from datetime import date

import pytest

from calculations.phase1_journey_demand_analysis import (
  JourneyDemandRouteSummary,
  summarize_phase1_journey_demand,
)
from models.phase1_journey_demand import JourneyDemandPeriod
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


def _period(index, **overrides):
  start_month = index
  values = {
    "journey_demand_id": f"YD-2025-{index:02d}",
    "period_label": f"Dönem {index}",
    "route_id": "ROTA-DALYAN-IZTUZU",
    "route_name": "Dalyan–İztuzu",
    "period_start": date(2025, start_month, 1),
    "period_end": date(2025, start_month, 10),
    "round_trip_passenger_demand": index * 1000,
    "peak_factor": 1.25,
    "input_basis": InputBasis.ASSUMED,
    "verification_status": VerificationStatus.SYNTHETIC,
  }
  values.update(overrides)
  return JourneyDemandPeriod(**values)


def test_summary_aggregates_route_demand_without_assignments():
  periods = (
    _period(4, round_trip_passenger_demand=12000),
    _period(5, round_trip_passenger_demand=65000),
    _period(6, round_trip_passenger_demand=110000),
  )

  summary = summarize_phase1_journey_demand(periods)[0]

  assert summary.route_id == "ROTA-DALYAN-IZTUZU"
  assert summary.route_name == "Dalyan–İztuzu"
  assert summary.season_start == date(2025, 4, 1)
  assert summary.season_end == date(2025, 6, 10)
  assert summary.period_count == 3
  assert summary.total_service_days == 30
  assert summary.total_round_trip_passenger_demand == 187000
  assert summary.total_passenger_leg_demand == 374000
  assert summary.average_daily_round_trip == pytest.approx(
    6233.333333333333
  )
  assert summary.highest_demand_period_id == "YD-2025-06"
  assert summary.highest_demand_period_label == "Dönem 6"
  assert (
    summary.highest_period_round_trip_passenger_demand
    == 110000
  )
  assert summary.peak_daily_round_trip == 13750
  assert summary.peak_daily_period_id == "YD-2025-06"


def test_highest_period_and_peak_daily_period_can_differ():
  periods = (
    _period(
      4,
      round_trip_passenger_demand=10000,
      peak_factor=3.0,
    ),
    _period(
      5,
      round_trip_passenger_demand=12000,
      peak_factor=1.0,
    ),
  )

  summary = summarize_phase1_journey_demand(periods)[0]

  assert summary.highest_demand_period_id == "YD-2025-05"
  assert summary.peak_daily_period_id == "YD-2025-04"
  assert summary.peak_daily_round_trip == 3000


def test_summary_groups_routes_in_stable_route_id_order():
  periods = (
    _period(
      5,
      journey_demand_id="YD-B-05",
      route_id="ROTA-B",
      route_name="Rota B",
    ),
    _period(
      4,
      journey_demand_id="YD-A-04",
      route_id="ROTA-A",
      route_name="Rota A",
    ),
  )

  summaries = summarize_phase1_journey_demand(periods)

  assert tuple(item.route_id for item in summaries) == (
    "ROTA-A",
    "ROTA-B",
  )


def test_summary_rejects_empty_period_collection():
  with pytest.raises(
    ValueError,
    match="Özetlenecek yolculuk talebi dönemi bulunamadı",
  ):
    summarize_phase1_journey_demand(())


@pytest.mark.parametrize("invalid_value", [object(), "geçersiz"])
def test_summary_requires_journey_demand_records(invalid_value):
  with pytest.raises(
    ValueError,
    match="yalnızca JourneyDemandPeriod",
  ):
    summarize_phase1_journey_demand((invalid_value,))


def test_summary_rejects_non_iterable_input():
  with pytest.raises(
    ValueError,
    match="JourneyDemandPeriod kayıtları içermelidir",
  ):
    summarize_phase1_journey_demand(None)


def test_summary_rejects_duplicate_period_ids():
  periods = (
    _period(4),
    _period(
      5,
      journey_demand_id="YD-2025-04",
    ),
  )

  with pytest.raises(
    ValueError,
    match="Tekrarlanan journey_demand_id: YD-2025-04",
  ):
    summarize_phase1_journey_demand(periods)


def test_summary_rejects_inconsistent_route_names():
  periods = (
    _period(4),
    _period(5, route_name="Başka Rota"),
  )

  with pytest.raises(
    ValueError,
    match="birden fazla rota adı içeriyor",
  ):
    summarize_phase1_journey_demand(periods)


def test_summary_rejects_overlapping_periods_on_same_route():
  periods = (
    _period(
      4,
      period_end=date(2025, 4, 15),
    ),
    _period(
      5,
      period_start=date(2025, 4, 15),
      period_end=date(2025, 4, 30),
    ),
  )

  with pytest.raises(
    ValueError,
    match="çakışan dönemler",
  ):
    summarize_phase1_journey_demand(periods)


def test_summary_accepts_adjacent_periods():
  periods = (
    _period(
      4,
      period_end=date(2025, 4, 15),
    ),
    _period(
      5,
      period_start=date(2025, 4, 16),
      period_end=date(2025, 4, 30),
    ),
  )

  summary = summarize_phase1_journey_demand(periods)[0]

  assert summary.total_service_days == 30


def test_period_overlap_is_allowed_across_different_routes():
  periods = (
    _period(4),
    _period(
      4,
      journey_demand_id="YD-OTHER-04",
      route_id="ROTA-OTHER",
      route_name="Diğer Rota",
    ),
  )

  assert len(summarize_phase1_journey_demand(periods)) == 2


def test_summary_is_frozen():
  summary = summarize_phase1_journey_demand((_period(4),))[0]

  with pytest.raises(FrozenInstanceError):
    summary.period_count = 2


def test_summary_does_not_mutate_input_order():
  periods = (
    _period(6),
    _period(4),
    _period(5),
  )

  original_ids = tuple(
    period.journey_demand_id
    for period in periods
  )
  summarize_phase1_journey_demand(periods)

  assert tuple(
    period.journey_demand_id
    for period in periods
  ) == original_ids


def test_equal_demand_ties_select_earliest_period():
  periods = (
    _period(
      5,
      round_trip_passenger_demand=10000,
    ),
    _period(
      4,
      round_trip_passenger_demand=10000,
    ),
  )

  summary = summarize_phase1_journey_demand(periods)[0]

  assert summary.highest_demand_period_id == "YD-2025-04"
  assert summary.peak_daily_period_id == "YD-2025-04"


def test_summary_schema_excludes_operational_decisions():
  field_names = {
    field.name
    for field in fields(JourneyDemandRouteSummary)
  }

  assert field_names.isdisjoint({
    "vessel_capacity",
    "trip_count",
    "required_vessel_count",
    "vessel_assignment",
    "energy_demand_kwh",
    "supply_point_id",
    "infrastructure_sufficiency",
    "parking_revenue_try",
    "conversion_priority",
    "optimization_result",
  })
