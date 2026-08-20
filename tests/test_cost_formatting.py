from unittest.mock import MagicMock

import pytest

from ui import inputs
from ui.formatting import format_integer_tr


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (12500, "12.500"),
        (1500000, "1.500.000"),
        (12500.49, "12.500"),
        (12500.5, "12.500"),
        (12500.51, "12.501"),
    ),
)
def test_integer_cost_formatting_is_turkish_and_has_no_fraction(value, expected):
  assert format_integer_tr(value) == expected


def test_cost_input_displays_turkish_grouping_and_returns_integer(monkeypatch):
  streamlit = MagicMock()
  streamlit.text_input.return_value = "150.000"
  monkeypatch.setattr(inputs, "st", streamlit)

  result = inputs._render_cost_input("Birim maliyet", 150000)

  streamlit.text_input.assert_called_once_with("Birim maliyet", value="150.000")
  assert result == 150000


@pytest.mark.parametrize("displayed", (None, "abc", "12,500", "1..500", "0", "-12.500"))
def test_cost_input_rejects_non_turkish_integer_format(monkeypatch, displayed):
  streamlit = MagicMock()
  streamlit.text_input.return_value = displayed
  streamlit.stop.side_effect = RuntimeError("stopped")
  monkeypatch.setattr(inputs, "st", streamlit)

  with pytest.raises(RuntimeError, match="stopped"):
    inputs._render_cost_input("Birim maliyet", 12500)
