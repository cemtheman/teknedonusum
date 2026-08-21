import pandas as pd
import streamlit as st

from models.inputs import SimulationInputs
from models.results import FleetResult
from ui.formatting import format_integer_tr


def render_fleet_dashboard(
    vessel_specs,
    inputs: SimulationInputs,
    fleet: FleetResult,
):
  st.subheader("🚢 Filo Geneli Toplam Dönüşüm ve Finansman Özeti")
  f_kpi1, f_kpi2, f_kpi3, f_kpi4 = st.columns(4)
  with f_kpi1:
    st.metric("Hedef Dönüştürülecek Tekne", f"{fleet.total_vessels} Adet")
  with f_kpi2:
    st.metric("Toplam Filo Yolcu Kapasitesi", f"{fleet.total_capacity:,} Kişi")
  with f_kpi3:
    st.metric(
        "İhtiyaç Duyulan Toplam Hibe",
        f"₺{format_integer_tr(fleet.fleet_total_grant)}",
    )
  with f_kpi4:
    st.metric(
        "Toplam Net Özkaynak Yatırımı",
        f"₺{format_integer_tr(fleet.fleet_total_capex)}",
    )

  fleet_summary_df = pd.DataFrame({
      "Tekne Tipi & Kategori": [
          "Tip 1: 12m Monohull (Kooperatif %55)",
          "Tip 2: 13.5m Katamaran (Kooperatif %55)",
          "Tip 3: 14m Katamaran (Kooperatif %70)",
          "Tip 4A: 12m Monohull (Bireysel %40)",
          "Tip 4B: 13.5m Katamaran (Bireysel %40)",
          "TOPLAM",
      ],
      "Adet": [
          inputs.count_v1,
          inputs.count_v2,
          inputs.count_v3,
          inputs.count_v4_24,
          inputs.count_v4_32,
          fleet.total_vessels,
      ],
      "Birim Kapasite": [
          "24 Kişi", "32 Kişi", "54 Kişi", "24 Kişi", "32 Kişi", "-"
      ],
      "Toplam Kapasite": [
          f"{inputs.count_v1 * 24} Kişi",
          f"{inputs.count_v2 * 32} Kişi",
          f"{inputs.count_v3 * 54} Kişi",
          f"{inputs.count_v4_24 * 24} Kişi",
          f"{inputs.count_v4_32 * 32} Kişi",
          f"{fleet.total_capacity:,} Kişi",
      ],
      "Birim Maliyet (EUR)": [
          f"€{format_integer_tr(vessel_specs['v1']['totalCostEur'])}",
          f"€{format_integer_tr(vessel_specs['v2']['totalCostEur'])}",
          f"€{format_integer_tr(vessel_specs['v3']['totalCostEur'])}",
          f"€{format_integer_tr(vessel_specs['v4_24']['totalCostEur'])}",
          f"€{format_integer_tr(vessel_specs['v4_32']['totalCostEur'])}",
          "-",
      ],
      "Birim Maliyet (TL)": [
          f"₺{format_integer_tr(vessel_specs['v1']['totalCost'])}",
          f"₺{format_integer_tr(vessel_specs['v2']['totalCost'])}",
          f"₺{format_integer_tr(vessel_specs['v3']['totalCost'])}",
          f"₺{format_integer_tr(vessel_specs['v4_24']['totalCost'])}",
          f"₺{format_integer_tr(vessel_specs['v4_32']['totalCost'])}",
          "-",
      ],
      "Brüt Yatırım (TL)": [
          f"₺{format_integer_tr(inputs.count_v1 * vessel_specs['v1']['totalCost'])}",
          f"₺{format_integer_tr(inputs.count_v2 * vessel_specs['v2']['totalCost'])}",
          f"₺{format_integer_tr(inputs.count_v3 * vessel_specs['v3']['totalCost'])}",
          f"₺{format_integer_tr(inputs.count_v4_24 * vessel_specs['v4_24']['totalCost'])}",
          f"₺{format_integer_tr(inputs.count_v4_32 * vessel_specs['v4_32']['totalCost'])}",
          f"₺{format_integer_tr(fleet.fleet_total_cost)}",
      ],
      "Toplam Hibe Miktarı": [
          f"₺{format_integer_tr(inputs.count_v1 * fleet.grants_per_type['v1'])}",
          f"₺{format_integer_tr(inputs.count_v2 * fleet.grants_per_type['v2'])}",
          f"₺{format_integer_tr(inputs.count_v3 * fleet.grants_per_type['v3'])}",
          f"₺{format_integer_tr(inputs.count_v4_24 * fleet.grants_per_type['v4_24'])}",
          f"₺{format_integer_tr(inputs.count_v4_32 * fleet.grants_per_type['v4_32'])}",
          f"₺{format_integer_tr(fleet.fleet_total_grant)}",
      ],
      "Net Özkaynak İhtiyacı": [
          f"₺{format_integer_tr(inputs.count_v1 * (vessel_specs['v1']['totalCost'] - fleet.grants_per_type['v1']))}",
          f"₺{format_integer_tr(inputs.count_v2 * (vessel_specs['v2']['totalCost'] - fleet.grants_per_type['v2']))}",
          f"₺{format_integer_tr(inputs.count_v3 * (vessel_specs['v3']['totalCost'] - fleet.grants_per_type['v3']))}",
          f"₺{format_integer_tr(inputs.count_v4_24 * (vessel_specs['v4_24']['totalCost'] - fleet.grants_per_type['v4_24']))}",
          f"₺{format_integer_tr(inputs.count_v4_32 * (vessel_specs['v4_32']['totalCost'] - fleet.grants_per_type['v4_32']))}",
          f"₺{format_integer_tr(fleet.fleet_total_capex)}",
      ],
  })
  st.table(fleet_summary_df)

  co2_html = f"""
<div style="background-color: #ECFDF5; border: 1.5px solid #10B981; border-radius: 8px; padding: 14px 20px; text-align: center; margin-top: 10px; margin-bottom: 12px;">
    <p style="font-size: 1.25rem; font-weight: 700; color: #065F46; margin: 0;">🌱 Filo Dönüşümü İle Yıllık Toplam CO₂ Salınım Azaltımı: {fleet.fleet_total_co2_reduction:,.1f} Ton / Yıl</p>
    <p style="font-size: 1.05rem; font-weight: 600; color: #047857; margin: 4px 0 0 0;">🌳 Bu Çevresel Kazanç Yılda Yaklaşık <b>{fleet.equivalent_trees:,} Yetişkin Ağacın</b> Temizlediği Karbon Miktarına Eşdeğerdir.</p>
</div>
"""
  st.markdown(co2_html, unsafe_allow_html=True)

  solar_html = f"""
<div style="background-color: #EFF6FF; border: 1.5px solid #3B82F6; border-radius: 8px; padding: 14px 20px; text-align: center; margin-bottom: 20px;">
    <p style="font-size: 1.25rem; font-weight: 700; color: #1E40AF; margin: 0;">⚡ Filo Solar Destek ve Kıyı Şarj Dengesi</p>
    <p style="font-size: 0.95rem; font-weight: 600; color: #1D4ED8; margin: 4px 0 0 0;">📍 {inputs.location_name} · {inputs.season_start:%d.%m.%Y}–{inputs.season_end:%d.%m.%Y} · Sezon: {inputs.season_days} gün · PVGIS ort. {inputs.average_daily_specific_yield_kwh_per_kwp:.2f} kWh/kWp-gün</p>
    <p style="font-size: 1.05rem; font-weight: 600; color: #1D4ED8; margin: 4px 0 0 0;">☀️ Sezonluk PV Üretimi: <b>{fleet.fleet_annual_solar_kwh:,.0f} kWh</b> | 🔌 SOC-Normalize Sezonluk Kıyı Enerjisi: <b>{fleet.fleet_annual_grid_kwh:,.0f} kWh</b> | Günlük ortalama: <b>{fleet.fleet_daily_grid_kwh:,.1f} kWh/gün</b></p>
    <p style="font-size: 0.88rem; color: #1E40AF; margin: 5px 0 0 0;">Saatlik modelde PV önce aktif elektrik yükünü karşılar; kalan enerji bataryaya yönelir. Kıyı enerjisi batarya rezerv sınırı sonrasında oluşur ve sezon sonu SOC farkı başlangıç seviyesine normalize edilir.</p>
</div>
"""
  st.markdown(solar_html, unsafe_allow_html=True)
