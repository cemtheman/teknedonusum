"""Tax breakdown for turnkey vessel market-price presentation."""

from dataclasses import dataclass
from math import isfinite

from config.tax_assumptions import (
    SPECIAL_CONSUMPTION_TAX_RATE,
    VALUE_ADDED_TAX_RATE,
)


@dataclass(frozen=True)
class TurnkeyTaxBreakdown:
  net_price_eur: float
  special_consumption_tax_eur: float
  vat_base_eur: float
  vat_eur: float
  gross_price_eur: float


def calculate_turnkey_tax_breakdown(net_price_eur: float) -> TurnkeyTaxBreakdown:
  """Apply ÖTV first, then KDV to net price plus ÖTV."""
  if not isfinite(net_price_eur) or net_price_eur < 0:
    raise ValueError("net_price_eur must be finite and non-negative")

  special_consumption_tax = net_price_eur * SPECIAL_CONSUMPTION_TAX_RATE
  vat_base = net_price_eur + special_consumption_tax
  vat = vat_base * VALUE_ADDED_TAX_RATE
  gross = vat_base + vat

  return TurnkeyTaxBreakdown(
      net_price_eur=net_price_eur,
      special_consumption_tax_eur=special_consumption_tax,
      vat_base_eur=vat_base,
      vat_eur=vat,
      gross_price_eur=gross,
  )
