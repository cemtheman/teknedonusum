import pandas as pd
import streamlit as st

from calculations.vessel_detail_analysis import build_vessel_detail_analysis
from calculations.vessel_hourly_energy import (
    build_vessel_hourly_energy_balance,
    installed_pv_kwp,
)
from models.inputs import SimulationInputs
from ui.formatting import format_integer_tr


def _format_decimal_tr(value):
  return f"{value:.1f}".replace(".", ",")


def _format_decimal_tr_3(value):
  return f"{value:.3f}".replace(".", ",")


def _render_v1_hourly_energy_diagnostics(
    spec,
    inputs,
    typical_hourly_specific_pv,
):
  if typical_hourly_specific_pv is None:
    return

  energy = build_vessel_hourly_energy_balance(
      vessel_id="v1",
      spec=spec,
      cruise_speed=inputs.cruise_speed,
      daily_miles=inputs.daily_miles,
      season_start=inputs.season_start,
      season_end=inputs.season_end,
      typical_hourly_specific_pv=typical_hourly_specific_pv,
  )

  st.markdown("**🔎 Tip 1 Saatlik Solar–Batarya Enerji Muhasebesi**")
  st.caption(
      "Bu bölüm diagnostic amaçlıdır ve doğrudan saatlik PV → tahrik → "
      "batarya SOC → kıyı enerjisi simülasyonundan gelir."
  )

  energy_df = pd.DataFrame({
      "Enerji Akışı": [
          "Kurulu PV Gücü",
          "PVGIS Saatlik Sezonluk Üretim",
          "Sezonluk Tahrik Enerjisi",
          "PV → Doğrudan Tahrik",
          "PV → Batarya Girişi (şarj öncesi)",
          "PV → Batarya (depolanan)",
          "Şarj Dönüşüm Kaybı",
          "Batarya İçinden Çekilen Enerji",
          "Batarya → Tahrik",
          "Deşarj Dönüşüm Kaybı",
          "Kullanılamayan / Fazla PV",
          "Sezonluk Kıyı Şarjı",
          "Terminal SOC Düzeltmeli Kıyı Enerjisi",
          "Solar-Only Seyir Süresi",
      ],
      "Değer": [
          f"{_format_decimal_tr(installed_pv_kwp(spec))} kWp",
          f"{_format_decimal_tr(energy.season_solar_generation_kwh)} kWh",
          f"{_format_decimal_tr(energy.season_propulsion_kwh)} kWh",
          f"{_format_decimal_tr(energy.solar_direct_to_propulsion_kwh)} kWh",
          f"{_format_decimal_tr(energy.solar_to_battery_input_kwh)} kWh",
          f"{_format_decimal_tr(energy.battery_charge_from_solar_kwh)} kWh",
          f"{_format_decimal_tr(energy.charge_conversion_loss_kwh)} kWh",
          f"{_format_decimal_tr(energy.battery_storage_withdrawal_kwh)} kWh",
          f"{_format_decimal_tr(energy.battery_discharge_to_propulsion_kwh)} kWh",
          f"{_format_decimal_tr(energy.discharge_conversion_loss_kwh)} kWh",
          f"{_format_decimal_tr(energy.curtailed_solar_kwh)} kWh",
          f"{_format_decimal_tr(energy.shore_energy_kwh)} kWh",
          f"{_format_decimal_tr(energy.normalized_shore_energy_kwh)} kWh",
          f"{_format_decimal_tr(energy.solar_only_propulsion_hours)} saat",
      ],
  })
  st.table(energy_df)

  soc_df = pd.DataFrame({
      "SOC Kontrolü": [
          "Sezon Başlangıç SOC",
          "Sezon Minimum SOC",
          "Sezon Sonu SOC",
          "Başlangıç → Son SOC Farkı",
          "Terminal SOC Açığı",
          "Terminal SOC Geri Kazanım Kıyı Enerjisi",
      ],
      "kWh": [
          _format_decimal_tr(energy.initial_soc_kwh),
          _format_decimal_tr(energy.minimum_soc_kwh),
          _format_decimal_tr(energy.final_soc_kwh),
          _format_decimal_tr(energy.final_soc_kwh - energy.initial_soc_kwh),
          _format_decimal_tr(energy.terminal_soc_deficit_kwh),
          _format_decimal_tr(energy.terminal_soc_recovery_shore_kwh),
      ],
  })
  st.table(soc_df)

  balance_df = pd.DataFrame({
      "Enerji Korunumu Kontrolü": [
          "PV denge hatası",
          "Tahrik denge hatası",
          "Batarya denge hatası",
      ],
      "kWh": [
          _format_decimal_tr_3(energy.pv_balance_error_kwh),
          _format_decimal_tr_3(energy.propulsion_balance_error_kwh),
          _format_decimal_tr_3(energy.battery_balance_error_kwh),
      ],
  })
  st.table(balance_df)

  tolerance_kwh = 0.01
  balances_ok = all(
      abs(value) <= tolerance_kwh
      for value in (
          energy.pv_balance_error_kwh,
          energy.propulsion_balance_error_kwh,
          energy.battery_balance_error_kwh,
      )
  )
  if balances_ok:
    st.success("PV, tahrik ve batarya enerji dengeleri kapanıyor.")
  else:
    st.error(
        "Enerji korunumu kontrolü kapanmıyor. Bu sonuç mühendislik çıktısı "
        "olarak kullanılmamalıdır."
    )

  soc_delta = energy.final_soc_kwh - energy.initial_soc_kwh
  if abs(soc_delta) <= 0.5:
    st.success(
        "Sezon sonu SOC başlangıç SOC seviyesine yakındır; sezonluk kıyı "
        "enerjisi başlangıç bataryasından gizli enerji tüketimine dayanmıyor."
    )
  else:
    st.warning(
        "Sezon başlangıç ve son SOC seviyeleri arasında belirgin fark var. "
        "Bu nedenle ham kıyı enerjisinin yanında terminal SOC düzeltmeli "
        "kıyı enerjisi esas alınmalıdır."
    )


