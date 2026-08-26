from dataclasses import (
  FrozenInstanceError,
  fields,
)

import pytest

from models.phase1_supply_demand_capacity import (
  InputBasis,
)
from models.phase1_visitor_demand import (
  AnnualVisitorDemandEstimate,
  SeasonalDemandBand,
  SeasonalVisitorDemandInput,
  VisitorTrackingMethod,
)


def _early_season(**overrides):
  values = {
    "seasonal_demand_id": "visitor-demand-early",
    "location_name": "İztuzu Plajı",
    "reference_year": 2025,
    "start_month": 2,
    "end_month": 4,
    "season_band": SeasonalDemandBand.EARLY_SEASON,
    "monthly_visitor_min": 15000,
    "monthly_visitor_max": 20000,
    "input_basis": InputBasis.ASSUMED,
    "source_note": (
      "Şubat, mart ve nisan aylarında aylık "
      "15.000–20.000 ziyaretçi mockup varsayımı."
    ),
  }
  values.update(overrides)
  return SeasonalVisitorDemandInput(**values)


def _peak_season(**overrides):
  values = {
    "seasonal_demand_id": "visitor-demand-peak",
    "location_name": "İztuzu Plajı",
    "reference_year": 2025,
    "start_month": 5,
    "end_month": 9,
    "season_band": SeasonalDemandBand.PEAK_SEASON,
    "monthly_visitor_min": None,
    "monthly_visitor_max": None,
    "input_basis": InputBasis.ASSUMED,
    "source_note": (
      "Toplam ziyaretçilerin ezici çoğunluğunun "
      "Mayıs–Eylül döneminde gerçekleştiği "
      "mockup varsayımı."
    ),
  }
  values.update(overrides)
  return SeasonalVisitorDemandInput(**values)


def _annual_estimate(**overrides):
  values = {
    "annual_demand_id": "visitor-demand-2025",
    "location_name": "İztuzu Plajı",
    "reference_year": 2025,
    "estimated_annual_visitors": 1_000_000,
    "tracking_method": (
      VisitorTrackingMethod.COMBINED_INDIRECT
    ),
    "input_basis": InputBasis.DECLARED,
    "source_note": (
      "Ortaca Belediyesi verilerine dayalı mockup: "
      "kara yolu girişleri otopark fişleriyle, kanal "
      "ulaşımı dolmuş tekne kapasiteleriyle dolaylı "
      "olarak izlenmektedir."
    ),
  }
  values.update(overrides)
  return AnnualVisitorDemandEstimate(**values)


def test_mockup_preserves_supplied_seasonal_information():
  early_season = _early_season()
  peak_season = _peak_season()

  assert early_season.reference_year == 2025
  assert early_season.start_month == 2
  assert early_season.end_month == 4
  assert early_season.monthly_visitor_min == 15000
  assert early_season.monthly_visitor_max == 20000
  assert (
    early_season.season_band
    is SeasonalDemandBand.EARLY_SEASON
  )

  assert peak_season.start_month == 5
  assert peak_season.end_month == 9
  assert peak_season.monthly_visitor_min is None
  assert peak_season.monthly_visitor_max is None
  assert (
    peak_season.season_band
    is SeasonalDemandBand.PEAK_SEASON
  )

  assert early_season.input_basis is InputBasis.ASSUMED
  assert peak_season.input_basis is InputBasis.ASSUMED


def test_mockup_preserves_2025_annual_indirect_estimate():
  estimate = _annual_estimate()

  assert estimate.reference_year == 2025
  assert estimate.estimated_annual_visitors == 1_000_000
  assert (
    estimate.tracking_method
    is VisitorTrackingMethod.COMBINED_INDIRECT
  )
  assert estimate.input_basis is InputBasis.DECLARED


def test_seasonal_demand_input_is_frozen():
  demand_input = _early_season()

  with pytest.raises(FrozenInstanceError):
    demand_input.start_month = 3


def test_annual_demand_estimate_is_frozen():
  estimate = _annual_estimate()

  with pytest.raises(FrozenInstanceError):
    estimate.estimated_annual_visitors = 900000


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("start_month", 0),
    ("start_month", 13),
    ("end_month", 0),
    ("end_month", 13),
  ],
)
def test_month_values_must_be_between_one_and_twelve(
  field_name,
  invalid_value,
):
  with pytest.raises(
    ValueError,
    match="1 ile 12 arasında",
  ):
    _early_season(
      **{field_name: invalid_value}
    )


