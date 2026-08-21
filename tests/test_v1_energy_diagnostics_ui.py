from pathlib import Path


SOURCE = Path("ui/vessel_detail.py").read_text(encoding="utf-8")


def test_hourly_energy_diagnostics_helper_remains_available_for_engineering_use():
  assert "def _render_v1_hourly_energy_diagnostics(" in SOURCE
  assert "PV → Doğrudan Tahrik" in SOURCE
  assert "PV → Batarya (depolanan)" in SOURCE
  assert "Batarya → Tahrik" in SOURCE
  assert "Kullanılamayan / Fazla PV" in SOURCE
  assert "Sezon Minimum SOC" in SOURCE
  assert "Sezon Sonu SOC" in SOURCE


def test_hourly_diagnostics_are_not_rendered_in_product_ui():
  assert 'if v_key == "v1":' not in SOURCE
  assert (
      "_render_v1_hourly_energy_diagnostics(\n"
      "            spec,"
  ) not in SOURCE
