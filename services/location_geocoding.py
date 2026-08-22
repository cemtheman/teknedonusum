"""Resolve a user-entered location name to coordinates for solar-resource queries."""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


def parse_nominatim_first_result(payload):
  """Return (display_name, latitude, longitude) from the first search result."""
  if not isinstance(payload, list) or not payload:
    raise ValueError("location could not be resolved")

  row = payload[0]
  try:
    display_name = str(row["display_name"]).strip()
    latitude = float(row["lat"])
    longitude = float(row["lon"])
  except (KeyError, TypeError, ValueError) as exc:
    raise ValueError("location result is invalid") from exc

  if not display_name:
    raise ValueError("location display name is empty")
  if not -90.0 <= latitude <= 90.0:
    raise ValueError("resolved latitude is invalid")
  if not -180.0 <= longitude <= 180.0:
    raise ValueError("resolved longitude is invalid")

  return display_name, latitude, longitude


@st.cache_data(
    ttl=86400,
    show_spinner="Güncel lokasyon verisi alınıyor...",
)
def geocode_location(location_name):
  """Resolve one explicit location query through OpenStreetMap Nominatim."""
  query = str(location_name).strip()
  if not query:
    raise ValueError("location name must not be empty")

  params = {
      "q": query,
      "format": "jsonv2",
      "limit": 1,
      "addressdetails": 0,
  }
  request = Request(
      f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}",
      headers={
          "User-Agent": (
              "Sessiz-Akim/0.2 "
              "(https://github.com/cemtheman/teknedonusum)"
          )
      },
  )

  with urlopen(request, timeout=10) as response:
    payload = json.loads(response.read().decode("utf-8"))

  return parse_nominatim_first_result(payload)
