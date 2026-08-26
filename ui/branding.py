from pathlib import Path
import base64
import html
import mimetypes

import streamlit as st


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
BRAND_LOGO_PATH = ASSET_DIR / "sessiz_akim_logo.png"
BRAND_ICON_PATH = ASSET_DIR / "sessiz_akim_icon.png"
FAVICON_PATH = ASSET_DIR / "favicon.png"
SUPPORTER_ASSET_DIR = ASSET_DIR / "supporters"

SUPPORTERS = (
    (
        "Sıfır Atık Vakfı",
        "sifir_atik_vakfi.png",
        "https://sifiratikvakfi.org/",
    ),
    (
        "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
        "cevre_sehircilik_iklim_bakanligi.png",
        "https://www.csb.gov.tr/",
    ),
    (
        "Muğla Valiliği",
        "mugla_valiligi.png",
        "https://www.mugla.gov.tr/",
    ),
    (
        "GEKA",
        "geka.png",
        "https://www.geka.gov.tr/",
    ),
    (
        "Ortaca Kaymakamlığı",
        "ortaca_kaymakamligi.png",
        "https://ortaca.gov.tr/",
    ),
    (
        "Köyceğiz Kaymakamlığı",
        "koycegiz_kaymakamligi.png",
        "https://koycegiz.gov.tr/",
    ),
    (
        "Muğla Büyükşehir Belediyesi",
        "mugla_buyuksehir.png",
        "https://www.mugla.bel.tr/",
    ),
    (
        "Ortaca Belediyesi",
        "ortaca_belediyesi.png",
        "https://www.ortaca.bel.tr/",
    ),
    (
        "Köyceğiz Belediyesi",
        "koycegiz_belediyesi.png",
        "https://www.koycegiz.bel.tr/",
    ),
)

BRAND_NAME = "Sessiz Akım"
BRAND_NAME_EN = "Quiet Current"
BRAND_TAGLINE = "Doğayı geleceğe taşıyoruz."
BRAND_TAGLINE_EN = "Moving with nature."


def _upper_initial(text):
  value = str(
      text
      or ""
  ).strip()

  if not value:
    return ""

  return (
      value[0].upper()
      + value[1:]
  )


def build_brand_description(
    location_name=None,
):
  return (
      "Elektrikli tekne dönüşümü için teknik ve ekonomik "
      "ön değerlendirme platformu"
  )


def render_brand_header(
    location_name,
):
  description = build_brand_description(
      location_name
  )

  st.markdown(
      f"""
      <div style="margin-top:-2px;">
        <div style="font-size:2rem;font-weight:750;color:#0A2B55;line-height:1.05;">
          {BRAND_NAME}
        </div>

        <div style="
            font-size:0.90rem;
            font-weight:600;
            color:#4B5563;
            line-height:1.25;
            margin-top:5px;
        ">
          {BRAND_TAGLINE}
        </div>

        <div style="
            font-size:2rem;
            font-weight:750;
            color:#2E7D57;
            line-height:1.05;
            margin-top:9px;
        ">
          {BRAND_NAME_EN}
        </div>

        <div style="
            font-size:0.78rem;
            font-weight:600;
            color:#6B7280;
            line-height:1.25;
            margin-top:4px;
        ">
          {BRAND_TAGLINE_EN}
        </div>

        <div style="
            font-size:0.92rem;
            color:#4B5563;
            margin-top:12px;
        ">
          {description}
        </div>
      </div>
      """,
      unsafe_allow_html=True,
  )

  st.divider()


def render_sidebar_brand():
  logo_uri = _image_data_uri(
      BRAND_LOGO_PATH
  )

  st.markdown(
      """
      <style>
      [data-testid="stMainBlockContainer"] {
        padding-top:1.5rem;
      }

      /*
       * Sidebar geometry is intentionally left to Streamlit.
       * Only the brand content itself is repositioned.
       */
      .sidebar-brand-shell {
        width:100%;
        min-width:0;
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        align-items:center;
        text-align:center;
        transform:translateY(-2.5rem);
        margin-bottom:-2.5rem;
      }

      .sidebar-brand-logo {
        display:block;
        width:min(160px,58%);
        height:auto;
        object-fit:contain;
        margin:0 auto;
      }

      .sidebar-brand-name {
        margin-top:8px;
        font-size:1.15rem;
        font-weight:750;
        line-height:1.2;
        color:#0A2B55;
      }

      .sidebar-brand-tagline {
        margin-top:8px;
        font-size:0.74rem;
        line-height:1.35;
        color:#4B5563;
      }

      .sidebar-brand-name-en {
        margin-top:10px;
        font-size:0.70rem;
        font-weight:650;
        line-height:1.3;
        letter-spacing:0.14em;
        color:#2E7D57;
      }

      .sidebar-brand-tagline-en {
        margin-top:5px;
        font-size:0.66rem;
        line-height:1.3;
        color:#6B7280;
      }

      @media (max-width: 768px) {
        html,
        body,
        [data-testid="stAppViewContainer"] {
          max-width: 100vw;
          overflow-x: hidden;
        }

        [data-testid="stMainBlockContainer"] {
          padding-top:4.5rem;
        }

        .sidebar-brand-shell {
          transform:translateY(-2rem);
          margin-bottom:-2rem;
        }
      }
      </style>
      """,
      unsafe_allow_html=True,
  )

  st.markdown(
      f"""
      <div class="sidebar-brand-shell">
        <img
          class="sidebar-brand-logo"
          src="{logo_uri}"
          alt="{BRAND_NAME}"
        />

        <div class="sidebar-brand-name">
          {BRAND_NAME}
        </div>

        <div class="sidebar-brand-tagline">
          {BRAND_TAGLINE}
        </div>

        <div class="sidebar-brand-name-en">
          QUIET CURRENT
        </div>

        <div class="sidebar-brand-tagline-en">
          {BRAND_TAGLINE_EN}
        </div>
      </div>
      """,
      unsafe_allow_html=True,
  )


