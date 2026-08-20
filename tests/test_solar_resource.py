from datetime import date

import pytest

from services.solar_resource import (
    build_season_solar_resource,
    parse_monthly_specific_yield,
)


def _monthly(value=5.0):
  return {month: value for month in range(1, 13)}


def test_season_dates_define_inclusive_operating_period():
  result = build_season_solar_resource(
      "Dalyan",
      36.8350,
      28.6424,
      date(2026, 4, 1),
      date(2026, 9, 30),
      monthly_specific_yield=_monthly(),
  )

  assert result.season_days == 183
  assert result.average_daily_specific_yield_kwh_per_kwp == pytest.approx(5.0)
  assert result.season_specific_yield_kwh_per_kwp == pytest.approx(915.0)


def test_partial_months_are_prorated_by_actual_selected_days():
  monthly = _monthly(4.0)
  monthly[4] = 6.0
  monthly[5] = 8.0

  result = build_season_solar_resource(
      "Test",
      36.0,
      28.0,
      date(2026, 4, 29),
      date(2026, 5, 2),
      monthly_specific_yield=monthly,
  )

  assert result.season_days == 4
  assert result.season_specific_yield_kwh_per_kwp == pytest.approx(28.0)
  assert result.average_daily_specific_yield_kwh_per_kwp == pytest.approx(7.0)


def test_rejects_reversed_date_range():
  with pytest.raises(ValueError):
    build_season_solar_resource(
        "Test",
        36.0,
        28.0,
        date(2026, 10, 1),
        date(2026, 4, 1),
        monthly_specific_yield=_monthly(),
    )


def test_pvgis_json_parser_requires_all_months():
  payload = {
      "outputs": {
          "monthly": {
              "fixed": [
                  {"month": month, "E_d": 4.0 + month / 10}
                  for month in range(1, 13)
              ]
          }
      }
  }

  parsed = parse_monthly_specific_yield(payload)

  assert parsed[1] == pytest.approx(4.1)
  assert parsed[12] == pytest.approx(5.2)
