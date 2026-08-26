from pathlib import Path


SOURCE = Path(
    "ui/branding.py"
).read_text(
    encoding="utf-8"
)


def _sidebar_brand_source():
  return (
      SOURCE
      .split(
          "def render_sidebar_brand(",
          1,
      )[1]
      .split(
          "def _image_data_uri(",
          1,
      )[0]
  )


def test_main_brand_titles_have_equal_visual_weight():
  assert (
      "font-size:2rem;font-weight:750;color:#0A2B55"
      in SOURCE
  )

  assert "font-size:2rem;" in SOURCE
  assert "font-weight:750;" in SOURCE
  assert "color:#2E7D57;" in SOURCE
  assert "Quiet Current" in SOURCE


def test_locked_taglines_are_visible_in_brand_header():
  assert "Doğayı geleceğe taşıyoruz." in SOURCE
  assert "Moving with nature." in SOURCE


def test_taglines_have_lower_visual_weight_than_brand_names():
  assert "font-size:0.90rem" in SOURCE
  assert "font-size:0.78rem" in SOURCE


def test_main_content_top_spacing_is_compact_on_desktop():
  assert (
      '[data-testid="stMainBlockContainer"]'
      in SOURCE
  )

  assert (
      "padding-top:1.5rem;"
      in SOURCE
  )


def test_main_content_has_safe_mobile_top_spacing():
  assert (
      "@media (max-width: 768px)"
      in SOURCE
  )

  assert (
      '[data-testid="stMainBlockContainer"] {'
      in SOURCE
  )

  assert (
      "padding-top:4.5rem;"
      in SOURCE
  )


def test_sidebar_brand_uses_its_own_html_shell():
  sidebar_source = _sidebar_brand_source()

  assert (
      'class="sidebar-brand-shell"'
      in sidebar_source
  )

  assert (
      "logo_uri = _image_data_uri("
      in sidebar_source
  )

  assert (
      "BRAND_LOGO_PATH"
      in sidebar_source
  )


def test_sidebar_brand_is_moved_up_explicitly():
  assert (
      ".sidebar-brand-shell"
      in SOURCE
  )

  assert (
      "transform:translateY(-2.5rem);"
      in SOURCE
  )

  assert (
      "margin-bottom:-2.5rem;"
      in SOURCE
  )


def test_sidebar_brand_no_longer_depends_on_streamlit_columns():
  sidebar_source = _sidebar_brand_source()

  assert (
      "st.columns("
      not in sidebar_source
  )

  assert (
      "st.image("
      not in sidebar_source
  )


def test_sidebar_spacing_does_not_depend_on_streamlit_dom_selectors():
  assert (
      '[data-testid="stSidebarContent"]'
      not in SOURCE
  )

  assert (
      '[data-testid="stSidebarUserContent"]'
      not in SOURCE
  )


def test_top_spacing_is_not_removed_entirely():
  assert (
      "padding-top:0;"
      not in SOURCE
  )

  assert (
      "padding-top:0rem;"
      not in SOURCE
  )