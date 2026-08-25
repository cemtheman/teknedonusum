import pandas as pd
import streamlit as st

from calculations.grant_program import calculate_first_year_grant_program
from ui.formatting import format_integer_tr


TYPE_LABELS = {
    "v1": "12 m Tek Gövdeli · 24 yolcu",
    "v2": "13,5 m Katamaran · 32 yolcu",
    "v3": "14 m Katamaran · 54 yolcu",
    "v4_24": "12 m Tek Gövdeli · 24 yolcu · Kooperatif Dışı",
    "v4_32": "13,5 m Katamaran · 32 yolcu · Kooperatif Dışı",
}

PRIORITY_LABELS = {
    "v3": "1",
    "v2": "2",
    "v1": "3",
    "v4_24": "4",
    "v4_32": "4",
}


def _grant_kpi_card(
    label,
    value,
):
  return (
      '<div class="grant-kpi-card">'
      f'<div class="grant-kpi-label">{label}</div>'
      f'<div class="grant-kpi-value">{value}</div>'
      '</div>'
  )


def _grant_kpi_grid_html(result):
  cards = [
      _grant_kpi_card(
          "Yıllık Hibe Bütçesi",
          f"₺{format_integer_tr(result.total_annual_budget_tl)}",
      ),
      _grant_kpi_card(
          "İlk Yıl Desteklenebilecek Tekne",
          f"{result.funded_vessels} tekne",
      ),
      _grant_kpi_card(
          "Tam Tekne Hibesi İçin Kullanılamayan Bakiye",
          f"₺{format_integer_tr(result.remaining_budget_tl)}",
      ),
      _grant_kpi_card(
          "Toplam İhtiyacın Bütçeyle Karşılanma Oranı",
          f"%{result.budget_coverage_ratio * 100:.1f}",
      ),
      _grant_kpi_card(
          "Tam Tekne Hibelerine Ayrılabilen Oran",
          f"%{result.allocated_coverage_ratio * 100:.1f}",
      ),
  ]

  css = (
      '<style>'
      '.grant-kpi-shell{'
      'width:100%;'
      'container-type:inline-size;'
      'container-name:grant-kpis;'
      '}'
      '.grant-kpi-grid{'
      'display:grid;'
      'grid-template-columns:repeat(auto-fit,minmax(230px,1fr));'
      'gap:22px 26px;'
      'width:100%;'
      'align-items:start;'
      '}'
      '.grant-kpi-card{'
      'width:100%;'
      'min-width:0;'
      'box-sizing:border-box;'
      'padding:8px 0 12px 0;'
      '}'
      '.grant-kpi-label{'
      'min-width:0;'
      'font-size:0.92rem;'
      'font-weight:500;'
      'line-height:1.35;'
      'color:#334155;'
      'overflow-wrap:anywhere;'
      '}'
      '.grant-kpi-value{'
      'min-width:0;'
      'margin-top:9px;'
      'font-size:clamp(1.65rem,2.4vw,2.25rem);'
      'font-weight:400;'
      'line-height:1.08;'
      'color:#30323D;'
      'white-space:normal;'
      'overflow-wrap:anywhere;'
      '}'
      '@container grant-kpis (min-width:1360px){'
      '.grant-kpi-grid{'
      'grid-template-columns:repeat(5,minmax(0,1fr));'
      'gap:20px 30px;'
      '}'
      '}'
      '@container grant-kpis '
      '(min-width:780px) and (max-width:1359px){'
      '.grant-kpi-grid{'
      'grid-template-columns:repeat(3,minmax(0,1fr));'
      'gap:22px 34px;'
      '}'
      '}'
      '@container grant-kpis '
      '(min-width:520px) and (max-width:779px){'
      '.grant-kpi-grid{'
      'grid-template-columns:repeat(2,minmax(0,1fr));'
      '}'
      '}'
      '@container grant-kpis (max-width:519px){'
      '.grant-kpi-grid{'
      'grid-template-columns:1fr;'
      'gap:12px;'
      '}'
      '.grant-kpi-card{'
      'padding:6px 0 10px 0;'
      '}'
      '}'
      '</style>'
  )

  return (
      css
      + '<div class="grant-kpi-shell">'
      + '<div class="grant-kpi-grid">'
      + "".join(cards)
      + '</div>'
      + '</div>'
  )


def _render_grant_kpis(result):
  st.markdown(
      _grant_kpi_grid_html(result),
      unsafe_allow_html=True,
  )


