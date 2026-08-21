"""Live PVGIS PVcalc vs seriescalc diagnostic.

Run in Codespace:
  python scripts/check_pvgis_consistency.py
"""

from datetime import date

from services.pvgis_crosscheck import compare_pvgis_seasonal_yields
from services.solar_hourly import (
    build_typical_hourly_profile,
    fetch_pvgis_hourly_specific_pv,
)
from services.solar_resource import build_season_solar_resource


LATITUDE = 36.8345
LONGITUDE = 28.6447
SEASON_START = date(2026, 4, 1)
SEASON_END = date(2026, 9, 30)
START_YEAR = 2020
END_YEAR = 2023


monthly = build_season_solar_resource(
    "Dalyan",
    LATITUDE,
    LONGITUDE,
    SEASON_START,
    SEASON_END,
)

points = fetch_pvgis_hourly_specific_pv(
    LATITUDE,
    LONGITUDE,
    START_YEAR,
    END_YEAR,
)
profile = build_typical_hourly_profile(points)

result = compare_pvgis_seasonal_yields(
    monthly.season_specific_yield_kwh_per_kwp,
    profile,
    SEASON_START,
    SEASON_END,
)

print("PVGIS PVcalc vs seriescalc seasonal cross-check")
print("------------------------------------------------")
print(
    "PVcalc seasonal yield : "
    f"{result.monthly_season_specific_yield_kwh_per_kwp:.2f} kWh/kWp"
)
print(
    "seriescalc seasonal   : "
    f"{result.hourly_season_specific_yield_kwh_per_kwp:.2f} kWh/kWp"
)
print(
    "absolute difference   : "
    f"{result.absolute_difference_kwh_per_kwp:.2f} kWh/kWp"
)
print(
    "relative difference   : "
    f"{result.relative_difference_percent:.2f}%"
)
print(f"hourly raw points      : {len(points)}")
print(f"typical profile buckets: {len(profile)}")

# Useful structural diagnostics: totals per historical year before averaging.
year_totals = {}
for point in points:
  if SEASON_START.month <= point.timestamp.month <= SEASON_END.month:
    year_totals.setdefault(point.timestamp.year, 0.0)
    year_totals[point.timestamp.year] += point.specific_power_kw_per_kwp

print("historical raw seasonal-ish totals by year:")
for year, total in sorted(year_totals.items()):
  print(f"  {year}: {total:.2f} kWh/kWp")
