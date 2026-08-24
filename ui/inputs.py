import re
from datetime import date

import streamlit as st

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
    load_and_analyze_inventory_excel,
)
from config.operational_speed import (
    DEFAULT_OPERATION_SPEED_KNOTS,
    MAX_OPERATION_SPEED_KNOTS,
    MIN_OPERATION_SPEED_KNOTS,
)
from config.solar_assumptions import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
)
from models.inputs import SimulationInputs
from services.location_geocoding import geocode_location
from services.solar_resource import build_season_solar_resource
from ui.formatting import format_integer_tr
from ui.branding import render_sidebar_brand


def _render_cost_input(label, value):
  displayed_value = st.text_input(
      label,
      value=format_integer_tr(value),
  )

  if not isinstance(displayed_value, str):
    st.error("Maliyet metin olarak girilmelidir.")
    st.stop()
    return value

  normalized_value = displayed_value.strip()

  if not re.fullmatch(
      r"(?:\d+|\d{1,3}(?:\.\d{3})+)",
      normalized_value,
  ):
    st.error(
        "Maliyet yalnızca tam sayı ve binlik ayraç "
        "olarak nokta içermelidir."
    )
    st.stop()
    return value

  parsed_value = int(
      normalized_value.replace(".", "")
  )

  if not 10000 <= parsed_value <= 1000000:
    st.error(
        "Maliyet 10.000 € ile 1.000.000 € "
        "arasında olmalıdır."
    )
    st.stop()
    return value

  return parsed_value


def _phase_one_cooperative_counts(analysis):
  counts = {
      COOPERATIVE_MEMBER: 0,
      COOPERATIVE_NON_MEMBER: 0,
      COOPERATIVE_UNKNOWN: 0,
  }

  for recommendation in analysis.recommendations:
    if recommendation.conversion_phase != "Faz 1":
      continue

    status = recommendation.vessel.cooperative_status

    if status not in counts:
      status = COOPERATIVE_UNKNOWN

    counts[status] += 1

  return counts


def _inventory_plan_can_activate(analysis):
  counts = _phase_one_cooperative_counts(analysis)

  phase_one_total = sum(counts.values())

  return (
      phase_one_total > 0
      and counts[COOPERATIVE_MEMBER] == phase_one_total
  )


