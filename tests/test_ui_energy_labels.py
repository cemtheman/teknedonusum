from pathlib import Path


def test_fleet_dashboard_names_soc_normalized_shore_energy():
  source = Path("ui/fleet_dashboard.py").read_text(encoding="utf-8")

  assert "Şebekeden Karşılanan Sezonluk Enerji" in source
  assert "sezon sonu SOC farkı başlangıç seviyesine normalize edilir" in source
  assert "Sezonluk Kıyı Şarj İhtiyacı" not in source


def test_technical_comparison_uses_energy_demand_language():
  source = Path("ui/normative_comparison.py").read_text(encoding="utf-8")

  assert "Günlük tahrik enerji talebi" in source
  assert "PV/batarya/kıyı" in source
  assert "Seyir/enerji hesap yöntemi" in source


def test_vessel_detail_does_not_repeat_technical_energy_cards():
  source = Path("ui/vessel_detail.py").read_text(encoding="utf-8")

  assert "Teknik ve Enerji Özeti" not in source
  assert "Saatlik PV / Kıyı Enerjisi" not in source
  assert "Şebekeden Karşılanan Enerji Gideri" in source
