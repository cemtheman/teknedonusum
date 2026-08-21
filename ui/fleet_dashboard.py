import pandas as pd
import streamlit as st

from models.inputs import SimulationInputs
from models.results import FleetResult
from ui.formatting import format_integer_tr


def build_fleet_distribution_chart_data(inputs: SimulationInputs):
  rows = [
      ("12 m Tek Gövdeli · 24 yolcu", "Kooperatif Üyesi", inputs.count_v1, "K1", "#0F766E", 1),
      ("13,5 m Katamaran · 32 yolcu", "Kooperatif Üyesi", inputs.count_v2, "K2", "#22C55E", 2),
      ("14 m Katamaran · 54 yolcu", "Kooperatif Üyesi", inputs.count_v3, "K3", "#F59E0B", 3),
      ("12 m Tek Gövdeli · 24 yolcu", "Kooperatif Dışı", inputs.count_v4_24, "D1", "#2563EB", 4),
      ("13,5 m Katamaran · 32 yolcu", "Kooperatif Dışı", inputs.count_v4_32, "D2", "#7C3AED", 5),
  ]

  total = sum(count for _, _, count, _, _, _ in rows)
  data = []
  for vessel_type, status, count, code, color, order in rows:
    share = (100.0 * count / total) if total else 0.0
    data.append({
        "Tekne Türü": vessel_type,
        "Statü": status,
        "Adet": count,
        "Kod": code,
        "Renk": color,
        "Sıra": order,
        "Pay (%)": share,
        "Etiket": f"{code} · {count}",
    })
  return pd.DataFrame(data)


def build_fleet_type_summary(inputs: SimulationInputs):
  rows = [
      {
          "Tekne Türü": "12 m Tek Gövdeli · 24 yolcu",
          "Kooperatif": inputs.count_v1,
          "Kooperatif Dışı": inputs.count_v4_24,
      },
      {
          "Tekne Türü": "13,5 m Katamaran · 32 yolcu",
          "Kooperatif": inputs.count_v2,
          "Kooperatif Dışı": inputs.count_v4_32,
      },
      {
          "Tekne Türü": "14 m Katamaran · 54 yolcu",
          "Kooperatif": inputs.count_v3,
          "Kooperatif Dışı": 0,
      },
  ]

  total = sum(row["Kooperatif"] + row["Kooperatif Dışı"] for row in rows)
  for row in rows:
    row["Toplam"] = row["Kooperatif"] + row["Kooperatif Dışı"]
    row["Filo Payı (%)"] = (
        100.0 * row["Toplam"] / total
        if total else 0.0
    )
  return pd.DataFrame(rows)


def _metric_card(icon, label, value, accent):
  return f"""
  <div style="
      border:1px solid #E2E8F0;
      border-radius:14px;
      background:#FFFFFF;
      padding:18px 20px;
      min-height:112px;
      display:flex;
      align-items:center;
      gap:16px;
      box-shadow:0 1px 2px rgba(15,23,42,0.03);">
    <div style="
        font-size:2rem;
        width:50px;
        text-align:center;">{icon}</div>
    <div>
      <div style="
          color:#334155;
          font-size:0.82rem;
          font-weight:650;
          margin-bottom:5px;">{label}</div>
      <div style="
          color:{accent};
          font-size:1.75rem;
          line-height:1;
          font-weight:800;">{value}</div>
    </div>
  </div>
  """


