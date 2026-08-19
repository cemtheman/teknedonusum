import re
import urllib.request
import xml.etree.ElementTree as ET

import streamlit as st


# Helper function to fetch TCMB EUR Rate online
@st.cache_data(ttl=3600)
def fetch_tcmb_eur():
  try:
    url = "https://www.tcmb.gov.tr/kurlar/today.xml"
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      xml_data = response.read()
    root = ET.fromstring(xml_data)
    for currency in root.findall("Currency"):
      if currency.attrib.get("CurrencyCode") == "EUR":
        forex_selling = currency.find("ForexSelling").text
        if forex_selling:
          return float(forex_selling), True
  except Exception:
    pass
  return 55.50, False  # Fallback varsayılan değer


# Helper function to fetch Aytemiz Mugla / Ortaca Diesel price online
@st.cache_data(ttl=3600)
def fetch_aytemiz_diesel():
  try:
    url = "https://www.aytemiz.com.tr/akaryakit-fiyatlari/motorin-fiyatlari/mugla-motorin-fiyati"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=8) as response:
      html = response.read().decode("utf-8")

    if "ORTACA" in html.upper():
      part = html.upper().split("ORTACA")[1][:500]
      matches = re.findall(r"(\d{2}[\.,]\d{2})", part)

      if len(matches) >= 2:
        diesel_price = float(matches[1].replace(",", "."))
        return diesel_price, True
      elif len(matches) == 1:
        return float(matches[0].replace(",", ".")), True
  except Exception:
    pass

  return 81.81, False  # Fallback varsayılan motorin değeri
