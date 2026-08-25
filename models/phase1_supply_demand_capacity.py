"""Faz 1 arz, talep ve kapasite veri sözleşmeleri.

Bu modül yalnızca doğrulanan ve değiştirilemeyen veri kayıtlarını tanımlar.
Teknelere altyapı atamaz, yatırım önceliği belirlemez, şarj programı oluşturmaz
ve uygulama kararı üretmez.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from numbers import Real


_PLATE_PATTERN = re.compile(r"^(T|Ö)-([0-9]{3})$")


class ActivityGroup(str, Enum):
  """Teknenin ticari veya özel faaliyet grubu."""

  COMMERCIAL = "commercial"
  PRIVATE = "private"


class VerificationStatus(str, Enum):
  """Envanter kaydının saha doğrulama durumu."""

  SYNTHETIC = "synthetic"
  REQUIRES_FIELD_VERIFICATION = "requires_field_verification"
  FIELD_VERIFIED = "field_verified"


class InputBasis(str, Enum):
  """Operasyonel talep girdisinin veri dayanağı."""

  MEASURED = "measured"
  DECLARED = "declared"
  ASSUMED = "assumed"


class AvailabilityBasis(str, Enum):
  """Arz kullanılabilirlik profilinin veri dayanağı."""

  MEASURED = "measured"
  CONTRACTED = "contracted"
  ESTIMATED = "estimated"


def _require_non_blank(field_name: str, value: object) -> None:
  if not isinstance(value, str) or not value.strip():
    raise ValueError(
      f"{field_name} alanı boş olmayan bir metin olmalıdır"
    )


def _require_number(field_name: str, value: object) -> None:
  if isinstance(value, bool) or not isinstance(value, Real):
    raise ValueError(f"{field_name} alanı sayısal olmalıdır")


def _require_non_negative(
  field_name: str,
  value: object,
) -> None:
  _require_number(field_name, value)

  if value < 0:
    raise ValueError(
      f"{field_name} alanı sıfırdan küçük olamaz"
    )


def _require_positive(field_name: str, value: object) -> None:
  _require_number(field_name, value)

  if value <= 0:
    raise ValueError(
      f"{field_name} alanı sıfırdan büyük olmalıdır"
    )


def _require_integer(field_name: str, value: object) -> None:
  if isinstance(value, bool) or not isinstance(value, int):
    raise ValueError(f"{field_name} alanı tam sayı olmalıdır")


def _require_aware_datetime(
  field_name: str,
  value: object,
) -> None:
  if not isinstance(value, datetime):
    raise ValueError(
      f"{field_name} alanı tarih ve saat değeri olmalıdır"
    )

  if value.tzinfo is None or value.utcoffset() is None:
    raise ValueError(
      f"{field_name} alanı saat dilimi bilgisi içermelidir"
    )


def _require_optional_aware_datetime(
  field_name: str,
  value: object,
) -> None:
  if value is not None:
    _require_aware_datetime(field_name, value)


@dataclass(frozen=True)
class VesselInventory:
  """Bir teknenin temel envanter ve plaka kaydı."""

  vessel_id: str
  plate_number: str
  vessel_name: str
  owner_name: str
  vessel_type: str
  activity_group: ActivityGroup
  length_m: float
  beam_m: float
  cooperative_id: str | None
  verification_status: VerificationStatus

  def __post_init__(self) -> None:
    _require_non_blank("vessel_id", self.vessel_id)
    _require_non_blank("plate_number", self.plate_number)
    _require_non_blank("vessel_name", self.vessel_name)
    _require_non_blank("owner_name", self.owner_name)
    _require_non_blank("vessel_type", self.vessel_type)

    plate_match = _PLATE_PATTERN.fullmatch(self.plate_number)

    if plate_match is None or plate_match.group(2) == "000":
      raise ValueError(
        "plate_number alanı T-001 veya Ö-001 biçiminde olmalıdır"
      )

    if not isinstance(self.activity_group, ActivityGroup):
      raise ValueError(
        "activity_group alanı ActivityGroup türünde olmalıdır"
      )

    plate_prefix = plate_match.group(1)

    if (
      plate_prefix == "T"
      and self.activity_group is not ActivityGroup.COMMERCIAL
    ):
      raise ValueError(
        "T plaka serisi yalnız ticari teknelerde kullanılabilir"
      )

    if (
      plate_prefix == "Ö"
      and self.activity_group is not ActivityGroup.PRIVATE
    ):
      raise ValueError(
        "Ö plaka serisi yalnız özel teknelerde kullanılabilir"
      )

    _require_positive("length_m", self.length_m)
    _require_positive("beam_m", self.beam_m)

    if self.cooperative_id is not None:
      _require_non_blank(
        "cooperative_id",
        self.cooperative_id,
      )

    if not isinstance(
      self.verification_status,
      VerificationStatus,
    ):
      raise ValueError(
        "verification_status alanı "
        "VerificationStatus türünde olmalıdır"
      )


@dataclass(frozen=True)
class OperationalDemandInput:
  """Bir tekneye ait sürümlü operasyonel talep girdileri."""

  demand_input_id: str
  vessel_id: str
  measurement_date: date
  service_speed_kn: float
  route_distance_nm_day: float
  service_hours_day: float
  operating_days_year: int
  installed_mechanical_power_kw: float
  auxiliary_energy_kwh_day: float
  reserve_fraction: float
  input_basis: InputBasis
  valid_from: datetime
  valid_to: datetime | None = None

  def __post_init__(self) -> None:
    _require_non_blank(
      "demand_input_id",
      self.demand_input_id,
    )
    _require_non_blank("vessel_id", self.vessel_id)

    if (
      not isinstance(self.measurement_date, date)
      or isinstance(self.measurement_date, datetime)
    ):
      raise ValueError(
        "measurement_date alanı yalnızca tarih olmalıdır"
      )

    _require_positive(
      "service_speed_kn",
      self.service_speed_kn,
    )
    _require_non_negative(
      "route_distance_nm_day",
      self.route_distance_nm_day,
    )
    _require_non_negative(
      "service_hours_day",
      self.service_hours_day,
    )

    if self.service_hours_day > 24:
      raise ValueError(
        "service_hours_day alanı 24'ten büyük olamaz"
      )

    _require_integer(
      "operating_days_year",
      self.operating_days_year,
    )

    if not 0 <= self.operating_days_year <= 366:
      raise ValueError(
        "operating_days_year alanı 0 ile 366 arasında olmalıdır"
      )

    _require_positive(
      "installed_mechanical_power_kw",
      self.installed_mechanical_power_kw,
    )
    _require_non_negative(
      "auxiliary_energy_kwh_day",
      self.auxiliary_energy_kwh_day,
    )
    _require_number(
      "reserve_fraction",
      self.reserve_fraction,
    )

    if not 0 <= self.reserve_fraction <= 1:
      raise ValueError(
        "reserve_fraction alanı 0 ile 1 arasında olmalıdır"
      )

    if not isinstance(self.input_basis, InputBasis):
      raise ValueError(
        "input_basis alanı InputBasis türünde olmalıdır"
      )

    _require_aware_datetime(
      "valid_from",
      self.valid_from,
    )
    _require_optional_aware_datetime(
      "valid_to",
      self.valid_to,
    )

    if (
      self.valid_to is not None
      and self.valid_to <= self.valid_from
    ):
      raise ValueError(
        "valid_to alanı valid_from alanından sonra olmalıdır"
      )


@dataclass(frozen=True)
class EnergyDemandResult:
  """Sürümlü talep girdisine bağlı hesaplanmış enerji sonucu."""

  demand_result_id: str
  demand_input_id: str
  methodology_version: str
  propulsion_energy_kwh_day: float
  total_energy_kwh_day: float
  peak_power_kw: float
  annual_energy_kwh: float
  calculated_at: datetime

  def __post_init__(self) -> None:
    _require_non_blank(
      "demand_result_id",
      self.demand_result_id,
    )
    _require_non_blank(
      "demand_input_id",
      self.demand_input_id,
    )
    _require_non_blank(
      "methodology_version",
      self.methodology_version,
    )

    _require_non_negative(
      "propulsion_energy_kwh_day",
      self.propulsion_energy_kwh_day,
    )
    _require_non_negative(
      "total_energy_kwh_day",
      self.total_energy_kwh_day,
    )
    _require_non_negative(
      "peak_power_kw",
      self.peak_power_kw,
    )
    _require_non_negative(
      "annual_energy_kwh",
      self.annual_energy_kwh,
    )

    if (
      self.total_energy_kwh_day
      < self.propulsion_energy_kwh_day
    ):
      raise ValueError(
        "total_energy_kwh_day alanı "
        "propulsion_energy_kwh_day alanından küçük olamaz"
      )

    _require_aware_datetime(
      "calculated_at",
      self.calculated_at,
    )


@dataclass(frozen=True)
class SupplyPoint:
  """Atama veya planlama mantığı içermeyen fiziksel arz noktası."""

  supply_point_id: str
  site_name: str
  latitude: float
  longitude: float
  connection_type: str
  operational_status: str
  operator_name: str
  field_verified_at: datetime | None = None

  def __post_init__(self) -> None:
    _require_non_blank(
      "supply_point_id",
      self.supply_point_id,
    )
    _require_non_blank("site_name", self.site_name)
    _require_non_blank(
      "connection_type",
      self.connection_type,
    )
    _require_non_blank(
      "operational_status",
      self.operational_status,
    )
    _require_non_blank(
      "operator_name",
      self.operator_name,
    )

    _require_number("latitude", self.latitude)
    _require_number("longitude", self.longitude)

    if not -90 <= self.latitude <= 90:
      raise ValueError(
        "latitude alanı -90 ile 90 arasında olmalıdır"
      )

    if not -180 <= self.longitude <= 180:
      raise ValueError(
        "longitude alanı -180 ile 180 arasında olmalıdır"
      )

    _require_optional_aware_datetime(
      "field_verified_at",
      self.field_verified_at,
    )


@dataclass(frozen=True)
class SupplyAvailabilityProfile:
  """Bir arz noktasının zamanla sınırlı güç ve enerji profili."""

  supply_profile_id: str
  supply_point_id: str
  interval_start: datetime
  interval_end: datetime
  available_power_kw: float
  energy_limit_kwh: float | None
  availability_basis: AvailabilityBasis
  valid_from: datetime
  valid_to: datetime | None = None

  def __post_init__(self) -> None:
    _require_non_blank(
      "supply_profile_id",
      self.supply_profile_id,
    )
    _require_non_blank(
      "supply_point_id",
      self.supply_point_id,
    )

    _require_aware_datetime(
      "interval_start",
      self.interval_start,
    )
    _require_aware_datetime(
      "interval_end",
      self.interval_end,
    )

    if self.interval_end <= self.interval_start:
      raise ValueError(
        "interval_end alanı interval_start alanından "
        "sonra olmalıdır"
      )

    _require_non_negative(
      "available_power_kw",
      self.available_power_kw,
    )

    if self.energy_limit_kwh is not None:
      _require_positive(
        "energy_limit_kwh",
        self.energy_limit_kwh,
      )

    if not isinstance(
      self.availability_basis,
      AvailabilityBasis,
    ):
      raise ValueError(
        "availability_basis alanı "
        "AvailabilityBasis türünde olmalıdır"
      )

    _require_aware_datetime(
      "valid_from",
      self.valid_from,
    )
    _require_optional_aware_datetime(
      "valid_to",
      self.valid_to,
    )

    if (
      self.valid_to is not None
      and self.valid_to <= self.valid_from
    ):
      raise ValueError(
        "valid_to alanı valid_from alanından sonra olmalıdır"
      )


@dataclass(frozen=True)
class CapacitySnapshot:
  """Bir arz noktasında belirli zamanda tespit edilen kapasite."""

  capacity_snapshot_id: str
  supply_point_id: str
  observed_at: datetime
  contracted_power_kw: float
  transformer_power_kva: float | None
  firm_capacity_kw: float
  reserved_capacity_kw: float
  simultaneous_unit_limit: int | None
  source_document: str

  def __post_init__(self) -> None:
    _require_non_blank(
      "capacity_snapshot_id",
      self.capacity_snapshot_id,
    )
    _require_non_blank(
      "supply_point_id",
      self.supply_point_id,
    )
    _require_non_blank(
      "source_document",
      self.source_document,
    )
    _require_aware_datetime(
      "observed_at",
      self.observed_at,
    )

    _require_non_negative(
      "contracted_power_kw",
      self.contracted_power_kw,
    )

    if self.transformer_power_kva is not None:
      _require_non_negative(
        "transformer_power_kva",
        self.transformer_power_kva,
      )

    _require_non_negative(
      "firm_capacity_kw",
      self.firm_capacity_kw,
    )
    _require_non_negative(
      "reserved_capacity_kw",
      self.reserved_capacity_kw,
    )

    if self.reserved_capacity_kw > self.firm_capacity_kw:
      raise ValueError(
        "reserved_capacity_kw alanı "
        "firm_capacity_kw alanından büyük olamaz"
      )

    if self.simultaneous_unit_limit is not None:
      _require_integer(
        "simultaneous_unit_limit",
        self.simultaneous_unit_limit,
      )

      if self.simultaneous_unit_limit < 0:
        raise ValueError(
          "simultaneous_unit_limit alanı sıfırdan küçük olamaz"
        )

  @property
  def usable_capacity_kw(self) -> float:
    """Mevcut ayrımlardan sonra kalan kullanılabilir kapasiteyi döndür."""

    return self.firm_capacity_kw - self.reserved_capacity_kw