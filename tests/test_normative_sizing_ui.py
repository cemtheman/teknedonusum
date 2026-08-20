from unittest.mock import MagicMock

import pytest

from config.vessels import BASE_VESSEL_SPECS
from ui import normative_sizing as normative_ui


@pytest.mark.parametrize(
    ("vessel_id", "speed_knots", "expected"),
    (
        ("v1", 6.0, (30.0, 189.47368421052633, 263.1578947368421, 143578.94736842104)),
        ("v2", 8.0, (42.5, 268.42105263157896, 372.8070175438596, 206803.5087719298)),
        ("v3", 10.0, (75.0, 473.6842105263158, 657.8947368421052, 364947.3684210526)),
        ("v1", 7.0, (36.25, 228.94736842105266, 317.9824561403509, 173491.22807017545)),
        ("v3", 9.0, (63.75, 402.63157894736844, 559.2105263157895, 310205.2631578947)),
    ),
)
def test_ui_summary_wiring_preserves_decision_values(
    vessel_id,
    speed_knots,
    expected,
):
  result = normative_ui.build_normative_ui_summary(vessel_id, speed_knots)

  actual = (
      result.reference_estimate_installed_mechanical_power_kw,
      result.reference_estimate_daily_propulsion_energy_kwh,
      result.reference_estimate_nominal_battery_capacity_kwh,
      result.reference_estimate_propulsion_system_cost,
  )
  assert actual == pytest.approx(expected)


def test_existing_vessel_names_map_to_internal_ids():
  result = normative_ui.build_vessel_selection_map(BASE_VESSEL_SPECS)

  assert result == {
      "Tip 1: 12m Monohull": "v1",
      "Tip 2: 13.5m Katamaran": "v2",
      "Tip 3: 14m Katamaran": "v3",
  }


@pytest.mark.parametrize("speed_knots", (4.0, 5.5, 10.5, 11.0))
def test_ui_rejects_speed_outside_normative_range(speed_knots):
  with pytest.raises(ValueError, match="6–10"):
    normative_ui.build_normative_ui_summary("v1", speed_knots)


def test_primary_values_use_existing_cost_formatting_and_total_power():
  result = normative_ui.build_normative_ui_summary("v2", 8.0)
  values = normative_ui.build_primary_display_values(result)

  assert values["mechanical_reference"] == "42,5 kW"
  assert values["mechanical_envelope"] == "30,0–55,0 kW"
  assert values["energy_reference"] == "268,4 kWh/gün"
  assert values["battery_reference"] == "372,8 kWh"
  assert values["cost_reference"] == "€206.804"
  assert values["cost_envelope"] == "€145.979–€267.628"
  assert result.twin_motor_configuration is True


def test_renderer_shows_separate_preliminary_section(monkeypatch):
  streamlit = MagicMock()
  streamlit.selectbox.return_value = "Tip 1: 12m Monohull"
  streamlit.columns.return_value = tuple(MagicMock() for _ in range(4))
  monkeypatch.setattr(normative_ui, "st", streamlit)

  result = normative_ui.render_normative_sizing_section(
      BASE_VESSEL_SPECS,
      6.0,
  )

  assert result.vessel_id == "v1"
  streamlit.subheader.assert_called_once_with(
      "⚡ Elektrikli Tahrik Ön Boyutlandırması"
  )
  assert "nihai tasarım veya sertifikasyon sonucu değildir" in (
      streamlit.caption.call_args.args[0]
  )
  assert streamlit.columns.call_args.args[0] == 4
  assert streamlit.write.call_args_list[0].args[0] == (
      "Tip 1: 12m Monohull · 6,0 kn hizmet hızı"
  )
  metric_labels = [column.metric.call_args.args[0] for column in columns]
  assert metric_labels == [
      "Toplam kurulu mekanik güç",
      "Günlük enerji ihtiyacı",
      "Nominal batarya kapasitesi",
      "Motor + batarya maliyeti",
  ]
  assert all(
      column.caption.call_args.args[0].startswith(
          "Ön değerlendirme aralığı:"
      )
      for column in columns
  )
  assert streamlit.expander.call_args.args[0] == (
      "Varsayımlar ve hesap detayları"
  )


def test_renderer_handles_out_of_range_speed_without_traceback(monkeypatch):
  streamlit = MagicMock()
  streamlit.selectbox.return_value = "Tip 1: 12m Monohull"
  monkeypatch.setattr(normative_ui, "st", streamlit)

  result = normative_ui.render_normative_sizing_section(
      BASE_VESSEL_SPECS,
      5.0,
  )

  assert result is None
  streamlit.error.assert_called_once()
