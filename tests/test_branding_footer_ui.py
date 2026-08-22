from pathlib import Path

from ui.branding import (
    SUPPORTERS,
    build_brand_description,
)


SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_brand_caption_no_longer_contains_location():
  description = build_brand_description("Dalyan")

  assert description == (
      "Elektrikli tekne dönüşümü için teknik ve ekonomik "
      "ön değerlendirme platformu"
  )
  assert "Dalyan" not in description


def test_footer_brand_icon_is_inline_after_disclaimer():
  assert "_image_data_uri(BRAND_ICON_PATH)" in SOURCE
  assert 'alt="Sessiz Akım"' in SOURCE
  assert (
      "Tüm sonuçlar ön teknik değerlendirme niteliğindedir."
      in SOURCE
  )


def test_supporters_are_rendered_in_single_responsive_strip():
  assert 'class="supporter-logo-strip"' in SOURCE
  assert "flex-wrap: nowrap" in SOURCE
  assert "overflow-x: auto" in SOURCE
  assert "gap: 10px" in SOURCE
  assert "logo_columns = st.columns(" not in SOURCE


def test_supporter_names_are_not_rendered_under_logos():
  assert "min-height:2.5em" not in SOURCE
  assert "font-size:0.66rem" not in SOURCE


def test_expected_supporters_are_declared_once_and_in_order():
  names = [name for name, _ in SUPPORTERS]

  assert names == [
      "Sıfır Atık Vakfı",
      "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
      "Muğla Valiliği",
      "GEKA",
      "Ortaca Kaymakamlığı",
      "Köyceğiz Kaymakamlığı",
      "Muğla Büyükşehir Belediyesi",
      "Ortaca Belediyesi",
      "Köyceğiz Belediyesi",
  ]

  assert len(names) == len(set(names))


def test_mugla_metropolitan_uses_png_asset():
  assert (
      "Muğla Büyükşehir Belediyesi",
      "mugla_buyuksehir.png",
  ) in SUPPORTERS

def test_supporter_strip_does_not_stack_on_mobile():
  assert "flex-direction: row" in SOURCE
  assert "flex-wrap: nowrap" in SOURCE
  assert "@media (max-width: 768px)" in SOURCE
  assert "overflow-x: auto" in SOURCE