def _image_data_uri(
    path,
):
  mime_type = (
      mimetypes.guess_type(
          str(
              path
          )
      )[0]
      or "image/png"
  )

  encoded = base64.b64encode(
      path.read_bytes()
  ).decode(
      "ascii"
  )

  return (
      f"data:{mime_type};base64,{encoded}"
  )


def _build_supporter_logo_html(
    name,
    filename,
    url,
):
  safe_name = html.escape(
      name,
      quote=True,
  )

  safe_url = html.escape(
      url,
      quote=True,
  )

  logo_path = (
      SUPPORTER_ASSET_DIR
      / filename
  )

  if not logo_path.exists():
    return (
        f'<a href="{safe_url}" '
        'target="_blank" '
        'rel="noopener noreferrer" '
        'class="supporter-logo-link" '
        f'title="{safe_name}" '
        f'aria-label="{safe_name}">'
        '<div class="supporter-logo-item supporter-logo-missing">'
        f'{safe_name}'
        '</div>'
        '</a>'
    )

  logo_uri = _image_data_uri(
      logo_path
  )

  return (
      f'<a href="{safe_url}" '
      'target="_blank" '
      'rel="noopener noreferrer" '
      'class="supporter-logo-link" '
      f'title="{safe_name}" '
      f'aria-label="{safe_name}">'
      '<div class="supporter-logo-item">'
      f'<img src="{logo_uri}" alt="{safe_name}" />'
      '</div>'
      '</a>'
  )


def render_brand_footer():
  st.divider()

  brand_icon_uri = _image_data_uri(BRAND_ICON_PATH)

  st.markdown(
      f"""
      <div style="
          display:flex;
          align-items:center;
          gap:7px;
          color:#6B7280;
          font-size:0.82rem;
          line-height:1.4;
      ">
        <span>
          {BRAND_NAME} · {BRAND_TAGLINE} ·
          Tüm sonuçlar ön teknik değerlendirme niteliğindedir.
        </span>

        <img
          src="{brand_icon_uri}"
          alt="Sessiz Akım"
          style="
              width:30px;
              height:30px;
              object-fit:contain;
              flex:0 0 auto;
          "
        />
      </div>
      """,
      unsafe_allow_html=True,
  )

  st.markdown(
      f"""
      <div style="
          margin-top:5px;
          color:#9CA3AF;
          font-size:0.72rem;
      ">
        {BRAND_NAME_EN} · {BRAND_TAGLINE_EN}
      </div>
      """,
      unsafe_allow_html=True,
  )

  st.markdown(
      """
      <div style="
          margin-top:24px;
          margin-bottom:16px;
          font-size:0.95rem;
          font-weight:750;
          color:#4B5563;
      ">
        Destekleyenler
      </div>
      """,
      unsafe_allow_html=True,
  )

  supporter_items = [
      _build_supporter_logo_html(
          name,
          filename,
          url,
      )
      for (
          name,
          filename,
          url,
      )
      in SUPPORTERS
  ]

  supporter_css = """
<style>
.supporter-logo-strip {
  display:flex;
  flex-direction:row;
  flex-wrap:nowrap;
  align-items:center;
  justify-content:flex-start;
  gap:10px;
  width:100%;
  overflow-x:auto;
  overflow-y:hidden;
  padding:2px 0 8px 0;
  scrollbar-width:thin;
  -webkit-overflow-scrolling:touch;
}

.supporter-logo-link {
  flex:0 0 auto;
  display:block;
  text-decoration:none;
  border-radius:6px;
}

.supporter-logo-link:focus-visible {
  outline:2px solid currentColor;
  outline-offset:2px;
}

.supporter-logo-item {
  flex:0 0 auto;
  width:92px;
  min-width:92px;
  height:72px;
  display:flex;
  align-items:center;
  justify-content:center;
}

.supporter-logo-item img {
  display:block;
  max-width:78px;
  max-height:64px;
  width:auto;
  height:auto;
  object-fit:contain;
}

.supporter-logo-missing {
  font-size:0.65rem;
  color:#9CA3AF;
  text-align:center;
}

@media (max-width:768px) {
  .supporter-logo-strip {
    gap:8px;
  }

  .supporter-logo-item {
    width:82px;
    min-width:82px;
    height:64px;
  }

  .supporter-logo-item img {
    max-width:70px;
    max-height:56px;
  }
}
</style>
"""

  supporter_html = (
      supporter_css
      + '<div class="supporter-logo-strip">'
      + "".join(supporter_items)
      + "</div>"
  )

  st.markdown(
      supporter_html,
      unsafe_allow_html=True,
  )