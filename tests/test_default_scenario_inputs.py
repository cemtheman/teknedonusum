from pathlib import Path

from config.solar_assumptions import DEFAULT_LOCATION_NAME


INPUTS_SOURCE = Path(
    "ui/inputs.py"
).read_text(
    encoding="utf-8"
)


def test_default_location_is_dalyan_mugla():
  assert DEFAULT_LOCATION_NAME == "Dalyan, Muğla"


def test_default_daily_route_is_twenty_nautical_miles():
  assert (
      '"Günlük Rota Mesafesi (deniz mili)"'
      in INPUTS_SOURCE
  )

  assert (
      "min_value=15.0"
      in INPUTS_SOURCE
  )

  assert (
      "max_value=60.0"
      in INPUTS_SOURCE
  )

  assert (
      "value=20.0"
      in INPUTS_SOURCE
  )

  assert (
      "step=5.0"
      in INPUTS_SOURCE
  )


def test_old_route_default_is_not_used():
  assert (
      "value=35.0"
      not in INPUTS_SOURCE
  )