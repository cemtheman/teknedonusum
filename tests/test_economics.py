from copy import deepcopy

import pytest

from calculations.economics import calculate_vessel_economics
from calculations.vessel_physics import calc_calibrated_vessel_physics
from config.vessels import BASE_VESSEL_SPECS


def test_default_v1_economics_regression():
  spec = deepcopy(BASE_VESSEL_SPECS["v1"])
  spec.update({
      "totalCostEur": 108100,
      "totalCost": 5999550,
      "maxGrant": 3299752,
  })
  physics = calc_calibrated_vessel_physics(
      spec,
      cruise_spd=6.0,
      d_miles=35.0,
      s_hours=8.0,
  )

  result = calculate_vessel_economics(
      spec,
      physics,
      eur_rate=55.50,
      diesel_price=81.81,
      elec_price=3.50,
      operating_days=180,
  )

  expected = {
      "motor_cost_tl": 697234.528511962,
      "solar_cost_tl": 303696.0,
      "bat_cost_tl": 2220000.0,
      "infra_share_tl": 277500.0,
      "hull_cost_tl": 2501119.471488038,
      "grant_amount": 3299752.0,
      "net_capex": 2699798.0,
      "old_diesel_consumption": 5837.268631821622,
      "old_diesel_cost": 477546.9467693269,
      "old_maint_cost": 140000.0,
      "old_total_annual": 617546.9467693269,
      "grid_electricity_consumption": 0.0,
      "new_elec_cost": 0.0,
      "new_degradation": 56527.01725424742,
      "new_maint_cost": 21000.0,
      "new_total_annual": 77527.01725424742,
      "net_savings": 540019.9295150795,
      "payback_seasons": 4.9994414139943535,
      "payback_months": 29.99664848396612,
      "old_co2": 15.643879933281948,
      "new_co2": 0.0,
      "net_co2": 15.643879933281948,
  }

  for field, baseline in expected.items():
    assert getattr(result, field) == pytest.approx(baseline)
