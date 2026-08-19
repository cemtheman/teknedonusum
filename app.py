from copy import deepcopy

import numpy as np
import pandas as pd
import streamlit as st

from calculations.economics import calculate_vessel_economics
from calculations.fleet import calculate_fleet
from calculations.vessel_physics import calc_calibrated_vessel_physics
from config.vessels import BASE_VESSEL_SPECS
from services.market_data import fetch_aytemiz_diesel, fetch_tcmb_eur
from ui.fleet_dashboard import render_fleet_dashboard
from ui.inputs import render_sidebar


def build_vessel_specs(cost_eur_v1, cost_eur_v2, cost_eur_v3, eur_rate):
  vessel_specs = deepcopy(BASE_VESSEL_SPECS)
  costs_eur = {
      "v1": cost_eur_v1,
      "v2": cost_eur_v2,
      "v3": cost_eur_v3,
      "v4_24": cost_eur_v1,
      "v4_32": cost_eur_v2,
  }

  for vessel_key, base_spec in vessel_specs.items():
    cost_eur = costs_eur[vessel_key]
    spec = {}
    for field, value in base_spec.items():
      spec[field] = value
      if field == "C":
        spec["totalCostEur"] = cost_eur
        spec["totalCost"] = int(cost_eur * eur_rate)
      elif field == "grantRate":
        spec["maxGrant"] = int(cost_eur * eur_rate * value)
    vessel_specs[vessel_key] = spec

  return vessel_specs

