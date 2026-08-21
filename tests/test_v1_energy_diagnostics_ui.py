from pathlib import Path


SOURCE = Path("ui/vessel_detail.py").read_text(encoding="utf-8")


def test_v1_detail_exposes_hourly_energy_diagnostics():
  assert "Tip 1 Saatlik Solar–Batarya Enerji Muhasebesi" in SOURCE
  assert "PV → Doğrudan Tahrik" in SOURCE
  assert "PV → Batarya (depolanan)" in SOURCE
  assert "Batarya → Tahrik" in SOURCE
  assert "Kullanılamayan / Fazla PV" in SOURCE
  assert "Sezonluk Kıyı Şarjı" in SOURCE
  assert "Sezon Minimum SOC" in SOURCE
  assert "Sezon Sonu SOC" in SOURCE


def test_hourly_diagnostics_are_only_rendered_for_v1():
  assert 'if v_key == "v1":' in SOURCE
  assert "_render_v1_hourly_energy_diagnostics(" in SOURCE