def render_sidebar(
    live_eur,
    eur_is_live,
    live_diesel,
    diesel_is_live,
):
  with st.sidebar:
    render_sidebar_brand()

    st.divider()

    st.header("⚙️ Simülasyon Girdileri")

    st.caption(
        "Aktif senaryoyu aşağıdaki başlıklardan düzenleyin. "
        "Tüm girdi grupları düzenli bir görünüm için kapalı başlar."
    )

    with st.expander(
        "🚢 Filo Dönüşüm Hedefleri",
        expanded=False,
    ):
      st.caption(
          "Kooperatif Üyesi Hedefleri (%55 & %70 Hibe)"
      )

      count_v1 = st.number_input(
          "Tip 1 (12 m Tek Gövdeli - 24 Kişi) Adet",
          min_value=0,
          max_value=200,
          value=50,
          step=1,
      )

      count_v2 = st.number_input(
          "Tip 2 (13,5 m Katamaran - 32 Kişi) Adet",
          min_value=0,
          max_value=200,
          value=50,
          step=1,
      )

      count_v3 = st.number_input(
          "Tip 3 (14 m Katamaran - 54 Kişi) Adet",
          min_value=0,
          max_value=200,
          value=40,
          step=1,
      )

      st.caption(
          "Kooperatif Dışı (Bireysel) Hedefler (%40 Hibe)"
      )

      count_v4_24 = st.number_input(
          "Tip 4A (12 m Tek Gövdeli - 24 Kişi) Adet",
          min_value=0,
          max_value=200,
          value=30,
          step=1,
      )

      count_v4_32 = st.number_input(
          "Tip 4B (13,5 m Katamaran - 32 Kişi) Adet",
          min_value=0,
          max_value=200,
          value=20,
          step=1,
      )

    with st.expander(
        "📊 Filo Envanteri & Dönüşüm Planı",
        expanded=False,
    ):
      st.caption(
          "Tekne listesini Excel formatında yükleyin. "
          "Envanter önce dönüşüm fazlarına ayrılır; Faz 1 "
          "yolcu motorları daha sonra hedef Tip 1/2/3 filo "
          "dağılımına dönüştürülür."
      )

      inventory_file = st.file_uploader(
          "Tekne Listesi (.xlsx)",
          type=["xlsx"],
          key="fleet_inventory_excel",
      )

      inventory_plan_active = False

      if inventory_file is None:
        st.session_state[
            "fleet_inventory_analysis"
        ] = None

        st.session_state[
            "fleet_inventory_plan_active"
        ] = False

      if inventory_file is not None:
        st.markdown(
            "**Hedef Faz 1 Filo Dağılımı**"
        )

        target_col1, target_col2, target_col3 = (
            st.columns(3)
        )

        with target_col1:
          target_v1_percent = st.number_input(
              "Tip 1 (%)",
              min_value=0,
              max_value=100,
              value=50,
              step=5,
              key="inventory_target_v1",
          )

        with target_col2:
          target_v2_percent = st.number_input(
              "Tip 2 (%)",
              min_value=0,
              max_value=100,
              value=30,
              step=5,
              key="inventory_target_v2",
          )

        with target_col3:
          target_v3_percent = st.number_input(
              "Tip 3 (%)",
              min_value=0,
              max_value=100,
              value=20,
              step=5,
              key="inventory_target_v3",
          )

        target_total_percent = (
            target_v1_percent
            + target_v2_percent
            + target_v3_percent
        )

        if target_total_percent != 100:
          st.session_state[
              "fleet_inventory_analysis"
          ] = None

          st.session_state[
              "fleet_inventory_plan_active"
          ] = False

          st.error(
              "Tip 1 + Tip 2 + Tip 3 hedef paylarının "
              "toplamı %100 olmalıdır."
          )

        else:
          try:
            inventory_analysis = (
                load_and_analyze_inventory_excel(
                    inventory_file,
                    target_shares={
                        "v1": (
                            target_v1_percent / 100.0
                        ),
                        "v2": (
                            target_v2_percent / 100.0
                        ),
                        "v3": (
                            target_v3_percent / 100.0
                        ),
                    },
                )
            )

          except Exception as exc:
            st.session_state[
                "fleet_inventory_analysis"
            ] = None

            st.session_state[
                "fleet_inventory_plan_active"
            ] = False

            st.error(
                f"Tekne listesi analiz edilemedi: {exc}"
            )

          else:
            st.session_state[
                "fleet_inventory_analysis"
            ] = inventory_analysis

            total_inventory = len(
                inventory_analysis.recommendations
            )

            phase_counts = (
                inventory_analysis.phase_counts
            )

            target_counts = (
                inventory_analysis
                .target_fleet
                .target_counts
            )

            cooperative_counts = (
                _phase_one_cooperative_counts(
                    inventory_analysis
                )
            )

            phase_one_total = sum(
                cooperative_counts.values()
            )

            phase_one_member = (
                cooperative_counts[
                    COOPERATIVE_MEMBER
                ]
            )

            phase_one_non_member = (
                cooperative_counts[
                    COOPERATIVE_NON_MEMBER
                ]
            )

            phase_one_unknown = (
                cooperative_counts[
                    COOPERATIVE_UNKNOWN
                ]
            )

            st.success(
                f"{total_inventory} tekne "
                "başarıyla analiz edildi."
            )

            st.caption(
                f"Faz 1: "
                f"{phase_counts.get('Faz 1', 0)} · "
                f"Faz 2: "
                f"{phase_counts.get('Faz 2', 0)} · "
                f"Faz 3: "
                f"{phase_counts.get('Faz 3', 0)} · "
                f"İnceleme: "
                f"{phase_counts.get('Özel İnceleme', 0)}"
            )

            st.markdown(
                "**Önerilen Faz 1 Hedef Filosu**"
            )

            st.caption(
                f"Tip 1: {target_counts['v1']} · "
                f"Tip 2: {target_counts['v2']} · "
                f"Tip 3: {target_counts['v3']}"
            )

            st.markdown(
                "**Faz 1 Kooperatif Durumu**"
            )

            st.caption(
                f"Toplam: {phase_one_total} · "
                f"Üye: {phase_one_member} · "
                f"Kooperatif dışı: "
                f"{phase_one_non_member} · "
                f"Bilinmiyor: {phase_one_unknown}"
            )

            activation_allowed = (
                _inventory_plan_can_activate(
                    inventory_analysis
                )
            )

            if activation_allowed:
              st.success(
                  "Faz 1 envanterindeki tüm teknelerin "
                  "kooperatif üyeliği doğrulanmıştır. "
                  "Mevcut Tip 1/2/3 finansman modeliyle "
                  "aktif senaryoya aktarım yapılabilir."
              )

            else:
              st.warning(
                  "Envanter teknik olarak analiz edildi ancak "
                  "ana simülasyon senaryosuna henüz aktarılamaz. "
                  "Faz 1 filosunda kooperatif dışı veya üyeliği "
                  "bilinmeyen tekne bulunduğunda bütün tekneleri "
                  "kooperatif üyesi kabul etmek yanlış hibe "
                  "hesabına yol açar."
              )

              st.caption(
                  "Teknik hedef filo önerisi yukarıda "
                  "kullanılabilir durumdadır. Aktif teknik filo "
                  "ile finansman filosu sonraki aşamada ayrı "
                  "veri yapıları olarak modellenerek bu sınırlama "
                  "kaldırılacaktır."
              )

            inventory_plan_active = st.checkbox(
                "Envanter planını aktif senaryo olarak kullan",
                value=False,
                disabled=not activation_allowed,
                help=(
                    "Mevcut ana simülasyon zinciri teknik filo "
                    "adetleri ile finansman statüsünü aynı veri "
                    "yapısında tuttuğundan, yalnız Faz 1'in "
                    "tamamı doğrulanmış kooperatif üyesiyse "
                    "aktif edilebilir."
                ),
                key="inventory_plan_active",
            )

            st.session_state[
                "fleet_inventory_plan_active"
            ] = inventory_plan_active

            if inventory_plan_active:
              count_v1 = int(
                  target_counts["v1"]
              )

              count_v2 = int(
                  target_counts["v2"]
              )

              count_v3 = int(
                  target_counts["v3"]
              )

              count_v4_24 = 0
              count_v4_32 = 0

              st.info(
                  "Aktif envanter senaryosu: "
                  f"Tip 1 {count_v1} · "
                  f"Tip 2 {count_v2} · "
                  f"Tip 3 {count_v3}. "
                  "Faz 1 kooperatif üyeliği doğrulanmış "
                  "olduğundan mevcut kooperatif finansman "
                  "profili kullanılıyor."
              )

    with st.expander(
        "⚓ Operasyon Profili",
        expanded=False,
    ):
      st.caption(
          "Günlük rota ve hizmet hızı teknik "
          "boyutlandırmanın ana operasyon girdileridir."
      )

      daily_miles = st.number_input(
          "Günlük Rota Mesafesi (deniz mili)",
          min_value=15.0,
          max_value=60.0,
          value=20.0,
          step=5.0,
      )

      cruise_speed = st.number_input(
          "Ortalama Seyir Hızı (Knot)",
          min_value=MIN_OPERATION_SPEED_KNOTS,
          max_value=MAX_OPERATION_SPEED_KNOTS,
          value=DEFAULT_OPERATION_SPEED_KNOTS,
          step=0.5,
      )

    with st.expander(
        "💶 Anahtar Teslim Piyasa Bedelleri",
        expanded=False,
    ):
      st.caption(
          "Bedeller gövde, elektrikli tahrik sistemi, "
          "batarya ve güneş panellerini kapsayan piyasa "
          "referanslarıdır. %8 ÖTV ve %20 KDV hariçtir. "
          "Tip 4A bedeli Tip 1 ile, Tip 4B bedeli "
          "Tip 2 ile aynıdır."
      )

      cost_eur_v1 = _render_cost_input(
          "Tip 1 & Tip 4A anahtar teslim bedeli (€)",
          108100,
      )

      cost_eur_v2 = _render_cost_input(
          "Tip 2 & Tip 4B anahtar teslim bedeli (€)",
          144140,
      )

      cost_eur_v3 = _render_cost_input(
          "Tip 3 anahtar teslim bedeli (€)",
          180180,
      )

    with st.expander(
        "🌐 Piyasa & Enerji Fiyatları",
        expanded=False,
    ):
      st.caption(
          "TCMB ve Aytemiz servislerinden otomatik "
          "güncellenir. Canlı kaynağa erişilemezse "
          "tanımlı yedek değer kullanılır."
      )

      eur_rate = st.number_input(
          (
              "EUR / TRY Kuru "
              f"{'🟢 Canlı TCMB' if eur_is_live else '🟡 Yedek değer'}"
          ),
          min_value=30.0,
          max_value=120.0,
          value=float(live_eur),
          step=0.1,
      )

      diesel_price = st.number_input(
          "Dizel Yakıt Fiyatı TL/L "
          f"{'🟢 Canlı Aytemiz' if diesel_is_live else '🟡 Yedek değer'}",
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

    with st.expander(
        "☀️ Lokasyon, Sezon & Solar Kaynak",
        expanded=False,
    ):
      st.caption(
          "Lokasyon solar kaynak koordinatlarını belirler. "
          "Sezon süresi, başlangıç ve bitiş tarihleri "
          "arasındaki takvim günlerinden otomatik hesaplanır."
      )

      if "solar_latitude" not in st.session_state:
        st.session_state[
            "solar_latitude"
        ] = float(DEFAULT_LATITUDE)

      if "solar_longitude" not in st.session_state:
        st.session_state[
            "solar_longitude"
        ] = float(DEFAULT_LONGITUDE)

      location_name = st.text_input(
          "Lokasyon",
          value=DEFAULT_LOCATION_NAME,
      )

      if st.button(
          "Lokasyonu Çözümle",
          use_container_width=True,
      ):
        try:
          (
              resolved_name,
              resolved_latitude,
              resolved_longitude,
          ) = geocode_location(
              location_name
          )

        except Exception as exc:
          st.error(
              f"Lokasyon çözümlenemedi: {exc}"
          )

        else:
          st.session_state[
              "solar_latitude"
          ] = resolved_latitude

          st.session_state[
              "solar_longitude"
          ] = resolved_longitude

          st.caption(
              f"Çözümlenen lokasyon: {resolved_name}"
          )

      latitude = st.number_input(
          "Enlem",
          min_value=-90.0,
          max_value=90.0,
          step=0.0001,
          format="%.4f",
          key="solar_latitude",
      )

      longitude = st.number_input(
          "Boylam",
          min_value=-180.0,
          max_value=180.0,
          step=0.0001,
          format="%.4f",
          key="solar_longitude",
      )

      season_start = st.date_input(
          "Sezon Başlangıcı",
          value=date(2026, 4, 1),
          format="DD.MM.YYYY",
      )

      season_end = st.date_input(
          "Sezon Bitişi",
          value=date(2026, 9, 30),
          format="DD.MM.YYYY",
      )

      if season_end < season_start:
        st.error(
            "Sezon bitiş tarihi başlangıç "
            "tarihinden önce olamaz."
        )
        st.stop()

      season_days = (
          season_end - season_start
      ).days + 1

      st.number_input(
          "Sezon Süresi (gün)",
          min_value=1,
          value=season_days,
          step=1,
          disabled=True,
      )

      operating_days = st.number_input(
          "Fiili Operasyon Günü",
          min_value=1,
          max_value=season_days,
          value=season_days,
          step=1,
          help=(
              "Teknenin seçilen sezon içinde fiilen "
              "hizmet verdiği gün sayısıdır. "
              "Güneş üretimi ise sezonun tüm takvim "
              "günleri için hesaplanır."
          ),
      )

      st.caption(
          f"Operasyon oranı: "
          f"%{operating_days / season_days * 100:.1f} · "
          f"{operating_days}/{season_days} gün"
      )

      try:
        solar_resource = (
            build_season_solar_resource(
                location_name,
                latitude,
                longitude,
                season_start,
                season_end,
            )
        )

      except Exception as exc:
        st.error(
            "PVGIS solar kaynağı alınamadı. "
            "Lokasyon/koordinatları ve internet "
            "bağlantısını kontrol edin. "
            f"Ayrıntı: {exc}"
        )
        st.stop()

      st.caption(
          f"PVGIS sezonu: "
          f"{solar_resource.season_days} gün · "
          "ortalama özgül PV üretimi "
          f"{solar_resource.average_daily_specific_yield_kwh_per_kwp:.2f} "
          "kWh/kWp-gün"
      )

    with st.expander(
        "🎯 Hibe Programı Bütçeleri",
        expanded=False,
    ):
      st.caption(
          "Dört ana kaynağın ilk yıl için programa "
          "ayrılabilecek toplam hibe bütçesini TL olarak girin."
      )

      grant_budget_ministry_tl = st.number_input(
          "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı (TL)",
          min_value=0,
          max_value=5_000_000_000,
          value=200_000_000,
          step=1_000_000,
      )

      grant_budget_geka_tl = st.number_input(
          "GEKA (TL)",
          min_value=0,
          max_value=5_000_000_000,
          value=0,
          step=1_000_000,
      )

      grant_budget_yikob_tl = st.number_input(
          "YİKOB (TL)",
          min_value=0,
          max_value=5_000_000_000,
          value=100_000_000,
          step=1_000_000,
      )

      grant_budget_zero_waste_tl = st.number_input(
          "Sıfır Atık Vakfı (TL)",
          min_value=0,
          max_value=5_000_000_000,
          value=100_000_000,
          step=1_000_000,
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
          solar_resource
          .average_daily_specific_yield_kwh_per_kwp
      ),
      season_specific_yield_kwh_per_kwp=(
          solar_resource
          .season_specific_yield_kwh_per_kwp
      ),
      solar_resource_source=(
          solar_resource.source
      ),
      sun_hours=None,
      grant_budget_ministry_tl=(
          grant_budget_ministry_tl
      ),
      grant_budget_geka_tl=(
          grant_budget_geka_tl
      ),
      grant_budget_yikob_tl=(
          grant_budget_yikob_tl
      ),
      grant_budget_zero_waste_tl=(
          grant_budget_zero_waste_tl
      ),
  )
