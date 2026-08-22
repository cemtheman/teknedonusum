"""PVGIS-backed seasonal solar resource service."""

from datetime import date, timedelta
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

from config.solar_assumptions import (
    PVGIS_API_VERSION,
    PVGIS_PANEL_ANGLE_DEGREES,
    PVGIS_PANEL_ASPECT_DEGREES,
    PVGIS_PV_TECH_CHOICE,
    PVGIS_SYSTEM_LOSS_PERCENT,
)
from models.season_solar import SeasonSolarResource


PVGIS_BASE_URL = (
    f"https://re.jrc.ec.europa.eu/api/v{PVGIS_API_VERSION}/PVcalc"
)


def parse_monthly_specific_yield(payload):
  """Return month -> average daily PV yield for a 1 kWp fixed system."""
  try:
    rows = payload["outputs"]["monthly"]["fixed"]
  except (KeyError, TypeError) as exc:
    raise ValueError("PVGIS monthly fixed output is missing") from exc

  monthly = {}
  for row in rows:
    try:
      month = int(row["month"])
      daily_yield = float(row["E_d"])
    except (KeyError, TypeError, ValueError) as exc:
      raise ValueError("PVGIS monthly row is invalid") from exc
    if not 1 <= month <= 12 or daily_yield <= 0:
      raise ValueError("PVGIS monthly yield must be positive")
    monthly[month] = daily_yield

  if set(monthly) != set(range(1, 13)):
    raise ValueError("PVGIS response must contain all 12 months")
  return monthly


@st.cache_data(
    ttl=86400,
    show_spinner="Güneş enerjisi verisi alınıyor...",
)
def fetch_pvgis_monthly_specific_yield(latitude, longitude):
  """Fetch average monthly specific PV yield for a horizontal 1 kWp system."""
  params = {
      "lat": float(latitude),
      "lon": float(longitude),
      "peakpower": 1.0,
      "loss": PVGIS_SYSTEM_LOSS_PERCENT,
      "pvtechchoice": PVGIS_PV_TECH_CHOICE,
      "mountingplace": "free",
      "fixed": 1,
      "angle": PVGIS_PANEL_ANGLE_DEGREES,
      "aspect": PVGIS_PANEL_ASPECT_DEGREES,
      "outputformat": "json",
  }
  url = f"{PVGIS_BASE_URL}?{urlencode(params)}"
  request = Request(url, headers={"User-Agent": "Sessiz-Akim/0.2"})

  with urlopen(request, timeout=10) as response:
    payload = json.loads(response.read().decode("utf-8"))

  return parse_monthly_specific_yield(payload)


def build_season_solar_resource(
    location_name,
    latitude,
    longitude,
    season_start,
    season_end,
    *,
    monthly_specific_yield=None,
):
  """Convert PVGIS monthly climatology into the selected date-range resource."""
  if not isinstance(season_start, date) or not isinstance(season_end, date):
    raise TypeError("season_start and season_end must be date objects")
  if season_end < season_start:
    raise ValueError("season_end must not be before season_start")

  monthly = (
      fetch_pvgis_monthly_specific_yield(latitude, longitude)
      if monthly_specific_yield is None
      else monthly_specific_yield
  )
  if set(monthly) != set(range(1, 13)):
    raise ValueError("monthly_specific_yield must contain months 1..12")

  current = season_start
  total_specific_yield = 0.0
  season_days = 0
  while current <= season_end:
    daily_yield = float(monthly[current.month])
    if daily_yield <= 0:
      raise ValueError("monthly specific yield must be positive")
    total_specific_yield += daily_yield
    season_days += 1
    current += timedelta(days=1)

  return SeasonSolarResource(
      location_name=str(location_name).strip(),
      latitude=float(latitude),
      longitude=float(longitude),
      season_start=season_start,
      season_end=season_end,
      season_days=season_days,
      average_daily_specific_yield_kwh_per_kwp=(
          total_specific_yield / season_days
      ),
      season_specific_yield_kwh_per_kwp=total_specific_yield,
      source=(
          f"PVGIS {PVGIS_API_VERSION} · {PVGIS_PV_TECH_CHOICE} · "
          f"%{PVGIS_SYSTEM_LOSS_PERCENT:.0f} sistem kaybı · yatay panel"
      ),
  )
