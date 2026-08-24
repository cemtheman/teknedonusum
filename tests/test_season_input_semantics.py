from pathlib import Path


SOURCE = Path(
    "ui/inputs.py"
).read_text(
    encoding="utf-8"
)


def test_sidebar_uses_requested_season_labels():
  assert '"Sezon Başlangıcı"' in SOURCE
  assert '"Sezon Bitişi"' in SOURCE
  assert '"Sezon Süresi (gün)"' in SOURCE

  assert (
      "Solar sezon başlangıcı"
      not in SOURCE
  )

  assert (
      "Solar sezon bitişi"
      not in SOURCE
  )

  assert (
      "Sezonluk planlanan operasyon / rota günü"
      not in SOURCE
  )


def test_operating_days_are_user_defined_within_calendar_season():
  assert (
      "season_days = ("
      in SOURCE
  )

  assert (
      "season_end"
      in SOURCE
  )

  assert (
      "season_start"
      in SOURCE
  )

  assert (
      ").days + 1"
      in SOURCE
  )

  assert (
      '"Fiili Operasyon Günü"'
      in SOURCE
  )

  assert (
      "max_value=season_days"
      in SOURCE
  )

  assert (
      "operating_days = season_days"
      not in SOURCE
  )


def test_location_name_is_wired_to_geocoder():
  assert (
      "geocode_location("
      in SOURCE
  )

  assert (
      '"Lokasyonu Çözümle"'
      in SOURCE
  )

  assert (
      "st.button("
      in SOURCE
  )