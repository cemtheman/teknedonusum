import pandas as pd
import streamlit as st

from calculations.vessel_detail_analysis import build_vessel_detail_analysis
from models.inputs import SimulationInputs
from ui.formatting import format_integer_tr


def _format_decimal_tr(value):
  return f"{value:.1f}".replace(".", ",")


def render_vessel_details(
    vessel_specs,
    inputs: SimulationInputs,
    typical_hourly_specific_pv=None,
):
  st.divider()
  st.subheader("💶 Tekne Bazlı Finansal Analizler")

  st.caption(
      "Teknik ön boyutlandırma üstteki karşılaştırma tablosunda tek kez "
      "sunulur. Bu bölüm yatırım, işletme gideri, tasarruf ve amortisman "
      "sonuçlarına odaklanır."
  )

  for v_key, spec in vessel_specs.items():
    with st.expander(
        f"📌 {spec['name']}",
        expanded=False,
    ):
      try:
        detail = build_vessel_detail_analysis(
            v_key,
            spec,
            inputs,
            typical_hourly_specific_pv=typical_hourly_specific_pv,
        )

      except (TypeError, ValueError):
        st.warning(
            "Bu tekne için detay analizi hesaplanamadı. v0.2 teknik zinciri "
            "5–10 knot hizmet hızı aralığında çalışır."
        )
        continue

      sizing = detail.sizing

      top_left, top_right = st.columns(2)

      with top_left:
        st.metric(
            "Hibe Sonrası Özkaynak Yatırımı",
            f"₺{format_integer_tr(detail.net_capex_tl)}",
        )

      with top_right:
        st.metric(
            "Sezonluk Net Tasarruf",
            f"₺{format_integer_tr(detail.net_savings_tl)}",
        )

      st.markdown(
          "<div style='height:6px'></div>",
          unsafe_allow_html=True,
      )

      bottom_left, bottom_right = st.columns(2)

      with bottom_left:
        st.metric(
            "Yatırımın Geri Dönüş Süresi",
            f"{detail.payback_seasons:.1f} Sezon "
            f"({int(detail.payback_months)} Ay)",
        )

      with bottom_right:
        st.metric(
            "Sezonluk CO2 Salınım Azaltımı",
            f"{detail.net_co2_tonnes:.1f} Ton",
        )

      st.markdown(
          "<div style='height:8px'></div>",
          unsafe_allow_html=True,
      )

      col_left, col_right = st.columns([6, 6])

      with col_left:
        st.markdown(
            "**Yatırım ve Hibe Özeti**"
        )

        capex_df = pd.DataFrame({
            "Kalem": [
                "Anahtar Teslim Piyasa Bedeli",
                "Alınan Devlet Hibesi",
                "Net Özkaynak (CAPEX)",
            ],
            "Tutar (TL)": [
                (
                    f"₺{format_integer_tr(spec['totalCost'])} "
                    f"(€{format_integer_tr(spec['totalCostEur'])})"
                ),
                f"-₺{format_integer_tr(detail.grant_amount_tl)}",
                f"₺{format_integer_tr(detail.net_capex_tl)}",
            ],
            "Açıklama": [
                (
                    "Gövde, tahrik sistemi, batarya ve güneş paneli "
                    "dahil piyasa bedeli"
                ),
                spec["priority"],
                (
                    "Anahtar teslim bedelden hibe düşüldükten sonraki "
                    "yatırımcı sermayesi"
                ),
            ],
        })

        st.table(
            capex_df
        )

      with col_right:
        st.markdown(
            "**Sezonluk İşletme Giderleri ve Tasarruf Dökümü**"
        )

        opex_df = pd.DataFrame({
            "Gider Kalemi": [
                (
                    f"Eski Tekne Yakıt Gideri "
                    f"({inputs.cruise_speed:.1f} kt / "
                    f"{detail.old_diesel_lph:.2f} L/h)"
                ),
                "Eski Tekne Sezonluk Bakım/Rektefiye",
                "ESKİ TEKNE SEZONLUK GİDERLER TOPLAMI",
                "Şebekeden Karşılanan Enerji Gideri",
                "Yeni Batarya Yıpranma Karşılığı",
                "Yeni Elektrikli Periyodik Bakım",
                "YENİ TEKNE SEZONLUK GİDER TOPLAMI",
                "SEZONLUK NET FİNANSAL TASARRUF",
            ],
            "Tutar (TL)": [
                f"₺{format_integer_tr(detail.old_diesel_cost_tl)}",
                f"₺{format_integer_tr(detail.old_maintenance_cost_tl)}",
                f"₺{format_integer_tr(detail.old_total_annual_tl)}",
                f"₺{format_integer_tr(detail.new_electricity_cost_tl)}",
                f"₺{format_integer_tr(detail.new_battery_degradation_tl)}",
                f"₺{format_integer_tr(detail.new_maintenance_cost_tl)}",
                f"₺{format_integer_tr(detail.new_total_annual_tl)}",
                f"₺{format_integer_tr(detail.net_savings_tl)}",
            ],
        })

        st.table(
            opex_df
        )

      st.caption(
          "Teknik güç, enerji talebi ve batarya sonuçları üstteki teknik "
          "karşılaştırmada özetlenmiştir. Tip 4A teknik olarak Tip 1, "
          "Tip 4B teknik olarak Tip 2 profilini kullanır."
      )