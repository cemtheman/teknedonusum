import pytest

from calculations.taxation import calculate_turnkey_tax_breakdown
from config.tax_assumptions import (
    SPECIAL_CONSUMPTION_TAX_RATE,
    VALUE_ADDED_TAX_RATE,
)


def test_tax_rates_are_current_product_assumptions():
  assert SPECIAL_CONSUMPTION_TAX_RATE == pytest.approx(0.08)
  assert VALUE_ADDED_TAX_RATE == pytest.approx(0.20)


def test_turnkey_tax_sequence_is_otv_then_kdv():
  result = calculate_turnkey_tax_breakdown(200000.0)

  assert result.special_consumption_tax_eur == pytest.approx(16000.0)
  assert result.vat_base_eur == pytest.approx(216000.0)
  assert result.vat_eur == pytest.approx(43200.0)
  assert result.gross_price_eur == pytest.approx(259200.0)


@pytest.mark.parametrize("value", (-1.0, float("nan"), float("inf")))
def test_invalid_turnkey_price_is_rejected(value):
  with pytest.raises(ValueError):
    calculate_turnkey_tax_breakdown(value)
