from pathlib import Path


UI = Path("ui/grant_program.py").read_text(encoding="utf-8")


def test_grant_ui_labels_are_decision_friendly():
  for text in (
      "Toplam İhtiyacın Bütçeyle Karşılanma Oranı",
      "Tam Tekne Hibelerine Ayrılabilen Oran",
      "İlk Yıl Desteklenebilecek Tekne",
      "Tam Tekne Hibesi İçin Kullanılamayan Bakiye",
      "Program Önceliğine Göre İlk Yıl Tahsisi",
  ):
    assert text in UI


def test_grant_ui_states_combined_pool_assumption_explicitly():
  assert "Senaryo varsayımı" in UI
  assert "tek bir toplam " in UI
  assert "hibe havuzu" in UI
  assert "gerçek başvuru, uygunluk" in UI


def test_grant_source_table_is_labeled_as_scenario_budget():
  assert "Senaryo Bütçesi (TL)" in UI
  assert "kaynak bazında gerçek tahsis değil" in UI
