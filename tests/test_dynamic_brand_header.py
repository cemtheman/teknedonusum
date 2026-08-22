from pathlib import Path

from ui.branding import build_brand_description


BRANDING = Path("ui/branding.py").read_text(encoding="utf-8")
APP = Path("app.py").read_text(encoding="utf-8")


def test_brand_description_is_location_independent():
  assert build_brand_description("dalyan, Ortaca, Muğla, Türkiye") == (
      "Elektrikli tekne dönüşümü için teknik ve ekonomik "
      "ön değerlendirme platformu"
  )


def test_brand_description_does_not_include_location():
  description = build_brand_description("Dalyan, Muğla")

  assert "Dalyan" not in description
  assert "Muğla" not in description

def test_main_header_has_no_duplicate_logo_image():
  start = BRANDING.index("def render_brand_header")
  end = BRANDING.index("def render_sidebar_brand", start)
  block = BRANDING[start:end]

  assert "st.image(" not in block
  assert "BRAND_ICON_PATH" not in block


def test_brand_header_is_rendered_after_sidebar_inputs():
  sidebar_pos = APP.index("inputs = render_sidebar(")
  header_pos = APP.index("render_brand_header(inputs.location_name)")
  assert sidebar_pos < header_pos
