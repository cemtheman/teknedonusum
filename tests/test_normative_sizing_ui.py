from unittest.mock import MagicMock

import pytest

from config.vessels import BASE_VESSEL_SPECS
from config.vessel_factory import build_vessel_specs
from ui import normative_sizing as normative_ui


VESSEL_SPECS = build_vessel_specs(108100, 144140, 180180, 50.0)


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected"),
    (
        ("v1", 6.0, (30.0, 41.08703676465949, 57.065328839804835)),
        ("v2", 8.0, (42.5, 158.4799303412363, 220.11101436282817)),
        ("v3", 10.0, (75.0, 276.3157894736842, 383.77192982456137)),
    ),
)
def test_ui_summary_preserves_primary_technical_values(
    vessel_id,
    speed_knots,
    expected,
):
  result = normative_ui.build_normative_ui_summary(vessel_id, speed_knots)

  actual = (
      result.reference_estimate_installed_mechanical_power_kw,
      result.reference_estimate_daily_propulsion_energy_kwh,
      result.reference_estimate_nominal_battery_capacity_kwh,
  )
  assert actual == pytest.approx(expected)


def test_vessel_labels_are_fully_turkish():
  result = normative_ui.build_vessel_selection_map(BASE_VESSEL_SPECS)

  assert result == {
      "Tip 1 — 12 m Tek Gövdeli": "v1",
      "Tip 2 — 13,5 m Katamaran": "v2",
      "Tip 3 — 14 m Katamaran": "v3",
  }


def test_primary_values_use_turnkey_market_price_and_tax_breakdown():
  summary = normative_ui.build_normative_ui_summary("v2", 8.0)
  values = normative_ui.build_primary_display_values(summary, 144140)

  assert values["mechanical_reference"] == "42,5 kW"
  assert values["energy_reference"] == "158,5 kWh/gün"
  assert values["battery_reference"] == "220,1 kWh"
  assert values["turnkey_cost"] == "€144.140"
  assert values["tax_inclusive_cost"] == "€186.805"
  assert "cost_reference" not in values


def test_renderer_uses_four_clear_primary_metrics(monkeypatch):
  streamlit = MagicMock()
  streamlit.selectbox.return_value = "Tip 1 — 12 m Tek Gövdeli"
  columns = tuple(MagicMock() for _ in range(4))
  streamlit.columns.return_value = columns
  monkeypatch.setattr(normative_ui, "st", streamlit)

  result = normative_ui.render_normative_sizing_section(
      VESSEL_SPECS,
      6.0,
      35.0,
  )

  assert result.vessel_id == "v1"
  metric_labels = [column.metric.call_args.args[0] for column in columns]
  assert metric_labels == [
      "Toplam kurulu motor gücü",
      "Günlük tahrik enerjisi",
      "Gerekli nominal batarya",
      "Anahtar teslim piyasa bedeli",
  ]
  assert "%8 ÖTV ve %20 KDV hariç" in columns[3].caption.call_args.args[0]
  assert streamlit.expander.call_args.args[0] == "Hesap ayrıntıları"


def test_ui_accepts_five_knot_lower_bound():
  result = normative_ui.build_normative_ui_summary("v1", 5.0)

  assert result.selected_speed_knots == 5.0
  assert result.reference_estimate_daily_propulsion_energy_kwh > 0


@pytest.mark.parametrize("speed_knots", (4.0, 4.5, 10.5, 11.0))
def test_ui_rejects_speed_outside_range(speed_knots):
  with pytest.raises(ValueError, match="5–10"):
    normative_ui.build_normative_ui_summary("v1", speed_knots)


def test_methodology_labels_are_explicit_at_transition():
  assert normative_ui.cruise_methodology_label_tr(6.0) == (
      "Direnç tabanlı ön seyir hesabı"
  )
  assert normative_ui.cruise_methodology_label_tr(6.5) == (
      "Piyasa referanslı ön güç ölçeklemesi"
  )
