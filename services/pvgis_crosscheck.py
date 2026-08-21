"""Cross-check PVGIS monthly PVcalc and hourly seriescalc seasonal yields."""

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class PVGISCrosscheckResult:
  monthly_season_specific_yield_kwh_per_kwp: float
  hourly_season_specific_yield_kwh_per_kwp: float
  absolute_difference_kwh_per_kwp: float
  relative_difference_percent: float


def sum_typical_hourly_season_yield(
    typical_hourly_specific_pv,
    season_start,
    season_end,
):
  """Sum hourly kW/kWp values as hourly kWh/kWp over a selected season."""
  if season_end < season_start:
    raise ValueError("season_end must not be before season_start")

  total = 0.0
  current = season_start
  while current <= season_end:
    for hour in range(24):
      value = float(
          typical_hourly_specific_pv.get(
              (current.month, current.day, hour),
              0.0,
          )
      )
      if value < 0:
        raise ValueError("hourly specific PV must not be negative")
      total += value
    current += timedelta(days=1)
  return total


def compare_pvgis_seasonal_yields(
    monthly_season_specific_yield_kwh_per_kwp,
    typical_hourly_specific_pv,
    season_start,
    season_end,
):
  monthly = float(monthly_season_specific_yield_kwh_per_kwp)
  if monthly <= 0:
    raise ValueError("monthly seasonal yield must be positive")

  hourly = sum_typical_hourly_season_yield(
      typical_hourly_specific_pv,
      season_start,
      season_end,
  )
  difference = hourly - monthly
  relative = difference / monthly * 100.0

  return PVGISCrosscheckResult(
      monthly_season_specific_yield_kwh_per_kwp=monthly,
      hourly_season_specific_yield_kwh_per_kwp=hourly,
      absolute_difference_kwh_per_kwp=difference,
      relative_difference_percent=relative,
  )
