"""Faz 1 rota ve dönem bazlı hizmet faaliyeti veri sözleşmesi.

Bu modül, bir JourneyDemandPeriod kaydına ait rota toplamı tekne
gidiş-dönüş faaliyetini saklar. Tekne veya kooperatif bazında sefer varsayımı,
yolcu kapasitesi, doluluk, filo ataması ya da kapasite yeterlilik kararı üretmez.
"""

from dataclasses import dataclass

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


@dataclass(frozen=True)
class RouteServiceActivityPeriod:
  """Bir talep dönemindeki rota toplamı tekne gidiş-dönüş faaliyeti."""

  service_activity_id: str
  journey_demand_id: str
  route_id: str
  total_vessel_round_trips: int
  input_basis: InputBasis
  verification_status: VerificationStatus
  source_note: str

  def __post_init__(self) -> None:
    _require_non_blank(
      "service_activity_id",
      self.service_activity_id,
    )
    _require_non_blank(
      "journey_demand_id",
      self.journey_demand_id,
    )
    _require_non_blank(
      "route_id",
      self.route_id,
    )
    _require_non_blank(
      "source_note",
      self.source_note,
    )
    _require_non_negative_integer(
      "total_vessel_round_trips",
      self.total_vessel_round_trips,
    )

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
