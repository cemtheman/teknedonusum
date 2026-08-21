from unittest.mock import MagicMock

import pytest

from calculations.normative_vessel_comparison import (
    build_normative_vessel_comparison,
)
from config.vessel_factory import build_vessel_specs
from ui import normative_comparison as comparison_ui


VESSEL_SPECS = build_vessel_specs(108100, 144140, 180180, 50.0)


def test_table_contains_single_clear_cost_meaning():
  comparison = build_normative_vessel_comparison(8.0)
  table = comparison_ui.build_normative_comparison_table(
      comparison,
      VESSEL_SPECS,
  )

  assert list(table.columns) == [
      "Tekne tipi",
      "Yolcu kapasitesi",
      "Toplam kurulu motor gücü",
      "Günlük tahrik enerji talebi",
      "Gerekli nominal batarya",
      "Anahtar teslim piyasa bedeli",
  ]
  assert list(table["Tekne tipi"]) == [
      "Tip 1 — 12 m Tek Gövdeli",
      "Tip 2 — 13,5 m Katamaran",
      "Tip 3 — 14 m Katamaran",
  ]
  assert list(table["Anahtar teslim piyasa bedeli"]) == [
      "€108.100",
      "€144.140",
      "€180.180",
  ]
  assert "Motor + batarya maliyeti" not in table.columns


def test_renderer_uses_same_speed_route_and_no_duplicate_download_cards(monkeypatch):
  streamlit = MagicMock()
  comparison = build_normative_vessel_comparison(7.0, 35.0)
  build_comparison = MagicMock(return_value=comparison)

  monkeypatch.setattr(comparison_ui, "st", streamlit)
  monkeypatch.setattr(
      comparison_ui,
      "build_normative_vessel_comparison",
      build_comparison,
  )

  result = comparison_ui.render_normative_comparison_section(
      VESSEL_SPECS,
      7.0,
      35.0,
  )

  assert result is comparison
  build_comparison.assert_called_once_with(7.0, 35.0)
  streamlit.subheader.assert_called_once_with(
      "⚡ Teknik Ön Boyutlandırma Karşılaştırması"
  )
  streamlit.dataframe.assert_called_once()
  streamlit.download_button.assert_not_called()


def test_table_rejects_wrong_contract():
  with pytest.raises(TypeError, match="NormativeVesselComparisonResult"):
    comparison_ui.build_normative_comparison_table(object(), VESSEL_SPECS)
