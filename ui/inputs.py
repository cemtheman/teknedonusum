import re

import streamlit as st

from models.inputs import SimulationInputs
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
        "Tip 1 (12m Monohull - 24 Kişi) Adet",
        min_value=0,
        max_value=200,
        value=50,
        step=1,
    )
    count_v2 = st.number_input(
        "Tip 2 (13.5m Katamaran - 32 Kişi) Adet",
        min_value=0,
        max_value=200,
        value=50,
        step=1,
    )
    count_v3 = st.number_input(
        "Tip 3 (14m Katamaran - 54 Kişi) Adet",
        min_value=0,
        max_value=200,
        value=40,
        step=1,
    )

    st.caption("Kooperatif Dışı (Bireysel) Hedefler (%40 Hibe)")
    count_v4_24 = st.number_input(
        "Tip 4A (12m Monohull - 24 Kişi) Adet",
        min_value=0,
        max_value=200,
        value=30,
        step=1,
    )
    count_v4_32 = st.number_input(
        "Tip 4B (13.5m Katamaran - 32 Kişi) Adet",
        min_value=0,
        max_value=200,
        value=20,
        step=1,
    )

    st.divider()

    st.subheader("💶 Tekne Birim Maliyetleri (EUR)")
    st.caption(
        "Tip 4A maliyeti Tip1 ile, Tip 4B maliyeti Tip2 ile aynıdır."
    )
    cost_eur_v1 = _render_cost_input(
        "Tip 1 & Tip 4A (12m Monohull - 24 Kişi) Maliyeti (€)",
        108100,
    )
    cost_eur_v2 = _render_cost_input(
        "Tip 2 & Tip 4B (13.5m Katamaran - 32 Kişi) Maliyeti (€)",
        144140,
    )
    cost_eur_v3 = _render_cost_input(
        "Tip 3 (14m Katamaran - 54 Kişi) Maliyeti (€)",
        180180,
    )

    st.divider()

    st.subheader("🌐 Canlı Piyasa & Kurlar")
    st.caption("TCMB ve Aytemiz servislerinden otomatik güncellenir.")

    eur_rate = st.number_input(
        f"EUR / TRY Kuru {'🟢 Canlı TCMB' if eur_is_live else '🟡 Sabit'}",
        min_value=30.0,
        max_value=120.0,
        value=float(live_eur),
        step=0.1,
    )
    diesel_price = st.number_input(
        (
            "Dizel Yakıt Fiyatı TL/L"
            f" {'🟢 Canlı Aytemiz' if diesel_is_live else '🟡 Sabit'} "
        ),
        min_value=30.0,
        max_value=180.0,
        value=float(live_diesel),
        step=0.1,
    )
    elec_price = st.number_input(
        "Liman Şebeke Elektrik Fiyatı (TL/kWh)",
        min_value=3.0,
        max_value=30.0,
        value=3.50,
        step=0.5,
    )

    st.subheader("İklim ve Operasyon")
    operating_days = st.number_input(
        "Sezon Operasyon Gün Sayısı",
        min_value=30,
        max_value=360,
        value=180,
        step=10,
    )
    sun_hours = st.number_input(
        "Günlük Güneşlenme Süresi (Saat/Gün)",
        min_value=0.0,
        max_value=12.0,
        value=8.0,
        step=0.5,
    )
    daily_miles = st.number_input(
        "Günlük Rota Mesafesi (Mil)",
        min_value=15.0,
        max_value=60.0,
        value=35.0,
        step=5.0,
    )
    cruise_speed = st.number_input(
        "Ortalama Seyir Hızı (Knot)",
        min_value=4.0,
        max_value=10.0,
        value=6.0,
        step=0.5,
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
      sun_hours=sun_hours,
      daily_miles=daily_miles,
      cruise_speed=cruise_speed,
  )
