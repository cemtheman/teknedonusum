from pathlib import Path


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
BRANDING_SOURCE = Path("ui/branding.py").read_text(encoding="utf-8")


def test_brand_assets_are_present():
  for path in (
      Path("assets/sessiz_akim_logo.png"),
      Path("assets/sessiz_akim_icon.png"),
      Path("assets/favicon.png"),
  ):
    assert path.is_file()


def test_branding_module_exposes_required_surfaces():
  assert "BRAND_LOGO_PATH" in BRANDING_SOURCE
  assert "BRAND_ICON_PATH" in BRANDING_SOURCE
  assert "FAVICON_PATH" in BRANDING_SOURCE
  assert "def render_brand_header(" in BRANDING_SOURCE
  assert "def render_sidebar_brand(" in BRANDING_SOURCE
  assert "def render_brand_footer(" in BRANDING_SOURCE
  assert "Quiet Current" in BRANDING_SOURCE


def test_primary_app_does_not_render_main_brand_header():
  assert "render_brand_header" not in APP_SOURCE


def test_primary_app_keeps_sidebar_footer_and_page_branding():
  assert "inputs = render_sidebar(" in APP_SOURCE
  assert "render_brand_footer()" in APP_SOURCE
  assert 'page_title="Sessiz Akım"' in APP_SOURCE


def test_scenario_overview_renders_before_remote_solar_fetch():
  overview_pos = APP_SOURCE.index("render_scenario_overview(inputs)")
  solar_fetch_pos = APP_SOURCE.index("fetch_pvgis_hourly_specific_pv(")

  assert overview_pos < solar_fetch_pos
