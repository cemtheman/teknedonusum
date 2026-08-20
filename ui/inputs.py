import re
from datetime import date

import streamlit as st

from config.solar_assumptions import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
)
from models.inputs import SimulationInputs
from services.solar_resource import build_season_solar_resource
from ui.formatting import format_integer_tr


def _render_cost_input(label, value):
  displayed_value = st.text_input(label, value=format_integer_tr(value))
  if not isinstance(displayed_value, str):
    st.error("Maliyet metin olarak girilmelidir.")
    st.stop()
    return value

  normalized_value = displayed_value.strip()
  if not re.fullmatch(r"(?:\d+|\d{1,3}(?:\.\d{3})+)", normalized_value):
    st.error("Maliyet yalnızca tam sayı ve binlik ayraç olarak nokta içermelidir.")
    st.stop()
    return value

  parsed_value = int(normalized_value.replace(".", ""))

  if not 10000 <= parsed_value <= 1000000:
    st.error("Maliyet 10.000 € ile 1.000.000 € arasında olmalıdır.")
    st.stop()
    return value
  return parsed_value


def render_sidebar(live_eur, eur_is_live, live_diesel, diesel_is_live):
  with st.sidebar:
    st.header("⚙️ Simülasyon Girdileri")

    st.subheader("🚢 Filo Dönüşüm Hedefleri")
    st.caption("Kooperatif Üyesi Hedefleri (%55 & %70 Hibe)")
    count_v1 = st.number_input(
        "Tip 1 (12 m Tek Gövdeli - 24 Kişi) Adet",
        min_value=0, max_value=200, value=50, step=1,
    )
    count_v2 = st.number_input(
        "Tip 2 (13,5 m Katamaran - 32 Kişi) Adet",
        min_value=0, max_value=200, value=50, step=1,
    )
    count_v3 = st.number_input(
        "Tip 3 (14 m Katamaran - 54 Kişi) Adet",
        min_value=0, max_value=200, value=40, step=1,
    )

    st.caption("Kooperatif Dışı (Bireysel) Hedefler (%40 Hibe)")
    count_v4_24 = st.number_input(
        "Tip 4A (12 m Tek Gövdeli - 24 Kişi) Adet",
        min_value=0, max_value=200, value=30, step=1,
    )
    count_v4_32 = st.number_input(
        "Tip 4B (13,5 m Katamaran - 32 Kişi) Adet",
        min_value=0, max_value=200, value=20, step=1,
    )

    st.divider()
    st.subheader("💶 Anahtar Teslim Piyasa Bedelleri (EUR)")
    st.caption(
        "Bedeller gövde, elektrikli tahrik sistemi, batarya ve güneş "
        "panellerini kapsayan piyasa referanslarıdır. %8 ÖTV ve %20 KDV hariçtir. "
        "Tip 4A bedeli Tip 1 ile, Tip 4B bedeli Tip 2 ile aynıdır."
    )
    cost_eur_v1 = _render_cost_input(
        "Tip 1 & Tip 4A anahtar teslim bedeli (€)", 108100
    )
    cost_eur_v2 = _render_cost_input(
        "Tip 2 & Tip 4B anahtar teslim bedeli (€)", 144140
    )
    cost_eur_v3 = _render_cost_input("Tip 3 anahtar teslim bedeli (€)", 180180)

    st.divider()
    st.subheader("🌐 Canlı Piyasa ve Kurlar")
    st.caption("TCMB ve Aytemiz servislerinden otomatik güncellenir.")

    eur_rate = st.number_input(
        f"EUR / TRY Kuru {'🟢 Canlı TCMB' if eur_is_live else '🟡 Sabit'}",
        min_value=30.0, max_value=120.0, value=float(live_eur), step=0.1,
    )
    diesel_price = st.number_input(
        "Dizel Yakıt Fiyatı TL/L "
        f"{'🟢 Canlı Aytemiz' if diesel_is_live else '🟡 Sabit'}",
        min_value=30.0, max_value=180.0, value=float(live_diesel), step=0.1,
    )
    elec_price = st.number_input(
        "Liman Şebeke Elektrik Fiyatı (TL/kWh)",
        min_value=3.0, max_value=30.0, value=3.50, step=0.5,
    )

    st.subheader("☀️ Lokasyon, Solar Sezon ve Operasyon")
    st.caption(
        "Solar sezon tarih aralığıyla tanımlanır. Operasyon günü sayısı sezon "
        "uzunluğundan ayrıdır ve seçilen dönemde kaç gün rota yapıldığını belirtir."
    )
    location_name = st.text_input("Lokasyon", value=DEFAULT_LOCATION_NAME)
    latitude = st.number_input(
        "Enlem", min_value=-90.0, max_value=90.0,
        value=float(DEFAULT_LATITUDE), step=0.0001, format="%.4f",
    )
    longitude = st.number_input(
        "Boylam", min_value=-180.0, max_value=180.0,
        value=float(DEFAULT_LONGITUDE), step=0.0001, format="%.4f",
    )
    season_start = st.date_input(
        "Solar sezon başlangıcı", value=date(2026, 4, 1), format="DD.MM.YYYY"
    )
    season_end = st.date_input(
        "Solar sezon bitişi", value=date(2026, 9, 30), format="DD.MM.YYYY"
    )
    if season_end < season_start:
      st.error("Solar sezon bitiş tarihi başlangıç tarihinden önce olamaz.")
      st.stop()

    season_days = (season_end - season_start).days + 1
    operating_days = st.number_input(
        "Sezonluk planlanan operasyon / rota günü",
        min_value=1,
        max_value=season_days,
        value=min(150, season_days),
        step=1,
        help=(
            "Solar sezonun takvim uzunluğu değildir. Seçilen tarih aralığında "
            "kaç gün 35 NM gibi tanımlı günlük rotanın yapılacağını belirtir."
        ),
    )

    try:
      solar_resource = build_season_solar_resource(
          location_name, latitude, longitude, season_start, season_end
      )
    except Exception as exc:
      st.error(
          "PVGIS solar kaynağı alınamadı. Lokasyon/koordinatları ve internet "
          f"bağlantısını kontrol edin. Ayrıntı: {exc}"
      )
      st.stop()

    st.caption(
        f"PVGIS sezonu: {solar_resource.season_days} gün · ortalama özgül PV "
        f"üretimi {solar_resource.average_daily_specific_yield_kwh_per_kwp:.2f} "
        "kWh/kWp-gün"
    )

    daily_miles = st.number_input(
        "Günlük Rota Mesafesi (NM)",
        min_value=15.0, max_value=60.0, value=35.0, step=5.0,
    )
    cruise_speed = st.number_input(
        "Ortalama Seyir Hızı (Knot)",
        min_value=4.0, max_value=10.0, value=6.0, step=0.5,
    )

  return SimulationInputs(
      count_v1=count_v1,
      count_v2=count_v2,
      count_v3=count_v3,
      count_v4_24=count_v4_24,
      count_v4_32=count_v4_32,
      cost_eur_v1=cost_eur_v1,
      cost_eur_v2=cost_eur_v2,
      cost_eur_v3=cost_eur_v3,
      eur_rate=eur_rate,
      diesel_price=diesel_price,
      elec_price=elec_price,
      operating_days=operating_days,
      daily_miles=daily_miles,
      cruise_speed=cruise_speed,
      location_name=solar_resource.location_name,
      latitude=solar_resource.latitude,
      longitude=solar_resource.longitude,
      season_start=solar_resource.season_start,
      season_end=solar_resource.season_end,
      season_days=solar_resource.season_days,
      average_daily_specific_yield_kwh_per_kwp=(
          solar_resource.average_daily_specific_yield_kwh_per_kwp
      ),
      season_specific_yield_kwh_per_kwp=(
          solar_resource.season_specific_yield_kwh_per_kwp
      ),
      solar_resource_source=solar_resource.source,
      sun_hours=None,
  )
