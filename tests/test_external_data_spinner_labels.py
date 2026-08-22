from pathlib import Path


MARKET = Path("services/market_data.py").read_text(encoding="utf-8")
LOCATION = Path(
    "services/location_geocoding.py"
).read_text(encoding="utf-8")
SOLAR = Path("services/solar_resource.py").read_text(encoding="utf-8")
HOURLY = Path("services/solar_hourly.py").read_text(encoding="utf-8")


def test_market_data_uses_plain_language_spinner_labels():
  assert 'show_spinner="Güncel kur verisi alınıyor..."' in MARKET
  assert (
      'show_spinner="Güncel yakıt fiyatı alınıyor..."'
      in MARKET
  )


def test_location_uses_plain_language_spinner_label():
  assert (
      'show_spinner="Güncel lokasyon verisi alınıyor..."'
      in LOCATION
  )


def test_solar_services_use_plain_language_spinner_labels():
  assert (
      'show_spinner="Güneş enerjisi verisi alınıyor..."'
      in SOLAR
  )
  assert (
      'show_spinner="Saatlik güneş enerjisi profili alınıyor..."'
      in HOURLY
  )


def test_external_cache_calls_do_not_use_default_spinner():
  assert "@st.cache_data(ttl=3600)\n" not in MARKET
  assert "@st.cache_data(ttl=86400)\ndef geocode_location" not in LOCATION
