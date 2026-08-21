import pytest

from services.location_geocoding import parse_nominatim_first_result


def test_nominatim_parser_returns_name_and_coordinates():
  name, lat, lon = parse_nominatim_first_result([
      {
          "display_name": "Dalyan, Ortaca, Muğla, Türkiye",
          "lat": "36.8345",
          "lon": "28.6447",
      }
  ])

  assert "Dalyan" in name
  assert lat == pytest.approx(36.8345)
  assert lon == pytest.approx(28.6447)


def test_nominatim_parser_rejects_empty_result():
  with pytest.raises(ValueError):
    parse_nominatim_first_result([])