def test_end_month_cannot_precede_start_month():
  with pytest.raises(
    ValueError,
    match="end_month alanı start_month",
  ):
    _early_season(
      start_month=9,
      end_month=5,
    )


@pytest.mark.parametrize(
  (
    "monthly_visitor_min",
    "monthly_visitor_max",
  ),
  [
    (15000, None),
    (None, 20000),
  ],
)
def test_visitor_range_requires_both_limits_or_neither(
  monthly_visitor_min,
  monthly_visitor_max,
):
  with pytest.raises(
    ValueError,
    match="birlikte dolu veya birlikte boş",
  ):
    _early_season(
      monthly_visitor_min=monthly_visitor_min,
      monthly_visitor_max=monthly_visitor_max,
    )


@pytest.mark.parametrize(
  (
    "monthly_visitor_min",
    "monthly_visitor_max",
  ),
  [
    (-1, 20000),
    (15000, -1),
  ],
)
def test_seasonal_visitor_counts_cannot_be_negative(
  monthly_visitor_min,
  monthly_visitor_max,
):
  with pytest.raises(
    ValueError,
    match="sıfırdan küçük olamaz",
  ):
    _early_season(
      monthly_visitor_min=monthly_visitor_min,
      monthly_visitor_max=monthly_visitor_max,
    )


def test_minimum_visitor_count_cannot_exceed_maximum():
  with pytest.raises(
    ValueError,
    match="monthly_visitor_min alanı",
  ):
    _early_season(
      monthly_visitor_min=20001,
      monthly_visitor_max=20000,
    )


@pytest.mark.parametrize(
  "field_name",
  [
    "seasonal_demand_id",
    "location_name",
    "source_note",
  ],
)
def test_seasonal_required_text_fields_cannot_be_blank(
  field_name,
):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı",
  ):
    _early_season(
      **{field_name: " "}
    )


def test_season_band_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="SeasonalDemandBand türünde",
  ):
    _early_season(
      season_band="early_season"
    )


def test_input_basis_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="InputBasis türünde",
  ):
    _early_season(
      input_basis="assumed"
    )


@pytest.mark.parametrize(
  "invalid_year",
  [
    1899,
    2101,
    2025.0,
    True,
  ],
)
def test_reference_year_must_be_valid(
  invalid_year,
):
  with pytest.raises(
    ValueError,
    match="reference_year alanı",
  ):
    _annual_estimate(
      reference_year=invalid_year
    )


@pytest.mark.parametrize(
  "invalid_count",
  [
    0,
    -1,
    1_000_000.0,
    True,
  ],
)
def test_annual_visitor_estimate_must_be_positive_integer(
  invalid_count,
):
  with pytest.raises(
    ValueError,
    match="estimated_annual_visitors alanı",
  ):
    _annual_estimate(
      estimated_annual_visitors=invalid_count
    )


def test_annual_schema_excludes_entry_fee_fields():
  field_names = {
    field.name
    for field in fields(AnnualVisitorDemandEstimate)
  }

  assert field_names.isdisjoint({
    "road_vehicle_entry_fee_try",
    "vehicle_entry_fee_try",
    "parking_fee_try",
  })


def test_tracking_method_requires_strict_enum():
  with pytest.raises(
    ValueError,
    match="VisitorTrackingMethod türünde",
  ):
    _annual_estimate(
      tracking_method="combined_indirect"
    )


@pytest.mark.parametrize(
  "field_name",
  [
    "annual_demand_id",
    "location_name",
    "source_note",
  ],
)
def test_annual_required_text_fields_cannot_be_blank(
  field_name,
):
  with pytest.raises(
    ValueError,
    match=f"{field_name} alanı",
  ):
    _annual_estimate(
      **{field_name: " "}
    )


def test_seasonal_schema_has_no_boat_conversion_fields():
  field_names = {
    field.name
    for field in fields(SeasonalVisitorDemandInput)
  }

  forbidden_fields = {
    "boat_transport_share",
    "passenger_count",
    "trip_count",
    "energy_demand_kwh",
    "supply_point_id",
    "conversion_priority",
    "optimization_result",
  }

  assert field_names.isdisjoint(forbidden_fields)


def test_annual_schema_has_no_derived_counts_or_revenue():
  field_names = {
    field.name
    for field in fields(AnnualVisitorDemandEstimate)
  }

  forbidden_fields = {
    "vehicle_count",
    "parking_revenue_try",
    "boat_passenger_count",
    "trip_count",
    "energy_demand_kwh",
    "optimization_result",
  }

  assert field_names.isdisjoint(forbidden_fields)