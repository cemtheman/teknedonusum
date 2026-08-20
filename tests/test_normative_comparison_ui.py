from unittest.mock import MagicMock

import pytest

from calculations.normative_vessel_comparison import (
    build_normative_vessel_comparison,
)
from ui import normative_comparison as comparison_ui


def test_table_contains_only_reference_decision_columns():
  comparison = build_normative_vessel_comparison(8.0)
  table = comparison_ui.build_normative_comparison_table(comparison)

  assert list(table.columns) == [
      "Tekne",
      "Yolcu kapasitesi",
      "Toplam kurulu mekanik güç",
      "Günlük enerji",
      "Nominal batarya",
      "Motor + batarya maliyeti",
  ]
  assert list(table["Tekne"]) == [
      "V1 — 12 m conventional displacement monohull",
      "V2 — 13.5 m narrow catamaran",
      "V3 — 14 m higher-capacity catamaran",
  ]
  assert list(table["Yolcu kapasitesi"]) == [24, 32, 54]
  assert list(table["Toplam kurulu mekanik güç"]) == [
      "42,5 kW",
      "42,5 kW",
      "52,5 kW",
  ]
  assert list(table["Günlük enerji"]) == [
      "268,4 kWh/gün",
      "268,4 kWh/gün",
      "331,6 kWh/gün",
  ]
  assert list(table["Nominal batarya"]) == [
      "372,8 kWh",
      "372,8 kWh",
      "460,5 kWh",
  ]
  assert list(table["Motor + batarya maliyeti"]) == [
      "€203.404",
      "€206.804",
      "€255.463",
  ]


def test_renderer_uses_selected_speed_and_existing_exporters(monkeypatch):
  streamlit = MagicMock()
  comparison = build_normative_vessel_comparison(7.0)
  xlsx_content = b"xlsx-content"
  csv_content = b"csv-content"
  build_comparison = MagicMock(return_value=comparison)
  build_xlsx = MagicMock(return_value=xlsx_content)
  build_csv = MagicMock(return_value=csv_content)
  monkeypatch.setattr(comparison_ui, "st", streamlit)
  monkeypatch.setattr(
      comparison_ui,
      "build_normative_vessel_comparison",
      build_comparison,
  )
  monkeypatch.setattr(
      comparison_ui,
      "build_normative_comparison_xlsx",
      build_xlsx,
  )
  monkeypatch.setattr(
      comparison_ui,
      "build_normative_comparison_csv",
      build_csv,
  )

  result = comparison_ui.render_normative_comparison_section(7.0)

  assert result is comparison
  build_comparison.assert_called_once_with(7.0)
  build_xlsx.assert_called_once_with(comparison)
  build_csv.assert_called_once_with(comparison)
  streamlit.subheader.assert_called_once_with(
      "⚖️ Normatif Tekne Karşılaştırması"
  )
  table = streamlit.dataframe.call_args.args[0]
  assert len(table) == 3
  streamlit.dataframe.assert_called_once_with(
      table,
      hide_index=True,
      width="stretch",
  )
  downloads = streamlit.download_button.call_args_list
  assert len(downloads) == 2
  assert downloads[0].kwargs["data"] == xlsx_content
  assert downloads[0].kwargs["file_name"].endswith("_7_kn.xlsx")
  assert downloads[1].kwargs["data"] == csv_content
  assert downloads[1].kwargs["file_name"].endswith("_7_kn.csv")


def test_fractional_speed_is_preserved_in_download_names(monkeypatch):
  streamlit = MagicMock()
  monkeypatch.setattr(comparison_ui, "st", streamlit)

  comparison_ui.render_normative_comparison_section(7.5)

  downloads = streamlit.download_button.call_args_list
  assert downloads[0].kwargs["file_name"].endswith("_7_5_kn.xlsx")
  assert downloads[1].kwargs["file_name"].endswith("_7_5_kn.csv")


def test_renderer_handles_invalid_speed_without_downloads(monkeypatch):
  streamlit = MagicMock()
  monkeypatch.setattr(comparison_ui, "st", streamlit)

  result = comparison_ui.render_normative_comparison_section(5.0)

  assert result is None
  streamlit.error.assert_called_once()
  streamlit.dataframe.assert_not_called()
  streamlit.download_button.assert_not_called()


def test_table_rejects_wrong_contract():
  with pytest.raises(TypeError, match="NormativeVesselComparisonResult"):
    comparison_ui.build_normative_comparison_table(object())
