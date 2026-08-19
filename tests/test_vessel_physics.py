from copy import deepcopy

import pytest

from calculations.vessel_physics import calc_calibrated_vessel_physics
from config.vessels import BASE_VESSEL_SPECS


BASELINE_PHYSICS = {
    "v1": {
        "total_disp": 9.22,
        "payload_weight": 1.92,
        "battery_weight": 0.8,
        "max_power": 31.406960743782072,
        "cruise_power": 5.8200275165248305,
        "cruise_hours": 5.833333333333333,
        "brut_kwh": 33.95016051306151,
        "solar_area": 36.48,
        "solar_kwh": 43.775999999999996,
        "net_grid_kwh": 0.0,
        "cruise_diesel_lph": 5.559303458877735,
    },
    "v2": {
        "total_disp": 11.36,
        "payload_weight": 2.56,
        "battery_weight": 1.0,
        "max_power": 31.959493909890575,
        "cruise_power": 7.4529971829920605,
        "cruise_hours": 5.833333333333333,
        "brut_kwh": 43.47581690078702,
        "solar_area": 45.36000000000001,
        "solar_kwh": 54.43200000000001,
        "net_grid_kwh": 0.0,
        "cruise_diesel_lph": 6.996040554339534,
    },
    "v3": {
        "total_disp": 15.22,
        "payload_weight": 4.32,
        "battery_weight": 1.4000000000000001,
        "max_power": 33.815767980844704,
        "cruise_power": 7.885882805670861,
        "cruise_hours": 5.833333333333333,
        "brut_kwh": 46.00098303308002,
        "solar_area": 50.400000000000006,
        "solar_kwh": 60.480000000000004,
        "net_grid_kwh": 0.0,
        "cruise_diesel_lph": 6.996040554339534,
    },
}


@pytest.mark.parametrize("vessel_key", ["v1", "v2", "v3"])
def test_default_vessel_physics_regression(vessel_key):
  spec = deepcopy(BASE_VESSEL_SPECS[vessel_key])

  result = calc_calibrated_vessel_physics(
      spec,
      cruise_spd=6.0,
      d_miles=35.0,
      s_hours=8.0,
  )

  for field, expected in BASELINE_PHYSICS[vessel_key].items():
    assert getattr(result, field) == pytest.approx(expected)
