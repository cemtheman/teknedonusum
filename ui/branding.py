from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
BRAND_LOGO_PATH = ASSET_DIR / "sessiz_akim_logo.png"
BRAND_ICON_PATH = ASSET_DIR / "sessiz_akim_icon.png"
FAVICON_PATH = ASSET_DIR / "favicon.png"
SUPPORTER_ASSET_DIR = ASSET_DIR / "supporters"

SUPPORTERS = (
    ("Sıfır Atık Vakfı", "sifir_atik_vakfi.png"),
    (
        "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
        "cevre_sehircilik_iklim_bakanligi.png",
    ),
    ("Muğla Valiliği", "mugla_valiligi.png"),
    ("GEKA", "geka.png"),
    ("Ortaca Kaymakamlığı", "ortaca_kaymakamligi.png"),
    ("Köyceğiz Kaymakamlığı", "koycegiz_kaymakamligi.png"),
    ("Muğla Büyükşehir Belediyesi", "mugla_buyuksehir.png"),
    ("Ortaca Belediyesi", "ortaca_belediyesi.png"),
    ("Köyceğiz Belediyesi", "koycegiz_belediyesi.png"),
)

BRAND_NAME = "Sessiz Akım"
BRAND_NAME_EN = "Quiet Current"
BRAND_TAGLINE = "Daha sessiz. Daha temiz. Daha sürdürülebilir."


def _upper_initial(text):
  value = str(text or "").strip()
  if not value:
    return ""
  return value[0].upper() + value[1:]


def build_brand_description(location_name=None):
  return (
      "Elektrikli tekne dönüşümü için teknik ve ekonomik "
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
  st.markdown(
      """
      <style>
      section[data-testid="stSidebar"] {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
      }

      section[data-testid="stSidebar"] > div {
        width: 330px !important;
      }
      </style>
      """,
      unsafe_allow_html=True,
  )
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


def _image_data_uri(path):
  import base64
  import mimetypes

  mime_type = mimetypes.guess_type(str(path))[0] or "image/png"
  encoded = base64.b64encode(path.read_bytes()).decode("ascii")
  return f"data:{mime_type};base64,{encoded}"


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
          Sessiz Akım · {BRAND_TAGLINE} ·
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

  supporter_items = []

  for name, filename in SUPPORTERS:
    logo_path = SUPPORTER_ASSET_DIR / filename

    if not logo_path.exists():
      supporter_items.append(
          f"""
          <div class="supporter-logo-item supporter-logo-missing">
            {name}
          </div>
          """
      )
      continue

    logo_uri = _image_data_uri(logo_path)

    supporter_items.append(
        f"""
        <div class="supporter-logo-item" title="{name}">
          <img
            src="{logo_uri}"
            alt="{name}"
          />
        </div>
        """
    )

  st.markdown(
      f"""
      <style>
      .supporter-logo-strip {{
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        align-items: center;
        justify-content: flex-start;
        gap: 10px;
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 2px 0 8px 0;
        scrollbar-width: thin;
        -webkit-overflow-scrolling: touch;
      }}

      .supporter-logo-item {{
        flex: 0 0 auto;
        width: 92px;
        min-width: 92px;
        height: 72px;
        display: flex;
        align-items: center;
        justify-content: center;
      }}

      .supporter-logo-item img {{
        display: block;
        max-width: 78px;
        max-height: 64px;
        width: auto;
        height: auto;
        object-fit: contain;
      }}

      .supporter-logo-missing {{
        font-size: 0.65rem;
        color: #9CA3AF;
        text-align: center;
      }}

      @media (max-width: 768px) {{
        .supporter-logo-strip {{
          gap: 8px;
        }}

        .supporter-logo-item {{
          width: 82px;
          min-width: 82px;
          height: 64px;
        }}

        .supporter-logo-item img {{
          max-width: 70px;
          max-height: 56px;
        }}
      }}
      </style>

      <div class="supporter-logo-strip">
        {''.join(supporter_items)}
      </div>
      """,
      unsafe_allow_html=True,
  )
