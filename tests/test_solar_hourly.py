from datetime import datetime

import pytest

from services.solar_hourly import (
    build_typical_hourly_profile,
    parse_hourly_specific_pv,
)


def test_parser_normalizes_one_kwp_pvgis_power_to_kw_per_kwp():
  payload = {
      "outputs": {
          "hourly": [
              {"time": "20240401:1200", "P": 820.0},
              {"time": "20240401:1300", "P": 760.0},
          ]
      }
  }

  points = parse_hourly_specific_pv(payload)

  assert points[0].timestamp == datetime(2024, 4, 1, 12, 0)
  assert points[0].specific_power_kw_per_kwp == pytest.approx(0.82)
  assert points[1].specific_power_kw_per_kwp == pytest.approx(0.76)


def test_typical_profile_averages_same_calendar_hour_across_years():
  payload = {
      "outputs": {
          "hourly": [
              {"time": "20230401:1200", "P": 600.0},
              {"time": "20240401:1200", "P": 800.0},
          ]
      }
  }

  profile = build_typical_hourly_profile(
      parse_hourly_specific_pv(payload)
  )

  assert profile[(4, 1, 12)] == pytest.approx(0.70)


def test_hourly_parser_rejects_missing_or_negative_power():
  with pytest.raises(ValueError):
    parse_hourly_specific_pv(
        {"outputs": {"hourly": [{"time": "20240401:1200"}]}}
    )

  with pytest.raises(ValueError):
    parse_hourly_specific_pv(
        {"outputs": {"hourly": [{"time": "20240401:1200", "P": -1}]}}
    )