def render_vessel_details(
    vessel_specs,
    inputs: SimulationInputs,
    typical_hourly_specific_pv=None,
):
  st.divider()
  st.subheader("📊 Tüm Tekne Tipleri İçin Tekil Detay Analizleri")
  st.caption(
      "Teknik değerler Elektrikli Tahrik Ön Boyutlandırması ile aynı v0.2 "
      "hesap zincirinden gelir. Ekonomik değerler anahtar teslim piyasa bedeli "
      "ve açık işletme varsayımlarını kullanır."
  )

  for v_key, spec in vessel_specs.items():
    with st.expander(f"📌 {spec['name']}", expanded=False):
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
            "6–10 knot hizmet hızı aralığında çalışır."
        )
        continue

      sizing = detail.sizing

      kpi1, kpi2, kpi3, kpi4 = st.columns(4)
      with kpi1:
        st.metric(
            "Net Özkaynak CAPEX",
            f"₺{format_integer_tr(detail.net_capex_tl)}",
        )
      with kpi2:
        st.metric(
            "Sezonluk Net Tasarruf",
            f"₺{format_integer_tr(detail.net_savings_tl)}",
        )
      with kpi3:
        st.metric(
            "Özkaynak Amortisman (ROI)",
            f"{detail.payback_seasons:.1f} Sezon "
            f"({int(detail.payback_months)} Ay)",
        )
      with kpi4:
        st.metric(
            "Sezonluk CO2 Salınım Azaltımı",
            f"{detail.net_co2_tonnes:.1f} Ton",
        )

      col_left, col_right = st.columns([6, 6])

      with col_left:
        st.markdown("**Yatırım ve Hibe Özeti**")
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
                "Gövde, tahrik sistemi, batarya ve güneş paneli dahil piyasa bedeli",
                spec["priority"],
                "Anahtar teslim bedelden hibe düşüldükten sonraki yatırımcı sermayesi",
            ],
        })
        st.table(capex_df)

      with col_right:
        st.markdown("**Sezonluk İşletme Giderleri (OPEX) ve Tasarruf Dökümü**")
        opex_df = pd.DataFrame({
            "Gider Kalemi": [
                (
                    f"Eski Tekne Yakıt Gideri "
                    f"({inputs.cruise_speed:.1f} kt / "
                    f"{detail.old_diesel_lph:.2f} L/h)"
                ),
                "Eski Tekne Sezonluk Bakım/Rektefiye",
                "ESKİ TEKNE SEZONLUK GİDERLER TOPLAMI",
                "Yeni Elektrikli Şebeke Şarj Masrafları",
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
        st.table(opex_df)

      st.markdown("**⚡ Teknik ve Enerji Özeti — v0.2**")
      tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
      with tech_col1:
        st.info(
            "**Toplam Kurulu Motor Gücü:**\n\n"
            f"{_format_decimal_tr(
                sizing.reference_installed_mechanical_power_kw
            )} kW"
        )
      with tech_col2:
        st.info(
            f"**{inputs.cruise_speed:.1f} Knot Seyir Elektrik Gücü:**\n\n"
            f"{_format_decimal_tr(
                sizing.reference_electrical_input_power_kw
            )} kW"
        )
      with tech_col3:
        st.info(
            "**Günlük Tahrik Enerjisi / Gerekli Batarya:**\n\n"
            f"{_format_decimal_tr(
                sizing.reference_daily_propulsion_energy_kwh
            )} kWh/gün · "
            f"{_format_decimal_tr(
                sizing.reference_nominal_battery_capacity_kwh
            )} kWh"
        )
      with tech_col4:
        st.info(
            "**Saatlik PV / Kıyı Enerjisi:**\n\n"
            f"{_format_decimal_tr(detail.daily_solar_kwh)} / "
            f"{_format_decimal_tr(detail.daily_grid_kwh)} kWh/gün"
        )

      if v_key == "v1":
        _render_v1_hourly_energy_diagnostics(
            spec,
            inputs,
            typical_hourly_specific_pv,
        )

      st.caption(
          f"Teknik profil: {detail.technical_profile_id.upper()} · "
          f"Günlük rota: {_format_decimal_tr(inputs.daily_miles)} NM · "
          f"Tahmini seyir süresi: "
          f"{_format_decimal_tr(sizing.operating_hours_per_day)} saat/gün. "
          "Tip 4A teknik olarak Tip 1, Tip 4B teknik olarak Tip 2 profiliyle "
          "boyutlandırılır; hibe ve ekonomik kimlikleri ayrı tutulur."
      )
