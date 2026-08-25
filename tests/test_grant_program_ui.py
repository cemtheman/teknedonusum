from pathlib import Path


INPUTS = Path(
    "ui/inputs.py"
).read_text(
    encoding="utf-8"
)

APP = Path(
    "app.py"
).read_text(
    encoding="utf-8"
)

UI = Path(
    "ui/grant_program.py"
).read_text(
    encoding="utf-8"
)


def test_sidebar_exposes_four_grant_budget_sources():
  assert (
      'st.expander("🎯 Hibe Programı Bütçeleri", expanded=False)'
      in INPUTS
  )

  for label in (
      "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı",
      "GEKA",
      "YİKOB",
      "Sıfır Atık Vakfı",
  ):
    assert label in INPUTS


def test_grant_program_is_wired_after_fleet_calculation():
  assert (
      "from ui.grant_program import render_grant_program"
      in APP
  )

  assert (
      "render_grant_program(vessel_specs, inputs, fleet)"
      in APP
  )


def test_right_panel_exposes_first_year_decision_metrics():
  for text in (
      "Yıllık Hibe Bütçesi",
      "Toplam İhtiyacın Bütçeyle Karşılanma Oranı",
      "Tam Tekne Hibelerine Ayrılabilen Oran",
      "İlk Yıl Desteklenebilecek Tekne",
      "Tam Tekne Hibesi İçin Kullanılamayan Bakiye",
      "Program Önceliğine Göre İlk Yıl Tahsisi",
  ):
    assert text in UI


def test_first_year_metrics_use_responsive_grid():
  render_source = (
      UI
      .split(
          "def render_grant_program(",
          1,
      )[1]
      .split(
          "source_df = pd.DataFrame",
          1,
      )[0]
  )

  assert (
      "_render_grant_kpis("
      in render_source
  )

  assert (
      "st.columns(5)"
      not in render_source
  )

  assert (
      "st.columns(3)"
      not in render_source
  )

  assert (
      "st.columns(2)"
      not in render_source
  )

  assert (
      "grid-template-columns"
      in UI
  )

  assert (
      "repeat(auto-fit"
      in UI
  )

  assert (
      "minmax("
      in UI
  )

  assert (
      "overflow-wrap:anywhere"
      in UI
  )

  assert (
      "min-width:0"
      in UI
  )