def _render_fleet_top_kpis(fleet: FleetResult):
  c1, c2, c3, c4 = st.columns(4)
  cards = [
      (
          c1,
          "🚤",
          "Hedef Dönüştürülecek Tekne",
          f"{fleet.total_vessels} Adet",
          "#0F172A",
      ),
      (
          c2,
          "👥",
          "Toplam Filo Yolcu Kapasitesi",
          f"{fleet.total_capacity:,} Kişi",
          "#0F172A",
      ),
      (
          c3,
          "🎁",
          "İhtiyaç Duyulan Toplam Hibe",
          f"₺{format_integer_tr(fleet.fleet_total_grant)}",
          "#0F172A",
      ),
      (
          c4,
          "🪙",
          "Toplam Net Özkaynak Yatırımı",
          f"₺{format_integer_tr(fleet.fleet_total_capex)}",
          "#0F172A",
      ),
  ]
  for column, icon, label, value, accent in cards:
    with column:
      st.markdown(
          _metric_card(icon, label, value, accent),
          unsafe_allow_html=True,
      )


def _vessel_icon_svg(kind, color):
  if kind == "monohull":
    return f"""
    <svg viewBox="0 0 64 40" width="42" height="28" aria-hidden="true">
      <path d="M8 24h48l-7 9H17z" fill="{color}"/>
      <path d="M17 19h28l5 5H13z" fill="{color}" opacity="0.9"/>
      <rect x="24" y="11" width="18" height="8" rx="2" fill="{color}"/>
      <rect x="28" y="13" width="5" height="4" rx="1" fill="white"/>
      <rect x="35" y="13" width="5" height="4" rx="1" fill="white"/>
      <path d="M9 35c7 3 13 3 20 0 7 3 13 3 20 0" fill="none"
            stroke="{color}" stroke-width="2" stroke-linecap="round"/>
    </svg>
    """

  if kind == "catamaran_32":
    return f"""
    <svg viewBox="0 0 64 40" width="44" height="28" aria-hidden="true">
      <path d="M8 26h20l-5 8H12z" fill="{color}"/>
      <path d="M36 26h20l-5 8H41z" fill="{color}"/>
      <path d="M16 20h32l6 6H10z" fill="{color}" opacity="0.92"/>
      <rect x="22" y="11" width="20" height="9" rx="2" fill="{color}"/>
      <rect x="25" y="13" width="6" height="4" rx="1" fill="white"/>
      <rect x="33" y="13" width="6" height="4" rx="1" fill="white"/>
      <path d="M10 36c6 2 11 2 16 0M38 36c6 2 11 2 16 0" fill="none"
            stroke="{color}" stroke-width="2" stroke-linecap="round"/>
    </svg>
    """

  return f"""
  <svg viewBox="0 0 64 40" width="46" height="30" aria-hidden="true">
    <path d="M6 27h22l-5 8H10z" fill="{color}"/>
    <path d="M36 27h22l-5 8H41z" fill="{color}"/>
    <path d="M13 20h38l6 7H7z" fill="{color}" opacity="0.94"/>
    <rect x="18" y="9" width="28" height="11" rx="2" fill="{color}"/>
    <rect x="22" y="12" width="6" height="4" rx="1" fill="white"/>
    <rect x="30" y="12" width="6" height="4" rx="1" fill="white"/>
    <rect x="38" y="12" width="5" height="4" rx="1" fill="white"/>
    <path d="M9 37c6 2 11 2 17 0M38 37c6 2 11 2 17 0" fill="none"
          stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  </svg>
  """


