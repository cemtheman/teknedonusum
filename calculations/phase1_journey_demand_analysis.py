"""Faz 1 dönemsel yolculuk talebi toplulaştırma sınırı.

Bu modül doğrulanmış JourneyDemandPeriod kayıtlarını rota bazında
karar üretmeyen özetlere dönüştürür.

Tekne kapasitesi, sefer sayısı, tekne ataması, enerji talebi, altyapı
yeterliliği, gelir, dönüşüm önceliği veya optimizasyon üretmez.
"""

from dataclasses import dataclass
from datetime import date

from models.phase1_journey_demand import JourneyDemandPeriod


@dataclass(frozen=True)
class JourneyDemandRouteSummary:
  """Bir rotanın dönem kayıtlarından türetilen talep özeti."""

  route_id: str
  route_name: str
  season_start: date
  season_end: date
  period_count: int
  total_service_days: int
  total_round_trip_passenger_demand: int
  total_passenger_leg_demand: int
  average_daily_round_trip: float
  highest_demand_period_id: str
  highest_demand_period_label: str
  highest_period_round_trip_passenger_demand: int
  peak_daily_round_trip: int
  peak_daily_period_id: str
  peak_daily_period_label: str


def _require_period_records(periods) -> tuple[JourneyDemandPeriod, ...]:
  try:
    records = tuple(periods)
  except TypeError as error:
    raise ValueError(
      "periods alanı JourneyDemandPeriod kayıtları içermelidir"
    ) from error

  if not records:
    raise ValueError(
      "Özetlenecek yolculuk talebi dönemi bulunamadı"
    )

  for record in records:
    if not isinstance(record, JourneyDemandPeriod):
      raise ValueError(
        "periods alanı yalnızca JourneyDemandPeriod "
        "kayıtları içermelidir"
      )

  return records


def _require_unique_period_ids(
  periods: tuple[JourneyDemandPeriod, ...],
) -> None:
  seen_ids = set()

  for period in periods:
    if period.journey_demand_id in seen_ids:
      raise ValueError(
        "Tekrarlanan journey_demand_id: "
        f"{period.journey_demand_id}"
      )

    seen_ids.add(period.journey_demand_id)


def _summarize_route(
  route_id: str,
  periods: list[JourneyDemandPeriod],
) -> JourneyDemandRouteSummary:
  route_names = {
    period.route_name
    for period in periods
  }

  if len(route_names) != 1:
    raise ValueError(
      f"{route_id} rota kimliği birden fazla rota adı içeriyor"
    )

  ordered = sorted(
    periods,
    key=lambda period: (
      period.period_start,
      period.period_end,
      period.journey_demand_id,
    ),
  )

  for previous, current in zip(ordered, ordered[1:]):
    if current.period_start <= previous.period_end:
      raise ValueError(
        f"{route_id} rotasında çakışan dönemler: "
        f"{previous.journey_demand_id}, "
        f"{current.journey_demand_id}"
      )

  total_service_days = sum(
    period.service_days
    for period in ordered
  )
  total_round_trip = sum(
    period.round_trip_passenger_demand
    for period in ordered
  )

  highest_demand_period = min(
    ordered,
    key=lambda period: (
      -period.round_trip_passenger_demand,
      period.period_start,
      period.journey_demand_id,
    ),
  )
  peak_daily_period = min(
    ordered,
    key=lambda period: (
      -period.peak_daily_round_trip,
      period.period_start,
      period.journey_demand_id,
    ),
  )

  return JourneyDemandRouteSummary(
    route_id=route_id,
    route_name=next(iter(route_names)),
    season_start=ordered[0].period_start,
    season_end=max(
      period.period_end
      for period in ordered
    ),
    period_count=len(ordered),
    total_service_days=total_service_days,
    total_round_trip_passenger_demand=total_round_trip,
    total_passenger_leg_demand=sum(
      period.passenger_leg_demand
      for period in ordered
    ),
    average_daily_round_trip=(
      total_round_trip / total_service_days
    ),
    highest_demand_period_id=(
      highest_demand_period.journey_demand_id
    ),
    highest_demand_period_label=(
      highest_demand_period.period_label
    ),
    highest_period_round_trip_passenger_demand=(
      highest_demand_period.round_trip_passenger_demand
    ),
    peak_daily_round_trip=(
      peak_daily_period.peak_daily_round_trip
    ),
    peak_daily_period_id=(
      peak_daily_period.journey_demand_id
    ),
    peak_daily_period_label=(
      peak_daily_period.period_label
    ),
  )


def summarize_phase1_journey_demand(
  periods,
) -> tuple[JourneyDemandRouteSummary, ...]:
  """Dönemsel yolculuk talebini rota bazında toplulaştır."""

  records = _require_period_records(periods)
  _require_unique_period_ids(records)

  grouped: dict[str, list[JourneyDemandPeriod]] = {}

  for period in records:
    grouped.setdefault(period.route_id, []).append(period)

  return tuple(
    _summarize_route(route_id, grouped[route_id])
    for route_id in sorted(grouped)
  )
