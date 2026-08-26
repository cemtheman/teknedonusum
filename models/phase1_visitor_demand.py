"""Faz 1 mevsimsel ve yıllık ziyaretçi talebi veri sözleşmeleri.

Bu modül ziyaretçi yoğunluğu hakkında beyan edilen, varsayılan veya
dolaylı olarak tahmin edilen kaynak verilerini saklar.

Ziyaretçi sayısını tekne yolcusu, sefer sayısı, enerji talebi, gelir,
arz noktası ataması veya optimizasyon sonucuna dönüştürmez.
"""

from dataclasses import dataclass
from enum import Enum
from models.phase1_supply_demand_capacity import (
  InputBasis,
)


class SeasonalDemandBand(str, Enum):
  """Ziyaretçi talebinin mevsimsel yoğunluk sınıfı."""

  EARLY_SEASON = "early_season"
  PEAK_SEASON = "peak_season"
  OFF_SEASON = "off_season"


class VisitorTrackingMethod(str, Enum):
  """Yıllık ziyaretçi tahmininde kullanılan izleme yöntemi."""

  PARKING_RECEIPTS = "parking_receipts"
  BOAT_CAPACITY = "boat_capacity"
  COMBINED_INDIRECT = "combined_indirect"


def _require_non_blank(
  field_name: str,
  value: object,
) -> None:
  if not isinstance(value, str) or not value.strip():
    raise ValueError(
      f"{field_name} alanı boş olmayan bir metin olmalıdır"
    )


def _require_reference_year(value: object) -> None:
  if (
    isinstance(value, bool)
    or not isinstance(value, int)
    or not 1900 <= value <= 2100
  ):
    raise ValueError(
      "reference_year alanı 1900 ile 2100 arasında "
      "bir tam sayı olmalıdır"
    )


def _require_month(
  field_name: str,
  value: object,
) -> None:
  if (
    isinstance(value, bool)
    or not isinstance(value, int)
    or not 1 <= value <= 12
  ):
    raise ValueError(
      f"{field_name} alanı 1 ile 12 arasında "
      "bir tam sayı olmalıdır"
    )


def _require_non_negative_integer(
  field_name: str,
  value: object,
) -> None:
  if isinstance(value, bool) or not isinstance(value, int):
    raise ValueError(
      f"{field_name} alanı tam sayı olmalıdır"
    )

  if value < 0:
    raise ValueError(
      f"{field_name} alanı sıfırdan küçük olamaz"
    )


def _require_positive_integer(
  field_name: str,
  value: object,
) -> None:
  if isinstance(value, bool) or not isinstance(value, int):
    raise ValueError(
      f"{field_name} alanı pozitif bir tam sayı olmalıdır"
    )

  if value <= 0:
    raise ValueError(
      f"{field_name} alanı pozitif bir tam sayı olmalıdır"
    )


def _require_input_basis(value: object) -> None:
  if not isinstance(value, InputBasis):
    raise ValueError(
      "input_basis alanı InputBasis türünde olmalıdır"
    )


@dataclass(frozen=True)
class SeasonalVisitorDemandInput:
  """Belirli ay aralığına ait ziyaretçi yoğunluğu girdisi."""

  seasonal_demand_id: str
  location_name: str
  reference_year: int
  start_month: int
  end_month: int
  season_band: SeasonalDemandBand
  monthly_visitor_min: int | None
  monthly_visitor_max: int | None
  input_basis: InputBasis
  source_note: str

  def __post_init__(self) -> None:
    _require_non_blank(
      "seasonal_demand_id",
      self.seasonal_demand_id,
    )
    _require_non_blank(
      "location_name",
      self.location_name,
    )
    _require_non_blank(
      "source_note",
      self.source_note,
    )

    _require_reference_year(self.reference_year)
    _require_month(
      "start_month",
      self.start_month,
    )
    _require_month(
      "end_month",
      self.end_month,
    )

    if self.end_month < self.start_month:
      raise ValueError(
        "end_month alanı start_month alanından "
        "önce olamaz"
      )

    if not isinstance(
      self.season_band,
      SeasonalDemandBand,
    ):
      raise ValueError(
        "season_band alanı "
        "SeasonalDemandBand türünde olmalıdır"
      )

    range_values = (
      self.monthly_visitor_min,
      self.monthly_visitor_max,
    )

    if (
      range_values[0] is None
      and range_values[1] is not None
    ) or (
      range_values[0] is not None
      and range_values[1] is None
    ):
      raise ValueError(
        "monthly_visitor_min ve monthly_visitor_max "
        "alanları birlikte dolu veya birlikte boş olmalıdır"
      )

    if self.monthly_visitor_min is not None:
      _require_non_negative_integer(
        "monthly_visitor_min",
        self.monthly_visitor_min,
      )
      _require_non_negative_integer(
        "monthly_visitor_max",
        self.monthly_visitor_max,
      )

      if (
        self.monthly_visitor_min
        > self.monthly_visitor_max
      ):
        raise ValueError(
          "monthly_visitor_min alanı "
          "monthly_visitor_max alanından büyük olamaz"
        )

    _require_input_basis(self.input_basis)


@dataclass(frozen=True)
class AnnualVisitorDemandEstimate:
  """Bir yıl için dolaylı yöntemle oluşturulan ziyaretçi tahmini."""

  annual_demand_id: str
  location_name: str
  reference_year: int
  estimated_annual_visitors: int
  tracking_method: VisitorTrackingMethod
  input_basis: InputBasis
  source_note: str

  def __post_init__(self) -> None:
    _require_non_blank(
      "annual_demand_id",
      self.annual_demand_id,
    )
    _require_non_blank(
      "location_name",
      self.location_name,
    )
    _require_non_blank(
      "source_note",
      self.source_note,
    )

    _require_reference_year(self.reference_year)
    _require_positive_integer(
      "estimated_annual_visitors",
      self.estimated_annual_visitors,
    )

    if not isinstance(
      self.tracking_method,
      VisitorTrackingMethod,
    ):
      raise ValueError(
        "tracking_method alanı "
        "VisitorTrackingMethod türünde olmalıdır"
      )

    _require_input_basis(self.input_basis)