def _fleet_donut_svg(inputs: SimulationInputs):
  import math

  data = build_fleet_distribution_chart_data(inputs)
  nonzero = data[data["Adet"] > 0].copy()
  total = float(nonzero["Adet"].sum())

  if total <= 0:
    return ""

  cx = 210
  cy = 210
  radius = 132
  stroke_width = 74
  circumference = 2 * math.pi * radius

  segments = []
  labels = []
  offset = 0.0

  for row in nonzero.to_dict("records"):
    fraction = row["Adet"] / total
    dash = fraction * circumference
    gap = circumference - dash
    segments.append(
        (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
            f'stroke="{row["Renk"]}" stroke-width="{stroke_width}" '
            f'stroke-dasharray="{dash:.4f} {gap:.4f}" '
            f'stroke-dashoffset="{-offset:.4f}" '
            f'transform="rotate(-90 {cx} {cy})" />'
        )
    )

    mid_fraction = (offset + dash / 2) / circumference
    angle = -math.pi / 2 + 2 * math.pi * mid_fraction
    label_radius = radius
    x = cx + label_radius * math.cos(angle)
    y = cy + label_radius * math.sin(angle)

    share = 100.0 * fraction
    labels.append(
        f'<text x="{x:.1f}" y="{y - 7:.1f}" text-anchor="middle" '
        f'font-size="19" font-weight="800" fill="white" '
        f'stroke="#0F172A" stroke-width="0.5" paint-order="stroke">'
        f'{row["Kod"]}</text>'
    )
    labels.append(
        f'<text x="{x:.1f}" y="{y + 15:.1f}" text-anchor="middle" '
        f'font-size="17" font-weight="800" fill="white" '
        f'stroke="#0F172A" stroke-width="0.45" paint-order="stroke">'
        f'{int(row["Adet"])} · %{share:.1f}</text>'
    )

    offset += dash

  total_int = int(total)
  return (
      '<div style="display:flex;justify-content:center;width:100%;">'
      '<svg viewBox="0 0 420 420" '
      'style="width:100%;max-width:430px;height:auto;overflow:visible;" '
      'role="img" aria-label="Filo kompozisyonu donut grafiği">'
      + "".join(segments)
      + "".join(labels)
      + f'<text x="{cx}" y="{cy - 3}" text-anchor="middle" '
        'font-size="44" font-weight="850" fill="#0F172A">'
        f'{total_int}</text>'
      + f'<text x="{cx}" y="{cy + 29}" text-anchor="middle" '
        'font-size="17" font-weight="700" fill="#475569">'
        'Toplam Tekne</text>'
      + '</svg></div>'
  )


def _render_fleet_donut(inputs: SimulationInputs):
  html = _fleet_donut_svg(inputs)
  if not html:
    st.info("Filo dağılımı için en az bir tekne adedi girilmelidir.")
    return
  st.markdown(html, unsafe_allow_html=True)


def _legend_card(row):
  return f"""
  <div style="
      display:flex;
      align-items:center;
      gap:11px;
      padding:10px 12px;
      margin-bottom:8px;
      border:1px solid #E2E8F0;
      border-radius:11px;
      background:#FFFFFF;">
    <div style="
        width:38px;
        height:38px;
        border-radius:50%;
        background:{row['Renk']};
        color:#FFFFFF;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:0.82rem;
        font-weight:800;">{row['Kod']}</div>
    <div style="flex:1;min-width:0;">
      <div style="
          font-size:0.88rem;
          font-weight:750;
          color:#0F172A;">{row['Statü']}</div>
      <div style="
          font-size:0.76rem;
          color:#475569;
          line-height:1.25;">{row['Tekne Türü']}</div>
    </div>
    <div style="text-align:right;min-width:48px;">
      <div style="
          font-size:0.95rem;
          font-weight:800;
          color:{row['Renk']};">{row['Adet']}</div>
      <div style="
          font-size:0.72rem;
          color:#64748B;">%{row['Pay (%)']:.1f}</div>
    </div>
  </div>
  """


def _render_fleet_legend(inputs: SimulationInputs):
  st.markdown("**Grafik Anahtarı**")
  for row in build_fleet_distribution_chart_data(inputs).to_dict("records"):
    st.markdown(_legend_card(row), unsafe_allow_html=True)


