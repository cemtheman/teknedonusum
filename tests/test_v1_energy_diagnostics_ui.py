from pathlib import Path


SOURCE = Path("ui/vessel_detail.py").read_text(encoding="utf-8")


def test_product_ui_contains_no_v1_hourly_diagnostic_code():
  assert "def _render_v1_hourly_energy_diagnostics(" not in SOURCE
  assert "Tip 1 Saatlik Solar–Batarya Enerji Muhasebesi" not in SOURCE
  assert "PV → Doğrudan Tahrik" not in SOURCE
  assert "Sezon Minimum SOC" not in SOURCE
  assert "Enerji Korunumu Kontrolü" not in SOURCE
