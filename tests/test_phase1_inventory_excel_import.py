from io import BytesIO

import pytest
from openpyxl import Workbook

from calculations.phase1_inventory_import import (
  load_phase1_mockup_inventory_excel,
)
from models.phase1_supply_demand_capacity import (
  ActivityGroup,
  VerificationStatus,
)


HEADERS = (
  "Plaka No",
  "Tekne Adı",
  "Donatanı",
  "Tekne Cinsi",
  "Faaliyet Grubu",
  "Boyu (m)",
  "Eni (m)",
  "Kooperatif",
  "Kooperatif Üyeliği",
  "Faz 1 Kapsamı",
  "Veri Durumu",
)


def _commercial_row(**overrides):
  row = {
    "Plaka No": "T-001",
    "Tekne Adı": "Martı Gecesi",
    "Donatanı": "Ali Arslan",
    "Tekne Cinsi": "Yolcu Motoru",
    "Faaliyet Grubu": "Ticari",
    "Boyu (m)": 11.76,
    "Eni (m)": 3.50,
    "Kooperatif": "Dalyan Kooperatifi",
    "Kooperatif Üyeliği": "Evet",
    "Faz 1 Kapsamı": (
      "Faz 1 doğrudan elektrikli dönüşüm adayı"
    ),
    "Veri Durumu": (
      "Sentetik — saha doğrulaması gerekli"
    ),
  }
  row.update(overrides)
  return row


def _private_row(**overrides):
  row = {
    "Plaka No": "Ö-001",
    "Tekne Adı": "Karia Sesi",
    "Donatanı": "Ahmet Öztürk",
    "Tekne Cinsi": "Özel Tekne",
    "Faaliyet Grubu": "Özel",
    "Boyu (m)": 10.48,
    "Eni (m)": 2.19,
    "Kooperatif": None,
    "Kooperatif Üyeliği": "Hayır",
    "Faz 1 Kapsamı": "Faz 1 kapsamı dışında",
    "Veri Durumu": (
      "Sentetik — saha doğrulaması gerekli"
    ),
  }
  row.update(overrides)
  return row


def _workbook_bytes(
  rows,
  *,
  headers=HEADERS,
  sheet_name="Mockup Tekne Listesi",
):
  workbook = Workbook()
  worksheet = workbook.active
  worksheet.title = sheet_name

  worksheet.append(
    ["Dalyan / Köyceğiz Mockup Tekne Listesi — v5"]
  )
  worksheet.append(
    ["Tamamen sentetik örnek listedir."]
  )
  worksheet.append([])
  worksheet.append(list(headers))

  for row in rows:
    worksheet.append(
      [row.get(header) for header in headers]
    )

  buffer = BytesIO()
  workbook.save(buffer)
  buffer.seek(0)
  return buffer


def test_loader_maps_commercial_and_private_vessels():
  vessels = load_phase1_mockup_inventory_excel(
    _workbook_bytes(
      [
        _commercial_row(),
        _private_row(),
      ]
    )
  )

  assert len(vessels) == 2

  commercial, private = vessels

  assert commercial.vessel_id == "mockup:T-001"
  assert commercial.plate_number == "T-001"
  assert (
    commercial.activity_group
    is ActivityGroup.COMMERCIAL
  )
  assert (
    commercial.cooperative_id
    == "mockup-cooperative:Dalyan Kooperatifi"
  )
  assert (
    commercial.verification_status
    is VerificationStatus.SYNTHETIC
  )

  assert private.vessel_id == "mockup:Ö-001"
  assert private.plate_number == "Ö-001"
  assert private.activity_group is ActivityGroup.PRIVATE
  assert private.cooperative_id is None
  assert (
    private.verification_status
    is VerificationStatus.SYNTHETIC
  )


@pytest.mark.parametrize(
  ("source_value", "expected_status"),
  [
    (
      "Sentetik — saha doğrulaması gerekli",
      VerificationStatus.SYNTHETIC,
    ),
    (
      "Saha doğrulaması gerekli",
      VerificationStatus.REQUIRES_FIELD_VERIFICATION,
    ),
    (
      "Saha doğrulandı",
      VerificationStatus.FIELD_VERIFIED,
    ),
  ],
)
def test_loader_maps_verification_status(
  source_value,
  expected_status,
):
  vessel = load_phase1_mockup_inventory_excel(
    _workbook_bytes(
      [
        _commercial_row(
          **{"Veri Durumu": source_value}
        )
      ]
    )
  )[0]

  assert vessel.verification_status is expected_status


def test_loader_rejects_duplicate_plate_numbers():
  source = _workbook_bytes(
    [
      _commercial_row(),
      _commercial_row(
        **{"Tekne Adı": "İkinci Tekne"}
      ),
    ]
  )

  with pytest.raises(
    ValueError,
    match="Tekrarlanan Plaka No: T-001",
  ):
    load_phase1_mockup_inventory_excel(source)


def test_loader_rejects_plate_activity_mismatch():
  source = _workbook_bytes(
    [
      _commercial_row(
        **{"Faaliyet Grubu": "Özel"}
      )
    ]
  )

  with pytest.raises(
    ValueError,
    match="T plaka serisi yalnız ticari",
  ):
    load_phase1_mockup_inventory_excel(source)


def test_loader_rejects_missing_required_column():
  headers = tuple(
    header
    for header in HEADERS
    if header != "Eni (m)"
  )

  source = _workbook_bytes(
    [_commercial_row()],
    headers=headers,
  )

  with pytest.raises(
    ValueError,
    match=r"Eksik zorunlu sütunlar: Eni \(m\)",
  ):
    load_phase1_mockup_inventory_excel(source)


def test_loader_rejects_unknown_verification_status():
  source = _workbook_bytes(
    [
      _commercial_row(
        **{"Veri Durumu": "Durumu belirsiz"}
      )
    ]
  )

  with pytest.raises(
    ValueError,
    match="Veri Durumu değeri tanınmadı",
  ):
    load_phase1_mockup_inventory_excel(source)


def test_loader_rejects_missing_mockup_sheet():
  source = _workbook_bytes(
    [_commercial_row()],
    sheet_name="Başka Sayfa",
  )

  with pytest.raises(
    ValueError,
    match="Mockup Tekne Listesi sayfası bulunamadı",
  ):
    load_phase1_mockup_inventory_excel(source)


def test_loader_does_not_expose_phase_or_propulsion_decisions():
  vessel = load_phase1_mockup_inventory_excel(
    _workbook_bytes(
      [
        _commercial_row(
          **{
            "Faz 1 Kapsamı": (
              "Bu içerik içe aktarılmamalıdır"
            )
          }
        )
      ]
    )
  )[0]

  assert not hasattr(vessel, "conversion_phase")
  assert not hasattr(vessel, "recommended_propulsion")
  assert not hasattr(vessel, "conversion_priority")