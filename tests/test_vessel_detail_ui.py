from pathlib import Path


SOURCE = Path(
    "ui/vessel_detail.py"
).read_text(
    encoding="utf-8"
)


def test_vessel_financial_kpis_use_two_by_two_layout():
  render_source = (
      SOURCE
      .split(
          "def render_vessel_details(",
          1,
      )[1]
  )

  assert (
      "st.columns(4)"
      not in render_source
  )

  assert (
      render_source.count(
          "st.columns(2)"
      )
      >= 2
  )


def test_vessel_financial_kpis_preserve_four_decision_metrics():
  for label in (
      "Hibe Sonrası Özkaynak Yatırımı",
      "Sezonluk Net Tasarruf",
      "Yatırımın Geri Dönüş Süresi",
      "Sezonluk CO2 Salınım Azaltımı",
  ):
    assert label in SOURCE


def test_vessel_financial_detail_tables_are_preserved():
  assert (
      "Yatırım ve Hibe Özeti"
      in SOURCE
  )

  assert (
      "Sezonluk İşletme Giderleri ve Tasarruf Dökümü"
      in SOURCE
  )

  assert (
      'st.columns([6, 6])'
      in SOURCE
  )