def _summary_table_html(inputs: SimulationInputs):
  summary = build_fleet_type_summary(inputs)
  total_coop = int(summary["Kooperatif"].sum())
  total_non = int(summary["Kooperatif Dışı"].sum())
  total = int(summary["Toplam"].sum())

  row_styles = [
      {
          "color": "#0F766E",
          "bg": "#ECFDF5",
          "kind": "monohull",
      },
      {
          "color": "#22C55E",
          "bg": "#F0FDF4",
          "kind": "catamaran_32",
      },
      {
          "color": "#F59E0B",
          "bg": "#FFFBEB",
          "kind": "catamaran_54",
      },
  ]

  html = [
      '<div style="border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;background:#FFFFFF;">',
      '<table style="width:100%;border-collapse:collapse;font-size:0.79rem;">',
      '<thead><tr style="background:#F8FAFC;color:#334155;">',
      '<th style="text-align:left;padding:12px 10px;">Tekne türü</th>',
      '<th style="padding:12px 7px;text-align:center;">Kooperatif</th>',
      '<th style="padding:12px 7px;text-align:center;">Koop. Dışı</th>',
      '<th style="padding:12px 7px;text-align:center;">Toplam</th>',
      '<th style="padding:12px 7px;text-align:center;">Filo Payı</th>',
      '</tr></thead><tbody>',
  ]

  for index, row in summary.iterrows():
    style = row_styles[index]
    icon = _vessel_icon_svg(style["kind"], style["color"])
    html.extend([
        '<tr style="border-top:1px solid #E2E8F0;">',
        (
            '<td style="text-align:left;padding:12px 10px;color:#0F172A;">'
            '<div style="display:flex;align-items:center;gap:9px;">'
            f'<span style="width:52px;height:38px;border-radius:9px;'
            f'background:{style["bg"]};display:inline-flex;align-items:center;'
            f'justify-content:center;flex:0 0 52px;">{icon}</span>'
            '<span style="font-weight:750;line-height:1.25;">'
            f'{row["Tekne Türü"]}</span>'
            '</div></td>'
        ),
        (
            '<td style="padding:13px 7px;text-align:center;color:#15803D;'
            f'font-weight:800;">{int(row["Kooperatif"])}</td>'
        ),
        (
            '<td style="padding:13px 7px;text-align:center;color:#2563EB;'
            f'font-weight:800;">{int(row["Kooperatif Dışı"])}</td>'
        ),
        (
            '<td style="padding:13px 7px;text-align:center;font-weight:800;">'
            f'{int(row["Toplam"])}</td>'
        ),
        (
            '<td style="padding:13px 7px;text-align:center;font-weight:700;">'
            f'%{row["Filo Payı (%)"]:.1f}</td>'
        ),
        '</tr>',
    ])

  html.extend([
      '<tr style="background:#F8FAFC;border-top:1px solid #CBD5E1;">',
      '<td style="text-align:left;padding:12px 10px;font-weight:800;">TOPLAM</td>',
      f'<td style="padding:12px 7px;text-align:center;color:#15803D;font-weight:800;">{total_coop}</td>',
      f'<td style="padding:12px 7px;text-align:center;color:#2563EB;font-weight:800;">{total_non}</td>',
      f'<td style="padding:12px 7px;text-align:center;font-weight:800;">{total}</td>',
      '<td style="padding:12px 7px;text-align:center;font-weight:800;">%100</td>',
      '</tr></tbody></table></div>',
  ])

  return "".join(html)


def _render_fleet_type_table(inputs: SimulationInputs):
  st.markdown("**Tekne Tiplerine Göre Özet**")
  st.markdown(
      _summary_table_html(inputs),
      unsafe_allow_html=True,
  )


def _membership_kpi_card(icon, label, value, subtitle, accent):
  return f"""
  <div style="
      border:1px solid #E2E8F0;
      border-radius:14px;
      min-height:126px;
      padding:18px 20px;
      display:flex;
      align-items:center;
      justify-content:center;
      gap:18px;
      background:#FFFFFF;">
    <div style="font-size:2.6rem;">{icon}</div>
    <div>
      <div style="
          font-size:0.84rem;
          color:#334155;
          font-weight:700;">{label}</div>
      <div style="
          margin-top:4px;
          font-size:2rem;
          line-height:1;
          color:{accent};
          font-weight:850;">{value}</div>
      <div style="
          margin-top:6px;
          font-size:0.76rem;
          color:#64748B;">{subtitle}</div>
    </div>
  </div>
  """


