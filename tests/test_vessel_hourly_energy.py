from copy import deepcopy
from datetime import date

import pytest

from calculations.vessel_hourly_energy import build_vessel_hourly_energy_balance
from config.vessels import BASE_VESSEL_SPECS


def test_v1_six_knot_solar_assisted_path_can_be_shore_free():
  typical = {
      (6, 1, hour): (0.90 if 8 <= hour <= 17 else 0.0)
      for hour in range(24)
  }

  result = build_vessel_hourly_energy_balance(
      vessel_id="v1",
      spec=deepcopy(BASE_VESSEL_SPECS["v1"]),
      cruise_speed=6.0,
      daily_miles=35.0,
      season_start=date(2026, 6, 1),
      season_end=date(2026, 6, 1),
      typical_hourly_specific_pv=typical,
  )

  assert result.season_propulsion_kwh == pytest.approx(
      41.08703676465949
  )
  assert result.solar_direct_to_propulsion_kwh > 0
  assert result.shore_energy_kwh == pytest.approx(0.0)
