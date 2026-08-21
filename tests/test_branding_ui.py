from pathlib import Path


def test_brand_assets_are_present():
  for path in (
      Path("assets/sessiz_akim_logo.png"),
      Path("assets/sessiz_akim_icon.png"),
      Path("assets/favicon.png"),
  ):
    assert path.is_file()


def test_branding_module_exposes_required_surfaces():
  source = Path("ui/branding.py").read_text(encoding="utf-8")

  assert "BRAND_LOGO_PATH" in source
  assert "BRAND_ICON_PATH" in source
  assert "FAVICON_PATH" in source
  assert "def render_brand_header(" in source
  assert "def render_sidebar_brand(" in source
  assert "def render_brand_footer(" in source
  assert "Quiet Current" in source
