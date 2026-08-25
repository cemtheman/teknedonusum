"""Faz 1 sentetik tekne envanteri Excel içe aktarma sınırı.

Bu modül yalnızca mockup çalışma kitabındaki envanter verilerini okur
ve doğrulanmış VesselInventory kayıtlarına dönüştürür.

Dönüşüm fazı, tahrik sistemi, öncelik, hibe, kapasite tahsisi veya
optimizasyon kararı üretmez.
"""

from io import BytesIO
from math import isfinite

import pandas as pd

from models.phase1_supply_demand_capacity import (
  ActivityGroup,
  VerificationStatus,
  VesselInventory,
)


MOCKUP_SHEET_NAME = "Mockup Tekne Listesi"
MOCKUP_HEADER_ROW = 3

REQUIRED_COLUMNS = (
  "Plaka No",
  "Tekne Adı",
  "Donatanı",
  "Tekne Cinsi",
  "Faaliyet Grubu",
  "Boyu (m)",
  "Eni (m)",
  "Kooperatif",
  "Veri Durumu",
)

_ACTIVITY_GROUPS = {
  "ticari": ActivityGroup.COMMERCIAL,
  "özel": ActivityGroup.PRIVATE,
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


def _plate_text(value) -> str:
  if value is None or pd.isna(value):
    return ""

  return str(value)


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


def _positive_float(
  field_name: str,
  value,
  row_number: int,
) -> float:
  text = _normalize_text(value)

  try:
    result = float(text.replace(",", "."))
  except (TypeError, ValueError):
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "pozitif bir sayı olmalıdır"
    ) from None

  if not isfinite(result) or result <= 0:
    raise ValueError(
      f"Satır {row_number}: {field_name} alanı "
      "pozitif bir sayı olmalıdır"
    )

  return result


def _activity_group(
  value,
  row_number: int,
) -> ActivityGroup:
  source_value = _normalize_text(value)
  result = _ACTIVITY_GROUPS.get(source_value.casefold())

  if result is None:
    raise ValueError(
      f"Satır {row_number}: Faaliyet Grubu değeri "
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


def _cooperative_id(value) -> str | None:
  cooperative_name = _normalize_text(value)

  if not cooperative_name:
    return None

  return f"mockup-cooperative:{cooperative_name}"


def _read_mockup_frame(source) -> pd.DataFrame:
  reusable_source = _reusable_excel_source(source)
  excel_file = pd.ExcelFile(reusable_source)

  if MOCKUP_SHEET_NAME not in excel_file.sheet_names:
    raise ValueError(
      "Mockup Tekne Listesi sayfası bulunamadı"
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


def load_phase1_mockup_inventory_excel(
  source,
) -> tuple[VesselInventory, ...]:
  """Mockup Excel dosyasını katı Faz 1 envanter kayıtlarına dönüştür."""

  frame = _read_mockup_frame(source)
  vessels = []
  seen_plates = set()

  for frame_index, row in frame.iterrows():
    row_number = int(frame_index) + MOCKUP_HEADER_ROW + 2
    plate_number = _plate_text(row["Plaka No"])

    if plate_number in seen_plates:
      raise ValueError(
        f"Tekrarlanan Plaka No: {plate_number}"
      )

    activity_group = _activity_group(
      row["Faaliyet Grubu"],
      row_number,
    )
    verification_status = _verification_status(
      row["Veri Durumu"],
      row_number,
    )

    try:
      vessel = VesselInventory(
        vessel_id=f"mockup:{plate_number}",
        plate_number=plate_number,
        vessel_name=_normalize_text(
          row["Tekne Adı"]
        ),
        owner_name=_normalize_text(
          row["Donatanı"]
        ),
        vessel_type=_normalize_text(
          row["Tekne Cinsi"]
        ),
        activity_group=activity_group,
        length_m=_positive_float(
          "Boyu (m)",
          row["Boyu (m)"],
          row_number,
        ),
        beam_m=_positive_float(
          "Eni (m)",
          row["Eni (m)"],
          row_number,
        ),
        cooperative_id=_cooperative_id(
          row["Kooperatif"]
        ),
        verification_status=verification_status,
      )
    except ValueError as error:
      raise ValueError(
        f"Satır {row_number}: {error}"
      ) from error

    seen_plates.add(plate_number)
    vessels.append(vessel)

  if not vessels:
    raise ValueError(
      "Mockup Tekne Listesi sayfasında "
      "içe aktarılabilir tekne kaydı yok"
    )

  return tuple(vessels)