from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
BRAND_LOGO_PATH = ASSET_DIR / "sessiz_akim_logo.png"
BRAND_ICON_PATH = ASSET_DIR / "sessiz_akim_icon.png"
FAVICON_PATH = ASSET_DIR / "favicon.png"

BRAND_NAME = "Sessiz Akım"
BRAND_NAME_EN = "Quiet Current"
BRAND_TAGLINE = "Daha sessiz. Daha temiz. Daha sürdürülebilir."


def _upper_initial(text):
  value = str(text or "").strip()
  if not value:
    return ""
  return value[0].upper() + value[1:]


def build_brand_description(location_name):
  location = _upper_initial(location_name)
  if not location:
    location = "Seçili lokasyon"
  return (
      f"{location} elektrikli tekne dönüşümü için teknik ve ekonomik "
      "ön değerlendirme platformu"
  )


def render_brand_header(location_name):
  description = build_brand_description(location_name)

  st.markdown(
      f"""
      <div style="margin-top:-2px;">
        <div style="font-size:2rem;font-weight:750;color:#0A2B55;line-height:1.05;">
          Sessiz Akım
        </div>
        <div style="font-size:2rem;font-weight:750;color:#2E7D57;
                    line-height:1.05;margin-top:4px;">
          Quiet Current
        </div>
        <div style="font-size:0.92rem;color:#4B5563;margin-top:10px;">
          {description}
        </div>
      </div>
      """,
      unsafe_allow_html=True,
  )
  st.divider()


def render_sidebar_brand():
  left, logo_col, right = st.columns([1, 2, 1])

  with logo_col:
    st.image(
        str(BRAND_LOGO_PATH),
        use_container_width=True,
    )

  st.markdown(
      """
      <div style="text-align:center;margin-top:-12px;margin-bottom:12px;">
        <div style="font-size:1.15rem;font-weight:750;color:#0A2B55;">
          Sessiz Akım
        </div>
        <div style="font-size:0.70rem;font-weight:650;letter-spacing:0.14em;
                    color:#2E7D57;">
          QUIET CURRENT
        </div>
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
