"""Instantaneous DC-bus power sharing for solar-assisted propulsion."""

from models.solar_power import PropulsionPowerSplit


def split_propulsion_power(propulsion_demand_kw, solar_available_kw):
  """Allocate solar power to propulsion before drawing from the battery.

  This intentionally models the field-observed architecture:
  solar -> DC bus / propulsion first; battery supplies only the deficit.
  Surplus solar remains available for battery charging or other loads.
  """
  propulsion_demand_kw = float(propulsion_demand_kw)
  solar_available_kw = float(solar_available_kw)

  if propulsion_demand_kw < 0:
    raise ValueError("propulsion_demand_kw must not be negative")
  if solar_available_kw < 0:
    raise ValueError("solar_available_kw must not be negative")

  solar_to_propulsion_kw = min(
      propulsion_demand_kw,
      solar_available_kw,
  )
  battery_discharge_kw = max(
      0.0,
      propulsion_demand_kw - solar_to_propulsion_kw,
  )
  solar_surplus_kw = max(
      0.0,
      solar_available_kw - solar_to_propulsion_kw,
  )

  return PropulsionPowerSplit(
      propulsion_demand_kw=propulsion_demand_kw,
      solar_available_kw=solar_available_kw,
      solar_to_propulsion_kw=solar_to_propulsion_kw,
      battery_discharge_kw=battery_discharge_kw,
      solar_surplus_kw=solar_surplus_kw,
      solar_only_propulsion=(
          propulsion_demand_kw > 0
          and battery_discharge_kw == 0.0
      ),
  )


def available_solar_power_kw(
    installed_pv_kwp,
    specific_power_kw_per_kwp,
):
  installed_pv_kwp = float(installed_pv_kwp)
  specific_power_kw_per_kwp = float(specific_power_kw_per_kwp)

  if installed_pv_kwp < 0:
    raise ValueError("installed_pv_kwp must not be negative")
  if specific_power_kw_per_kwp < 0:
    raise ValueError("specific_power_kw_per_kwp must not be negative")

  return installed_pv_kwp * specific_power_kw_per_kwp