# Page Configuration
st.set_page_config(
    page_title="Sessiz Akım — Quiet Current",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Header Section
st.markdown(
    '<p style="font-size: 1.8rem; font-weight: 700; color: #1E3A8A;'
    ' margin-bottom: 2px;">⚓ Sessiz Akım — Köyceğiz & Dalyan Elektrikli Filo'
    " Simülasyon Portalı</p>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size: 1.05rem; font-weight: 600; color: #2563EB;'
    ' margin-bottom: 6px;">Quiet Current — Köyceğiz & Dalyan e-Fleet Simulation'
    " Portal</p>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 20px;">Yönetmelik'
    " ve Kurul Kararlarıyla Uyumlu İnteraktif Fizibilite ve Hibe"
    " Simülatörü</p>",
    unsafe_allow_html=True,
)

# Fetch Online Live Data
live_eur, eur_is_live = fetch_tcmb_eur()
live_diesel, diesel_is_live = fetch_aytemiz_diesel()

# Sidebar Controls
inputs = render_sidebar(live_eur, eur_is_live, live_diesel, diesel_is_live)

# Dynamic Vessel Data Specs Construction
VESSEL_SPECS = build_vessel_specs(
    inputs.cost_eur_v1,
    inputs.cost_eur_v2,
    inputs.cost_eur_v3,
    inputs.eur_rate,
)


# --- Fleet Aggregate Calculations ---
counts = {
    "v1": inputs.count_v1,
    "v2": inputs.count_v2,
    "v3": inputs.count_v3,
    "v4_24": inputs.count_v4_24,
    "v4_32": inputs.count_v4_32,
}

fleet = calculate_fleet(
    VESSEL_SPECS,
    counts,
    inputs.cruise_speed,
    inputs.daily_miles,
    inputs.sun_hours,
    inputs.operating_days,
)

render_fleet_dashboard(VESSEL_SPECS, inputs, fleet)

st.divider()

# --- All Vessel Types Detailed Breakdown Section (Alt Alta) ---
st.subheader("📊 Tüm Tekne Tipleri İçin Tekil Detay Analizleri (Kalibre Edilmiş)")

for v_key, spec in VESSEL_SPECS.items():
  with st.expander(f"📌 {spec['name']}", expanded=True):
    p = calc_calibrated_vessel_physics(
        spec, inputs.cruise_speed, inputs.daily_miles, inputs.sun_hours
    )

    economics = calculate_vessel_economics(
        spec,
        p,
        inputs.eur_rate,
        inputs.diesel_price,
        inputs.elec_price,
        inputs.operating_days,
    )

    per_motor_peak_kw = p.max_power / spec["motors"]
    per_motor_cruise_kw = p.cruise_power / spec["motors"]

    if spec["motors"] == 2:
      motor_desc = (
          f"• IE5 Çift Sevk Sistemi (2x {per_motor_peak_kw:.1f} kW Zirve Güç)"
      )
      peak_power_str = (
          f"2x {per_motor_peak_kw:.1f} kW ({p.max_power:.1f} kW Toplam)"
      )
      cruise_power_str = (
          f"2x {per_motor_cruise_kw:.1f} kW ({p.cruise_power:.1f} kW Toplam)"
      )
    else:
      motor_desc = f"• IE5 Tek Sevk Sistemi ({p.max_power:.1f} kW Zirve Güç)"
      peak_power_str = f"{p.max_power:.1f} kW"
      cruise_power_str = f"{p.cruise_power:.1f} kW"

    motor_cost_tl = economics.motor_cost_tl
    solar_cost_tl = economics.solar_cost_tl
    bat_cost_tl = economics.bat_cost_tl
    infra_share_tl = economics.infra_share_tl
    hull_cost_tl = economics.hull_cost_tl
    grant_amount = economics.grant_amount
    net_capex = economics.net_capex
    old_diesel_cost = economics.old_diesel_cost
    old_maint_cost = economics.old_maint_cost
    old_total_annual = economics.old_total_annual
    new_elec_cost = economics.new_elec_cost
    new_degradation = economics.new_degradation
    new_maint_cost = economics.new_maint_cost
    new_total_annual = economics.new_total_annual
    net_savings = economics.net_savings
    payback_seasons = economics.payback_seasons
    payback_months = economics.payback_months
    net_co2 = economics.net_co2

    # Metric Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
      st.metric("Net Özkaynak CAPEX", f"₺{int(net_capex):,}")
    with kpi2:
      st.metric("Sezonluk Net Tasarruf", f"₺{int(net_savings):,}")
    with kpi3:
      st.metric(
          "Özkaynak Amortisman (ROI)",
          f"{payback_seasons:.1f} Sezon ({int(payback_months)} Ay)",
      )
    with kpi4:
      st.metric("Sezonluk CO2 Salınım Azaltımı", f"{net_co2:.1f} Ton")

    col_left, col_right = st.columns([6, 6])

    with col_left:
      st.markdown("**Yatırım Masrafları (CAPEX) ve Hibe Detayı**")
      capex_df = pd.DataFrame({
          "Maliyet Kalemi": [
              "Brüt Toplam Maliyet",
              "Alınan Devlet Hibesi",
              "Net Özkaynak (CAPEX)",
              "• Tekne Gövde & Genel Donatım Maliyeti",
              motor_desc,
              "• Hardtop Solar PV Tavan",
              "• Lityum Batarya Paketi",
              "• Altyapı Payı (1/150)",
          ],
          "Tutar (TL)": [
              f"₺{spec['totalCost']:,} (€{spec['totalCostEur']:,})",
              f"-₺{int(grant_amount):,}",
              f"₺{int(net_capex):,}",
              f"₺{int(hull_cost_tl):,}",
              f"₺{int(motor_cost_tl):,}",
              f"₺{int(solar_cost_tl):,}",
              f"₺{int(bat_cost_tl):,}",
              f"₺{int(infra_share_tl):,}",
          ],
          "Açıklama": [
              "Birim ihale maliyeti",
              spec["priority"],
              "Yatırımcı Net Sermayesi",
              "Gövde & iç donatım maliyeti",
              (
                  f"{spec['motors']}x Pod/Şaft sevk motoru"
                  f" ({'Çift hattı' if spec['motors']==2 else 'Tek hat'})"
              ),
              f"{p.solar_area:.1f} m² tavan paneli",
              f"{spec['batCapacity']} kWh LFP paketi",
              "Liman şarj & izleme payı",
          ],
      })
      st.table(capex_df)

    with col_right:
      st.markdown("**Sezonluk İşletme Giderleri (OPEX) ve Tasarruf Dökümü**")
      opex_df = pd.DataFrame({
          "Gider Kalemi": [
              f"Eski Ahşap Yakıt Giderleri ({inputs.cruise_speed:.1f} kt /"
              f" {p.cruise_diesel_lph:.2f} L/h)",
              "Eski Ahşap Sezonluk Bakım/Rektefiye",
              "ESKİ TEKNE SEZONLUK GİDERLER TOPLAMI",
              "Yeni Elektrikli Şebeke Şarj Masrafları",
              "Yeni Batarya Yıpranma Karşılığı",
              "Yeni Elektrikli Periyodik Bakım",
              "YENİ TEKNE SEZONLUK GİDER TOPLAMI",
              "SEZONLUK NET FİNANSAL TASARRUF",
          ],
          "Tutar (TL)": [
              f"₺{int(old_diesel_cost):,}",
              f"₺{int(old_maint_cost):,}",
              f"₺{int(old_total_annual):,}",
              f"₺{int(new_elec_cost):,}",
              f"₺{int(new_degradation):,}",
              f"₺{int(new_maint_cost):,}",
              f"₺{int(new_total_annual):,}",
              f"₺{int(net_savings):,}",
          ],
      })
      st.table(opex_df)

    st.markdown(
        "**⚡ Hidrodinamik ve Sevk Sistemi Kalibrasyonu**"
        f" *(Deplasman: {p.total_disp:.2f} Ton | Motor Düzeni:"
        f" {spec['motors']}x Sevk Hattı)*"
    )
    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
    with tech_col1:
      st.info(f"**10 Knots Zirve Güç:**\n\n{peak_power_str}")
    with tech_col2:
      st.info(
          f"**{inputs.cruise_speed:.1f} Knots Seyir Gücü:**\n\n{cruise_power_str} (Dizel:"
          f" {p.cruise_diesel_lph:.2f} L/h)"
      )
    with tech_col3:
      st.info(
          "**Günlük Solar PV Üretimi:**\n\n"
          f"{p.solar_kwh:.1f} kWh/gün ({inputs.sun_hours}s Güneş)"
      )
    with tech_col4:
      st.info(f"**Net Şebeke Şarj İhtiyacı:**\n\n{p.net_grid_kwh:.1f} kWh/gün")
