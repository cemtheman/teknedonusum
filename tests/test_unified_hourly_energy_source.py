from copy import deepcopy
from datetime import date
from types import SimpleNamespace
import pytest
from calculations.fleet_energy_balance import build_fleet_energy_balance
from calculations.vessel_detail_analysis import build_vessel_detail_analysis
from config.vessels import BASE_VESSEL_SPECS

def _inputs():
  return SimpleNamespace(cruise_speed=6.0,daily_miles=35.0,season_start=date(2026,6,1),season_end=date(2026,6,1),operating_days=1,diesel_price=80.0,elec_price=3.5,eur_rate=56.0,average_daily_specific_yield_kwh_per_kwp=5.5,sun_hours=None)

def _spec():
  s=deepcopy(BASE_VESSEL_SPECS["v1"]); s.update(merged=1,totalCost=1_000_000.0,maxGrant=0.0,grantRate=0.0,batCostEur=10_000.0); return s

def _typical(): return {(6,1,h):(0.90 if 8 <= h <= 17 else 0.0) for h in range(24)}

def test_detail_uses_hourly_normalized_shore_energy():
  d=build_vessel_detail_analysis("v1",_spec(),_inputs(),typical_hourly_specific_pv=_typical())
  assert d.daily_grid_kwh == pytest.approx(d.season_grid_kwh)
  assert d.new_electricity_cost_tl == pytest.approx(d.season_grid_kwh*3.5)

def test_fleet_and_detail_use_same_hourly_energy_source():
  s=_spec()
  f=build_fleet_energy_balance({"v1":s},{"v1":1},6.0,35.0,None,1,season_start=date(2026,6,1),season_end=date(2026,6,1),typical_hourly_specific_pv=_typical())
  d=build_vessel_detail_analysis("v1",s,_inputs(),typical_hourly_specific_pv=_typical())
  assert f.annual_grid_kwh == pytest.approx(d.season_grid_kwh)
  assert f.annual_solar_kwh == pytest.approx(d.season_solar_kwh)

def test_hourly_coverage_means_shore_independence():
  f=build_fleet_energy_balance({"v1":_spec()},{"v1":1},6.0,35.0,None,1,season_start=date(2026,6,1),season_end=date(2026,6,1),typical_hourly_specific_pv=_typical())
  expected=(1.0-f.annual_grid_kwh/f.daily_propulsion_kwh)*100.0
  assert f.solar_coverage_ratio == pytest.approx(expected)
