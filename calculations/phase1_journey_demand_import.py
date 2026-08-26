"""Faz 1 sentetik dönemsel yolculuk talebi Excel içe aktarma sınırı.

Bu modül yalnızca mockup çalışma kitabındaki rota ve dönem bazlı yolcu
talebini okur ve doğrulanmış JourneyDemandPeriod kayıtlarına dönüştürür.

Tekne kapasitesi, sefer sayısı, tekne ataması, enerji talebi, altyapı
yeterliliği, gelir veya yatırım sıralaması üretmez.
"""

from datetime import date, datetime
from io import BytesIO
from math import isclose, isfinite
from numbers import Integral, Real

import pandas as pd

from models.phase1_journey_demand import JourneyDemandPeriod
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


MOCKUP_SHEET_NAME = "Mockup Yolculuk Talebi"
MOCKUP_HEADER_ROW = 3

REQUIRED_COLUMNS = (
  "Talep Dönemi ID",
  "Dönem",
  "Rota ID",
  "Rota",
  "Dönem Başlangıcı",
  "Dönem Bitişi",
  "Gün Sayısı",
  "Aylık Gidiş-Dönüş Yolcu",
  "Tek Yön Yolcu Bacağı",
  "Ortalama Günlük Gidiş-Dönüş Yolcu",
  "Pik Katsayısı",
  "Pik Günlük Gidiş-Dönüş Yolcu",
  "Talep Dayanağı",
  "Veri Durumu",
)

_INPUT_BASES = {
  "ölçülen": InputBasis.MEASURED,
  "beyan edilen": InputBasis.DECLARED,
  "varsayılan": InputBasis.ASSUMED,
  "sentetik varsayım": InputBasis.ASSUMED,
}

_VERIFICATION_STATUSES = {
  "sentetik — saha doğrulaması gerekli": (
    VerificationStatus.SYNTHETIC
  ),
  "saha doğrulaması gerekli": (
    VerificationStatus.REQUIRES_FIELD_VERIFICATION
  ),
  "saha doğrulandı": (
    VerificationStatus.FIELD_VERIFIED
  ),
}


def _normalize_text(value) -> str:
  if value is None or pd.isna(value):
    return ""

  return str(value).strip()


def _reusable_excel_source(source):
  if isinstance(source, bytes):
    return BytesIO(source)

  if isinstance(source, bytearray):
    return BytesIO(bytes(source))

  if hasattr(source, "read") and hasattr(source, "seek"):
    current_position = source.tell()
    source.seek(0)
    data = source.read()
    source.seek(current_position)

    if isinstance(data, bytes):
      return BytesIO(data)

  return source


def _date_only(
  field_name: str,
  value,
  row_number: int,
) -> date:
  if isinstance(value, datetime):
    return value.date()

  if isinstance(value, date):
    return value

  raise ValueError(
    f"Satır {row_number}: {field_name} alanı "
    "Excel tarih değeri olmalıdır"
  )


def _non_negative_integer(
  field_name: str,
  value,
  row_number: int,
) -> int:
  if isinstance(value, bool):
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "sıfır veya pozitif tam sayı olmalıdır"
    )

  if isinstance(value, Integral):
    result = int(value)
  elif (
    isinstance(value, Real)
    and isfinite(float(value))
    and float(value).is_integer()
  ):
    result = int(value)
  else:
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "sıfır veya pozitif tam sayı olmalıdır"
    )

  if result < 0:
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "sıfırdan küçük olamaz"
    )

  return result


def _peak_factor(value, row_number: int) -> float:
  if (
    isinstance(value, bool)
    or not isinstance(value, Real)
    or not isfinite(float(value))
    or value < 1
  ):
    raise ValueError(
      f"Satır {row_number}: Pik Katsayısı alanı "
      "1 veya daha büyük sonlu bir sayı olmalıdır"
    )

  return float(value)


def _input_basis(value, row_number: int) -> InputBasis:
  source_value = _normalize_text(value)
  result = _INPUT_BASES.get(source_value.casefold())

  if result is None:
    raise ValueError(
      f"Satır {row_number}: Talep Dayanağı değeri "
      f"tanınmadı: {source_value or '(boş)'}"
    )

  return result


def _verification_status(
  value,
  row_number: int,
) -> VerificationStatus:
  source_value = _normalize_text(value)
  result = _VERIFICATION_STATUSES.get(
    source_value.casefold()
  )

  if result is None:
    raise ValueError(
      f"Satır {row_number}: Veri Durumu değeri "
      f"tanınmadı: {source_value or '(boş)'}"
    )

  return result


def _derived_number(
  field_name: str,
  value,
  row_number: int,
) -> float:
  if (
    isinstance(value, bool)
    or not isinstance(value, Real)
    or not isfinite(float(value))
  ):
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "sonlu bir sayı olmalıdır"
    )

  return float(value)