def render_grant_program(
    vessel_specs,
    inputs,
    fleet,
):
  counts = {
      "v1": inputs.count_v1,
      "v2": inputs.count_v2,
      "v3": inputs.count_v3,
      "v4_24": inputs.count_v4_24,
      "v4_32": inputs.count_v4_32,
  }

  result = calculate_first_year_grant_program(
      vessel_specs,
      counts,
      fleet.grants_per_type,
      ministry_budget_tl=inputs.grant_budget_ministry_tl,
      geka_budget_tl=inputs.grant_budget_geka_tl,
      yikob_budget_tl=inputs.grant_budget_yikob_tl,
      zero_waste_budget_tl=inputs.grant_budget_zero_waste_tl,
  )

  st.subheader(
      "🎯 İlk Yıl Hibe Programı"
  )

  st.info(
      "Senaryo varsayımı: Dört finansman kaynağı ilk yıl için tek bir toplam "
      "hibe havuzu gibi modellenir. Kaynakların gerçek başvuru, uygunluk, "
      "eş-finansman ve harcama kuralları bu ekranda ayrı ayrı uygulanmaz."
  )

  st.caption(
      "Tahsis sırası mevcut program önceliği varsayımını izler; yüksek "
      "öncelikli grup tamamlanmadan daha düşük öncelik seviyesine geçilmez. "
      "Aynı öncelik seviyesinde daha düşük tekne-başı hibe ihtiyacı önce "
      "finanse edilir."
  )

  _render_grant_kpis(
      result
  )

  st.markdown(
      "<div style='height:12px'></div>",
      unsafe_allow_html=True,
  )

  source_df = pd.DataFrame({
      "Hibe Kaynağı": [
          "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
          "GEKA",
          "YİKOB",
          "Sıfır Atık Vakfı",
          "TOPLAM",
      ],
      "Senaryo Bütçesi (TL)": [
          inputs.grant_budget_ministry_tl,
          inputs.grant_budget_geka_tl,
          inputs.grant_budget_yikob_tl,
          inputs.grant_budget_zero_waste_tl,
          result.total_annual_budget_tl,
      ],
  })

  source_df["Senaryo Bütçesi (TL)"] = (
      source_df["Senaryo Bütçesi (TL)"].map(
          lambda value: (
              f"₺{format_integer_tr(value)}"
          )
      )
  )

  allocation_rows = []

  for key in (
      "v3",
      "v2",
      "v1",
      "v4_24",
      "v4_32",
  ):
    funded = result.funded_by_type[key]
    requested = counts[key]

    allocation_rows.append({
        "Program Önceliği": PRIORITY_LABELS[key],
        "Tekne Türü": TYPE_LABELS[key],
        "Hedef": requested,
        "İlk Yıl": funded,
        "Kalan": requested - funded,
        "Tekne Başı Hibe": (
            f"₺{format_integer_tr(fleet.grants_per_type[key])}"
        ),
    })

  allocation_df = pd.DataFrame(
      allocation_rows
  )

  left, right = st.columns(
      [0.36, 0.64],
      vertical_alignment="top",
  )

  with left:
    st.markdown(
        "**Yıllık Kaynak Bütçeleri**"
    )

    st.caption(
        "Bu tutarlar kaynak bazında gerçek tahsis değil, birleşik hibe "
        "havuzunu oluşturan senaryo girdileridir."
    )

    st.dataframe(
        source_df,
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(
        f"""
        <div style="
            border:1px solid #D1FAE5;
            background:#ECFDF5;
            border-radius:12px;
            padding:14px 16px;
            margin-top:8px;
        ">
          <div style="
              font-size:0.78rem;
              color:#047857;
              font-weight:700;
          ">
            İlk Yıl Harekete Geçen Toplam Yatırım
          </div>

          <div style="
              font-size:1.35rem;
              color:#065F46;
              font-weight:850;
          ">
            ₺{format_integer_tr(result.unlocked_investment_tl)}
          </div>

          <div style="
              font-size:0.76rem;
              color:#047857;
              margin-top:5px;
          ">
            Fiilen tahsis edilen hibe:
            ₺{format_integer_tr(result.allocated_grant_tl)}
          </div>

          <div style="
              font-size:0.76rem;
              color:#047857;
              margin-top:3px;
          ">
            Gerekli tekne sahibi özkaynağı:
            ₺{format_integer_tr(result.required_owner_equity_tl)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with right:
    st.markdown(
        "**Program Önceliğine Göre İlk Yıl Tahsisi**"
    )

    st.caption(
        "Öncelik sırası mevcut programlama varsayımıdır; fon "
        "sağlayıcıların nihai uygunluk ve tahsis kararlarının "
        "yerine geçmez."
    )

    st.dataframe(
        allocation_df,
        hide_index=True,
        use_container_width=True,
    )

  st.caption(
      "Toplam İhtiyacın Bütçeyle Karşılanma Oranı toplam bütçenin toplam "
      "hibe ihtiyacına oranını; Tam Tekne Hibelerine Ayrılabilen Oran ise "
      "yalnız tam tekne hibelerine bağlanabilen gerçek tahsis oranını gösterir."
  )

  st.divider()