"""Preliminary daily PV energy model using unrestricted static roof area.

The model does not resolve shading, roof curvature, orientation, temperature
profiles, partial shading, MPPT behavior, battery acceptance limits, seasonal
irradiation profiles, or moving-vessel orientation. Peak sun hours means daily
equivalent peak-sun-hours and is not silently interchangeable with a generic
sun-hours input. The derating factor represents aggregate temperature, wiring,
mismatch, dirt, controller, and related losses; it is not a verified manufacturer
or system value.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SolarEnergyResult:
  loa_m: float
  roof_length_fraction_of_loa: float
  roof_length_m: float
  usable_roof_width_m: float
  roof_area_m2: float
  panel_coverage_fraction: float
  panel_area_m2: float
  panel_efficiency: float
  reference_irradiance_kw_m2: float
  installed_pv_power_kwp: float
  peak_sun_hours: float
  derating_factor: float
  daily_solar_energy_kwh: float


def calculate_solar_energy(
    loa_m: float,
    roof_length_fraction_of_loa: float,
    usable_roof_width_m: float,
    panel_coverage_fraction: float,
    panel_efficiency: float,
    peak_sun_hours: float,
    derating_factor: float,
    reference_irradiance_kw_m2: float = 1.0,
) -> SolarEnergyResult:
  if not loa_m > 0:
    raise ValueError("loa_m must be positive")
  if not 0 < roof_length_fraction_of_loa <= 1:
    raise ValueError(
        "roof_length_fraction_of_loa must be greater than zero and at most one"
    )
  if not usable_roof_width_m > 0:
    raise ValueError("usable_roof_width_m must be positive")
  if not 0 < panel_coverage_fraction <= 1:
    raise ValueError("panel_coverage_fraction must be greater than zero and at most one")
  if not 0 < panel_efficiency <= 1:
    raise ValueError("panel_efficiency must be greater than zero and at most one")
  if not peak_sun_hours >= 0:
    raise ValueError("peak_sun_hours must be non-negative")
  if not 0 < derating_factor <= 1:
    raise ValueError("derating_factor must be greater than zero and at most one")
  if not reference_irradiance_kw_m2 > 0:
    raise ValueError("reference_irradiance_kw_m2 must be positive")

  roof_length_m = loa_m * roof_length_fraction_of_loa
  roof_area_m2 = roof_length_m * usable_roof_width_m
  panel_area_m2 = roof_area_m2 * panel_coverage_fraction
  installed_pv_power_kwp = (
      panel_area_m2 * reference_irradiance_kw_m2 * panel_efficiency
  )
  daily_solar_energy_kwh = (
      installed_pv_power_kwp * peak_sun_hours * derating_factor
  )

  return SolarEnergyResult(
      loa_m=loa_m,
      roof_length_fraction_of_loa=roof_length_fraction_of_loa,
      roof_length_m=roof_length_m,
      usable_roof_width_m=usable_roof_width_m,
      roof_area_m2=roof_area_m2,
      panel_coverage_fraction=panel_coverage_fraction,
      panel_area_m2=panel_area_m2,
      panel_efficiency=panel_efficiency,
      reference_irradiance_kw_m2=reference_irradiance_kw_m2,
      installed_pv_power_kwp=installed_pv_power_kwp,
      peak_sun_hours=peak_sun_hours,
      derating_factor=derating_factor,
      daily_solar_energy_kwh=daily_solar_energy_kwh,
  )
