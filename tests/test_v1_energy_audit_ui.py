from pathlib import Path


SOURCE = Path("ui/vessel_detail.py").read_text(encoding="utf-8")


def test_energy_audit_rows_are_not_exposed_in_product_ui():
  for text in (
      "PVGIS Saatlik Sezonluk Üretim",
      "PV → Batarya Girişi (şarj öncesi)",
      "Şarj Dönüşüm Kaybı",
      "Batarya İçinden Çekilen Enerji",
      "Deşarj Dönüşüm Kaybı",
      "Terminal SOC Düzeltmeli Kıyı Enerjisi",
      "Terminal SOC Açığı",
      "PV denge hatası",
      "Tahrik denge hatası",
      "Batarya denge hatası",
  ):
    assert text not in SOURCE
