"""PVGIS hourly PV-production service for solar-assisted propulsion."""

from collections import defaultdict
from datetime import datetime
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
from models.solar_power import HourlyPVPoint


PVGIS_SERIES_URL = (
    f"https://re.jrc.ec.europa.eu/api/v{PVGIS_API_VERSION}/seriescalc"
)


def _parse_pvgis_time(value):
  """Parse PVGIS YYYYMMDD:HHMM timestamps."""
  try:
    return datetime.strptime(str(value), "%Y%m%d:%H%M")
  except ValueError as exc:
    raise ValueError(f"invalid PVGIS timestamp: {value}") from exc


def parse_hourly_specific_pv(payload):
  """Parse PVGIS hourly output into normalized kW/kWp points.

  The request is made with peakpower=1 kWp, so hourly P values in watts are
  divided by 1000 to obtain instantaneous kW per installed kWp.
  """
  try:
    rows = payload["outputs"]["hourly"]
  except (KeyError, TypeError) as exc:
    raise ValueError("PVGIS hourly output is missing") from exc

  points = []
  for row in rows:
    try:
      timestamp = _parse_pvgis_time(row["time"])
      power_w = float(row["P"])
    except (KeyError, TypeError, ValueError) as exc:
      raise ValueError("PVGIS hourly row is invalid") from exc
    if power_w < 0:
      raise ValueError("PVGIS hourly PV power must not be negative")
    points.append(
        HourlyPVPoint(
            timestamp=timestamp,
            specific_power_kw_per_kwp=power_w / 1000.0,
        )
    )

  if not points:
    raise ValueError("PVGIS hourly output is empty")
  return tuple(points)


@st.cache_data(
    ttl=86400,
    show_spinner="Saatlik güneş enerjisi profili alınıyor...",
)
def fetch_pvgis_hourly_specific_pv(
    latitude,
    longitude,
    startyear,
    endyear,
):
  """Fetch normalized hourly PV power using a horizontal 1 kWp system."""
  params = {
      "lat": float(latitude),
      "lon": float(longitude),
      "startyear": int(startyear),
      "endyear": int(endyear),
      "pvcalculation": 1,
      "peakpower": 1.0,
      "pvtechchoice": PVGIS_PV_TECH_CHOICE,
      "mountingplace": "free",
      "loss": PVGIS_SYSTEM_LOSS_PERCENT,
      "trackingtype": 0,
      "angle": PVGIS_PANEL_ANGLE_DEGREES,
      "aspect": PVGIS_PANEL_ASPECT_DEGREES,
      "localtime": 1,
      "outputformat": "json",
  }
  url = f"{PVGIS_SERIES_URL}?{urlencode(params)}"
  request = Request(url, headers={"User-Agent": "Sessiz-Akim/0.2"})

  with urlopen(request, timeout=20) as response:
    payload = json.loads(response.read().decode("utf-8"))

  return parse_hourly_specific_pv(payload)


def build_typical_hourly_profile(points):
  """Average historical PVGIS years by month/day/hour.

  Returns a mapping keyed by (month, day, hour) so a future user-selected
  season can use a climatological hourly PV profile without pretending that
  PVGIS forecasts future weather.
  """
  buckets = defaultdict(list)
  for point in points:
    key = (
        point.timestamp.month,
        point.timestamp.day,
        point.timestamp.hour,
    )
    buckets[key].append(point.specific_power_kw_per_kwp)

  return {
      key: sum(values) / len(values)
      for key, values in buckets.items()
  }
