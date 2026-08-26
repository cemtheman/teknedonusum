"""Faz 1 dönemsel yolculuk talebi veri sözleşmesi.

Bu modül rota ve dönem bazındaki gidiş-dönüş yolcu talebini saklar.
Gün sayısı, tek yön yolcu bacağı, günlük ortalama ve pik günlük talep
ham girdilerden türetilir.

Tekne veya sefer ataması, kapasite yeterlilik kararı, enerji hesabı,
gelir hesabı, sıralama ya da optimizasyon sonucu üretmez.
"""

from dataclasses import dataclass
from datetime import date, datetime
from math import floor, isfinite
from numbers import Real

from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


def _require_non_blank(
  field_name: str,
  value: object,
) -> None:
  if not isinstance(value, str) or not value.strip():
    raise ValueError(
      f"{field_name} alanı boş olmayan bir metin olmalıdır"
    )


def _require_date(
  field_name: str,
  value: object,
) -> None:
  if not isinstance(value, date) or isinstance(value, datetime):
    raise ValueError(
      f"{field_name} alanı yalnızca tarih olmalıdır"
    )


def _require_non_negative_integer(
  field_name: str,
  value: object,
) -> None:
  if isinstance(value, bool) or not isinstance(value, int):
    raise ValueError(
      f"{field_name} alanı sıfır veya pozitif tam sayı olmalıdır"
    )

  if value < 0:
    raise ValueError(
      f"{field_name} alanı sıfırdan küçük olamaz"
    )


def _require_peak_factor(value: object) -> None:
  if isinstance(value, bool) or not isinstance(value, Real):
    raise ValueError(
      "peak_factor alanı 1 veya daha büyük sonlu bir sayı olmalıdır"
    )

  if not isfinite(float(value)) or value < 1:
    raise ValueError(
      "peak_factor alanı 1 veya daha büyük sonlu bir sayı olmalıdır"
    )


@dataclass(frozen=True)
class JourneyDemandPeriod:
  """Bir rota ve tarih aralığına ait gidiş-dönüş yolcu talebi."""

  journey_demand_id: str
  period_label: str
  route_id: str
  route_name: str
  period_start: date
  period_end: date
  round_trip_passenger_demand: int
  peak_factor: float
  input_basis: InputBasis
  verification_status: VerificationStatus

  def __post_init__(self) -> None:
    _require_non_blank(
      "journey_demand_id",
      self.journey_demand_id,
    )
    _require_non_blank(
      "period_label",
      self.period_label,
    )
    _require_non_blank(
      "route_id",
      self.route_id,
    )
    _require_non_blank(
      "route_name",
      self.route_name,
    )
    _require_date(
      "period_start",
      self.period_start,
    )
    _require_date(
      "period_end",
      self.period_end,
    )

    if self.period_end < self.period_start:
      raise ValueError(
        "period_end alanı period_start alanından önce olamaz"
      )

    _require_non_negative_integer(
      "round_trip_passenger_demand",
      self.round_trip_passenger_demand,
    )
    _require_peak_factor(self.peak_factor)

    if not isinstance(self.input_basis, InputBasis):
      raise ValueError(
        "input_basis alanı InputBasis türünde olmalıdır"
      )

    if not isinstance(
      self.verification_status,
      VerificationStatus,
    ):
      raise ValueError(
        "verification_status alanı "
        "VerificationStatus türünde olmalıdır"
      )

  @property
  def service_days(self) -> int:
    """Başlangıç ve bitiş günleri dahil hizmet günü sayısı."""

    return (self.period_end - self.period_start).days + 1

  @property
  def passenger_leg_demand(self) -> int:
    """Gidiş ve dönüşü ayrı sayan tek yön yolcu bacağı talebi."""

    return self.round_trip_passenger_demand * 2

  @property
  def average_daily_round_trip(self) -> float:
    """Dönem içindeki ortalama günlük gidiş-dönüş yolcu talebi."""

    return self.round_trip_passenger_demand / self.service_days

  @property
  def peak_daily_round_trip(self) -> int:
    """Excel ROUND ile uyumlu pozitif pik günlük yolcu talebi."""

    return floor(
      self.average_daily_round_trip
      * self.peak_factor
      + 0.5
    )