def _require_derived_integer_match(
  field_name: str,
  supplied_value,
  expected_value: int,
  row_number: int,
) -> None:
  supplied = _non_negative_integer(
    field_name,
    supplied_value,
    row_number,
  )

  if supplied != expected_value:
    raise ValueError(
      f"Satır {row_number}: {field_name} değeri "
      "ham girdilerle uyuşmuyor; "
      f"beklenen {expected_value}, bulunan {supplied}"
    )


def _require_derived_float_match(
  field_name: str,
  supplied_value,
  expected_value: float,
  row_number: int,
) -> None:
  supplied = _derived_number(
    field_name,
    supplied_value,
    row_number,
  )

  if not isclose(
    supplied,
    expected_value,
    rel_tol=1e-9,
    abs_tol=1e-6,
  ):
    raise ValueError(
      f"Satır {row_number}: {field_name} değeri "
      "ham girdilerle uyuşmuyor"
    )


def _read_mockup_frame(source) -> pd.DataFrame:
  reusable_source = _reusable_excel_source(source)
  excel_file = pd.ExcelFile(reusable_source)

  if MOCKUP_SHEET_NAME not in excel_file.sheet_names:
    raise ValueError(
      "Mockup Yolculuk Talebi sayfası bulunamadı"
    )

  frame = pd.read_excel(
    excel_file,
    sheet_name=MOCKUP_SHEET_NAME,
    header=MOCKUP_HEADER_ROW,
    dtype=object,
  )

  frame.columns = [
    _normalize_text(column)
    for column in frame.columns
  ]

  missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in frame.columns
  ]

  if missing_columns:
    raise ValueError(
      "Eksik zorunlu sütunlar: "
      + ", ".join(missing_columns)
    )

  return frame.dropna(how="all")


def load_phase1_mockup_journey_demand_excel(
  source,
) -> tuple[JourneyDemandPeriod, ...]:
  """Mockup Excel dosyasını katı dönemsel yolculuk talebine dönüştür."""

  frame = _read_mockup_frame(source)
  periods = []
  seen_ids = set()

  for frame_index, row in frame.iterrows():
    row_number = int(frame_index) + MOCKUP_HEADER_ROW + 2
    journey_demand_id = _normalize_text(
      row["Talep Dönemi ID"]
    )

    if journey_demand_id in seen_ids:
      raise ValueError(
        "Tekrarlanan Talep Dönemi ID: "
        f"{journey_demand_id}"
      )

    try:
      period = JourneyDemandPeriod(
        journey_demand_id=journey_demand_id,
        period_label=_normalize_text(row["Dönem"]),
        route_id=_normalize_text(row["Rota ID"]),
        route_name=_normalize_text(row["Rota"]),
        period_start=_date_only(
          "Dönem Başlangıcı",
          row["Dönem Başlangıcı"],
          row_number,
        ),
        period_end=_date_only(
          "Dönem Bitişi",
          row["Dönem Bitişi"],
          row_number,
        ),
        round_trip_passenger_demand=(
          _non_negative_integer(
            "Aylık Gidiş-Dönüş Yolcu",
            row["Aylık Gidiş-Dönüş Yolcu"],
            row_number,
          )
        ),
        peak_factor=_peak_factor(
          row["Pik Katsayısı"],
          row_number,
        ),
        input_basis=_input_basis(
          row["Talep Dayanağı"],
          row_number,
        ),
        verification_status=_verification_status(
          row["Veri Durumu"],
          row_number,
        ),
      )
    except ValueError as error:
      if str(error).startswith(f"Satır {row_number}:"):
        raise
      raise ValueError(
        f"Satır {row_number}: {error}"
      ) from error

    _require_derived_integer_match(
      "Gün Sayısı",
      row["Gün Sayısı"],
      period.service_days,
      row_number,
    )
    _require_derived_integer_match(
      "Tek Yön Yolcu Bacağı",
      row["Tek Yön Yolcu Bacağı"],
      period.passenger_leg_demand,
      row_number,
    )
    _require_derived_float_match(
      "Ortalama Günlük Gidiş-Dönüş Yolcu",
      row["Ortalama Günlük Gidiş-Dönüş Yolcu"],
      period.average_daily_round_trip,
      row_number,
    )
    _require_derived_integer_match(
      "Pik Günlük Gidiş-Dönüş Yolcu",
      row["Pik Günlük Gidiş-Dönüş Yolcu"],
      period.peak_daily_round_trip,
      row_number,
    )

    seen_ids.add(journey_demand_id)
    periods.append(period)

  if not periods:
    raise ValueError(
      "Mockup Yolculuk Talebi sayfasında "
      "içe aktarılabilir dönem kaydı yok"
    )

  return tuple(periods)
