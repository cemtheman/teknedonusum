from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
BRAND_LOGO_PATH = ASSET_DIR / "sessiz_akim_logo.png"
BRAND_ICON_PATH = ASSET_DIR / "sessiz_akim_icon.png"
FAVICON_PATH = ASSET_DIR / "favicon.png"

BRAND_NAME = "Sessiz Akım"
BRAND_NAME_EN = "Quiet Current"
BRAND_TAGLINE = "Daha sessiz. Daha temiz. Daha sürdürülebilir."


def render_brand_header():
  logo_col, title_col = st.columns([0.12, 0.88], vertical_alignment="center")
  with logo_col:
    st.image(str(BRAND_ICON_PATH), width=82)
  with title_col:
    st.markdown(
        """
        <div style="margin-top:-2px;">
          <div style="font-size:2rem;font-weight:750;color:#0A2B55;line-height:1.05;">
            Sessiz Akım
          </div>
          <div style="font-size:0.92rem;font-weight:600;letter-spacing:0.16em;
                      color:#2E7D57;margin-top:4px;">
            QUIET CURRENT
          </div>
          <div style="font-size:0.92rem;color:#4B5563;margin-top:8px;">
            Köyceğiz–Dalyan elektrikli tekne dönüşümü için teknik ve ekonomik
            ön değerlendirme platformu
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  st.divider()


def render_sidebar_brand():
  st.image(str(BRAND_LOGO_PATH), width=150)
  st.markdown(
      """
      <div style="text-align:center;margin-top:-12px;margin-bottom:12px;">
        <div style="font-size:1.15rem;font-weight:750;color:#0A2B55;">Sessiz Akım</div>
        <div style="font-size:0.70rem;font-weight:650;letter-spacing:0.14em;
                    color:#2E7D57;">QUIET CURRENT</div>
      </div>
      """,
      unsafe_allow_html=True,
  )


def render_brand_footer():
  st.divider()
  left, right = st.columns([0.78, 0.22], vertical_alignment="center")
  with left:
    st.caption(
        "Sessiz Akım · "
        + BRAND_TAGLINE
        + " · Tüm sonuçlar ön teknik değerlendirme niteliğindedir."
    )
  with right:
    st.image(str(BRAND_ICON_PATH), width=42)
