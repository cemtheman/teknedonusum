from datetime import date

import pytest

from services.pvgis_crosscheck import (
    compare_pvgis_seasonal_yields,
    sum_typical_hourly_season_yield,
)


def test_hourly_season_sum_integrates_one_hour_buckets():
  profile = {
      (6, 1, 10): 0.5,
      (6, 1, 11): 0.8,
      (6, 1, 12): 0.7,
  }

  total = sum_typical_hourly_season_yield(
      profile,
      date(2026, 6, 1),
      date(2026, 6, 1),
  )

  assert total == pytest.approx(2.0)


def test_crosscheck_reports_signed_and_relative_difference():
  profile = {
      (6, 1, 10): 0.5,
      (6, 1, 11): 0.5,
  }

  result = compare_pvgis_seasonal_yields(
      2.0,
      profile,
      date(2026, 6, 1),
      date(2026, 6, 1),
  )

  assert result.hourly_season_specific_yield_kwh_per_kwp == pytest.approx(1.0)
  assert result.absolute_difference_kwh_per_kwp == pytest.approx(-1.0)
  assert result.relative_difference_percent == pytest.approx(-50.0)
