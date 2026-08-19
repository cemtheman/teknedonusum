from models.results import VesselPhysicsResult


def calc_calibrated_vessel_physics(spec, cruise_spd, d_miles, s_hours):
  payload_weight = spec["capacity"] * 0.080  # Kişi başı 80 kg
  battery_weight = spec["batCapacity"] * 0.010  # LFP Batarya: 10 kg/kWh
  total_disp = spec["disp"] + payload_weight + battery_weight

  if spec["hull"] == "monohull":
    max_power = ((total_disp ** (2 / 3)) * (10**3)) / spec["C"]
    cruise_power = max_power * ((cruise_spd / 10.0) ** 3.3)
  else:
    max_power = ((total_disp**0.72) * (10**3)) / spec["C"]
    cruise_power = max_power * ((cruise_spd / 10.0) ** 2.85)

  cruise_hours = d_miles / cruise_spd
  brut_kwh = cruise_power * cruise_hours

  solar_area = spec["loa"] * spec["beam"] * 0.80
  solar_kwh = solar_area * 0.15 * s_hours
  net_grid_kwh = max(0.0, (brut_kwh / 0.95) - solar_kwh)

  max_diesel_lph = 30.0
  cruise_diesel_lph = (
      max_diesel_lph * ((cruise_spd / 10.0) ** 3.3)
      if spec["hull"] == "monohull"
      else max_diesel_lph * ((cruise_spd / 10.0) ** 2.85)
  )

  return VesselPhysicsResult(
      total_disp=total_disp,
      payload_weight=payload_weight,
      battery_weight=battery_weight,
      max_power=max_power,
      cruise_power=cruise_power,
      cruise_hours=cruise_hours,
      brut_kwh=brut_kwh,
      solar_area=solar_area,
      solar_kwh=solar_kwh,
      net_grid_kwh=net_grid_kwh,
      cruise_diesel_lph=cruise_diesel_lph,
  )
