from pathlib import Path

from ui.branding import (
    BRAND_TAGLINE,
    BRAND_TAGLINE_EN,
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


def test_locked_brand_taglines_are_used():
  assert BRAND_TAGLINE == "Doğayı geleceğe taşıyoruz."
  assert BRAND_TAGLINE_EN == "Moving with nature."

  assert "Daha sessiz. Daha temiz. Daha sürdürülebilir." not in SOURCE


def test_footer_brand_icon_is_inline_after_disclaimer():
  assert "_image_data_uri(BRAND_ICON_PATH)" in SOURCE
  assert 'alt="Sessiz Akım"' in SOURCE
  assert (
      "Tüm sonuçlar ön teknik değerlendirme niteliğindedir."
      in SOURCE
  )


def test_supporters_are_rendered_in_single_responsive_strip():
  assert 'class="supporter-logo-strip"' in SOURCE
  assert "flex-wrap:nowrap" in SOURCE
  assert "overflow-x:auto" in SOURCE
  assert "gap:10px" in SOURCE
  assert "logo_columns = st.columns(" not in SOURCE


def test_supporter_names_are_not_rendered_as_logo_captions():
  assert "min-height:2.5em" not in SOURCE
  assert "<figcaption" not in SOURCE
  assert 'class="supporter-logo-caption"' not in SOURCE


def test_expected_supporters_are_declared_once_and_in_order():
  names = [name for name, _, _ in SUPPORTERS]

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


def test_all_supporters_have_https_links():
  for _, _, url in SUPPORTERS:
    assert url.startswith("https://")


def test_supporter_logos_are_clickable_external_links():
  assert "def _build_supporter_logo_html(" in SOURCE
  assert 'f\'<a href="{safe_url}" \'' in SOURCE
  assert 'target="_blank"' in SOURCE
  assert 'rel="noopener noreferrer"' in SOURCE
  assert 'class="supporter-logo-link"' in SOURCE


def test_supporter_markup_is_built_as_single_html_block():
  assert 'supporter_html = (' in SOURCE
  assert '"".join(supporter_items)' in SOURCE
  assert "unsafe_allow_html=True" in SOURCE


def test_mugla_metropolitan_uses_png_asset():
  assert (
      "Muğla Büyükşehir Belediyesi",
      "mugla_buyuksehir.png",
      "https://www.mugla.bel.tr/",
  ) in SUPPORTERS


def test_supporter_strip_does_not_stack_on_mobile():
  assert "flex-direction:row" in SOURCE
  assert "flex-wrap:nowrap" in SOURCE
  assert "@media (max-width:768px)" in SOURCE
  assert "overflow-x:auto" in SOURCE