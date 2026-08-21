from pathlib import Path


INPUTS = Path("ui/inputs.py").read_text(encoding="utf-8")
APP = Path("app.py").read_text(encoding="utf-8")
UI = Path("ui/grant_program.py").read_text(encoding="utf-8")


def test_sidebar_exposes_four_grant_budget_sources():
  assert 'st.expander("🎯 Hibe Programı Bütçeleri", expanded=False)' in INPUTS
  for label in (
      "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
      "GEKA",
      "YİKOB",
      "Sıfır Atık Vakfı",
  ):
    assert label in INPUTS


def test_grant_program_is_wired_after_fleet_calculation():
  assert "from ui.grant_program import render_grant_program" in APP
  assert "render_grant_program(vessel_specs, inputs, fleet)" in APP


def test_right_panel_exposes_first_year_decision_metrics():
  for text in (
      "Toplam Yıllık Hibe Bütçesi",
      "Toplam Hibe İhtiyacı Karşılama",
      "İlk Yıl Finanse Edilebilir",
      "GEKA Önceliğine Göre İlk Yıl Tahsisi",
  ):
    assert text in UI
