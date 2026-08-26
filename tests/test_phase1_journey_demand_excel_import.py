from dataclasses import fields
from datetime import date
from io import BytesIO

import pytest
from openpyxl import Workbook

from calculations.phase1_journey_demand_import import (
  load_phase1_mockup_journey_demand_excel,
)
from models.phase1_journey_demand import JourneyDemandPeriod
from models.phase1_supply_demand_capacity import (
  InputBasis,
  VerificationStatus,
)


HEADERS = (
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


def _row(**overrides):
  values = {
    "Talep Dönemi ID": "YD-2025-05",
    "Dönem": "Mayıs 2025",
    "Rota ID": "ROTA-DALYAN-IZTUZU",
    "Rota": "Dalyan–İztuzu",
    "Dönem Başlangıcı": date(2025, 5, 1),
    "Dönem Bitişi": date(2025, 5, 31),
    "Gün Sayısı": 31,
    "Aylık Gidiş-Dönüş Yolcu": 65000,
    "Tek Yön Yolcu Bacağı": 130000,
    "Ortalama Günlük Gidiş-Dönüş Yolcu": (
      2096.7741935483873
    ),
    "Pik Katsayısı": 1.35,
    "Pik Günlük Gidiş-Dönüş Yolcu": 2831,
    "Talep Dayanağı": "Sentetik varsayım",
    "Veri Durumu": "Saha doğrulaması gerekli",
  }
  values.update(overrides)
  return values


def _workbook_bytes(
  rows,
  *,
  headers=HEADERS,
  sheet_name="Mockup Yolculuk Talebi",
):
  workbook = Workbook()
  worksheet = workbook.active
  worksheet.title = sheet_name

  worksheet.append([
    "Dalyan / İztuzu Sentetik Dönemsel "
    "Yolculuk Talebi — 2025 v1"
  ])
  worksheet.append([
    "1 Nisan–30 Eylül sezonu için sentetik talep."
  ])
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


def test_loader_maps_mockup_period_and_derives_indicators():
  period = load_phase1_mockup_journey_demand_excel(
    _workbook_bytes([_row()])
  )[0]

  assert period.journey_demand_id == "YD-2025-05"
  assert period.period_label == "Mayıs 2025"
  assert period.route_id == "ROTA-DALYAN-IZTUZU"
  assert period.route_name == "Dalyan–İztuzu"
  assert period.period_start == date(2025, 5, 1)
  assert period.period_end == date(2025, 5, 31)
  assert period.round_trip_passenger_demand == 65000
  assert period.peak_factor == 1.35
  assert period.service_days == 31
  assert period.passenger_leg_demand == 130000
  assert period.average_daily_round_trip == pytest.approx(
    2096.7741935483873
  )
  assert period.peak_daily_round_trip == 2831


@pytest.mark.parametrize(
  ("source_value", "expected_basis"),
  [
    ("Ölçülen", InputBasis.MEASURED),
    ("Beyan edilen", InputBasis.DECLARED),
    ("Varsayılan", InputBasis.ASSUMED),
    ("Sentetik varsayım", InputBasis.ASSUMED),
  ],
)
def test_loader_maps_input_basis(source_value, expected_basis):
  period = load_phase1_mockup_journey_demand_excel(
    _workbook_bytes([
      _row(**{"Talep Dayanağı": source_value})
    ])
  )[0]

  assert period.input_basis is expected_basis


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
  period = load_phase1_mockup_journey_demand_excel(
    _workbook_bytes([
      _row(**{"Veri Durumu": source_value})
    ])
  )[0]

  assert period.verification_status is expected_status


def test_loader_rejects_duplicate_demand_period_ids():
  source = _workbook_bytes([
    _row(),
    _row(**{"Dönem": "İkinci dönem"}),
  ])

  with pytest.raises(
    ValueError,
    match="Tekrarlanan Talep Dönemi ID: YD-2025-05",
  ):
    load_phase1_mockup_journey_demand_excel(source)


def test_loader_rejects_missing_required_column():
  headers = tuple(
    header
    for header in HEADERS
    if header != "Pik Katsayısı"
  )

  with pytest.raises(
    ValueError,
    match="Eksik zorunlu sütunlar: Pik Katsayısı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([_row()], headers=headers)
    )


def test_loader_rejects_missing_mockup_sheet():
  with pytest.raises(
    ValueError,
    match="Mockup Yolculuk Talebi sayfası bulunamadı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes(
        [_row()],
        sheet_name="Başka Sayfa",
      )
    )


@pytest.mark.parametrize(
  "field_name",
  [
    "Dönem Başlangıcı",
    "Dönem Bitişi",
  ],
)
def test_loader_requires_excel_date_values(field_name):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı Excel tarih değeri",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{field_name: "2025-05-01"})
      ])
    )


@pytest.mark.parametrize(
  "invalid_value",
  [
    -1,
    65000.5,
    True,
    "65000",
  ],
)
def test_loader_requires_non_negative_integer_demand(
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match="Aylık Gidiş-Dönüş Yolcu alanı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{
          "Aylık Gidiş-Dönüş Yolcu": invalid_value,
        })
      ])
    )


@pytest.mark.parametrize(
  "invalid_value",
  [
    0.99,
    0,
    True,
    "1.35",
  ],
)
def test_loader_requires_valid_peak_factor(invalid_value):
  with pytest.raises(
    ValueError,
    match="Pik Katsayısı alanı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{"Pik Katsayısı": invalid_value})
      ])
    )


def test_loader_rejects_unknown_input_basis():
  with pytest.raises(
    ValueError,
    match="Talep Dayanağı değeri tanınmadı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{"Talep Dayanağı": "Belirsiz"})
      ])
    )


def test_loader_rejects_unknown_verification_status():
  with pytest.raises(
    ValueError,
    match="Veri Durumu değeri tanınmadı",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{"Veri Durumu": "Belirsiz"})
      ])
    )


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("Gün Sayısı", 30),
    ("Tek Yön Yolcu Bacağı", 129999),
    (
      "Ortalama Günlük Gidiş-Dönüş Yolcu",
      2096.0,
    ),
    ("Pik Günlük Gidiş-Dönüş Yolcu", 2830),
  ],
)
def test_loader_rejects_mismatched_derived_values(
  field_name,
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match=f"{field_name} değeri ham girdilerle uyuşmuyor",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([
        _row(**{field_name: invalid_value})
      ])
    )


def test_loader_rejects_empty_mockup_sheet():
  with pytest.raises(
    ValueError,
    match="içe aktarılabilir dönem kaydı yok",
  ):
    load_phase1_mockup_journey_demand_excel(
      _workbook_bytes([])
    )


def test_loader_does_not_expose_operational_decisions():
  period = load_phase1_mockup_journey_demand_excel(
    _workbook_bytes([_row()])
  )[0]
  field_names = {
    field.name
    for field in fields(JourneyDemandPeriod)
  }

  assert field_names.isdisjoint({
    "vessel_id",
    "trip_count",
    "energy_demand_kwh",
    "supply_point_id",
    "parking_revenue_try",
    "optimization_result",
  })
  assert not hasattr(period, "boat_assignment")
