from pathlib import Path


def test_fleet_dashboard_names_soc_normalized_shore_energy():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")

  assert "SOC-Normalize Sezonluk Kıyı Enerjisi" in source
  assert "sezon sonu SOC farkı başlangıç seviyesine normalize edilir" in source
  assert "Sezonluk Kıyı Şarj İhtiyacı" not in source


def test_vessel_detail_uses_precise_hourly_energy_label():
  source = Path("ui/vessel_detail.py").read_text(encoding="utf-8")

  assert "Ort. Günlük PV / SOC-Normalize Kıyı Enerjisi" in source
  assert 'if v_key == "v1":' not in source