def _render_membership_kpis(inputs: SimulationInputs):
  distribution = build_fleet_distribution_chart_data(inputs)
  total = int(distribution["Adet"].sum())
  cooperative = int(
      distribution.loc[
          distribution["Statü"] == "Kooperatif Üyesi",
          "Adet",
      ].sum()
  )
  non_cooperative = total - cooperative
  cooperative_share = (100.0 * cooperative / total) if total else 0.0

  c1, c2, c3 = st.columns(3)
  cards = [
      (
          c1,
          "👥",
          "Kooperatif Üyesi",
          f"{cooperative}",
          "tekne",
          "#16A34A",
      ),
      (
          c2,
          "🧑‍💼",
          "Kooperatif Dışı",
          f"{non_cooperative}",
          "tekne",
          "#2563EB",
      ),
      (
          c3,
          "◔",
          "Kooperatif Payı",
          f"%{cooperative_share:.1f}",
          f"({cooperative} / {total})",
          "#16A34A",
      ),
  ]
  for column, icon, label, value, subtitle, accent in cards:
    with column:
      st.markdown(
          _membership_kpi_card(
              icon,
              label,
              value,
              subtitle,
              accent,
          ),
          unsafe_allow_html=True,
      )


def _render_fleet_composition(inputs: SimulationInputs):
  st.markdown("### 🚤 Filo Kompozisyonu")
  st.caption(
      "Donut grafik beş üyelik/hibe grubunu; özet tablo ise aynı teknik tipleri "
      "birleştirerek üç gerçek tekne türünü gösterir."
  )

  chart_col, legend_col, table_col = st.columns(
      [0.37, 0.28, 0.35],
      vertical_alignment="top",
  )

  with chart_col:
    _render_fleet_donut(inputs)

  with legend_col:
    _render_fleet_legend(inputs)

  with table_col:
    _render_fleet_type_table(inputs)

  st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
  _render_membership_kpis(inputs)
  st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


def render_fleet_dashboard(
    vessel_specs,
    inputs: SimulationInputs,
    fleet: FleetResult,
):
  st.subheader("🚢 Filo Geneli Toplam Dönüşüm ve Finansman Özeti")
  _render_fleet_top_kpis(fleet)

  st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
  _render_fleet_composition(inputs)

  st.markdown("**Filo Finansman Dağılımı**")
  fleet_summary_df = pd.DataFrame({
      "Tekne Tipi & Kategori": [
          "12 m Tek Gövdeli · 24 yolcu (Kooperatif %55)",
          "13,5 m Katamaran · 32 yolcu (Kooperatif %55)",
          "14 m Katamaran · 54 yolcu (Kooperatif %70)",
          "12 m Tek Gövdeli · 24 yolcu (Kooperatif Dışı %40)",
          "13,5 m Katamaran · 32 yolcu (Kooperatif Dışı %40)",
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
    <p style="font-size: 1.05rem; font-weight: 600; color: #1D4ED8; margin: 4px 0 0 0;">☀️ Sezonluk PV Üretimi: <b>{fleet.fleet_annual_solar_kwh:,.0f} kWh</b> | 🔌 Şebekeden Karşılanan Sezonluk Enerji: <b>{fleet.fleet_annual_grid_kwh:,.0f} kWh</b> | Günlük ortalama: <b>{fleet.fleet_daily_grid_kwh:,.1f} kWh/gün</b></p>
    <p style="font-size: 0.88rem; color: #1E40AF; margin: 5px 0 0 0;">Saatlik modelde PV önce aktif elektrik yükünü karşılar; kalan enerji bataryaya yönelir. Kıyı enerjisi batarya rezerv sınırı sonrasında oluşur ve sezon sonu SOC farkı başlangıç seviyesine normalize edilir.</p>
</div>
"""
  st.markdown(solar_html, unsafe_allow_html=True)
