from unittest.mock import MagicMock

import pytest

from calculations.presentation import build_technical_scenario_presentation
from calculations.technical_scenario import evaluate_preliminary_technical_scenario
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from ui import technical_scenario as technical_scenario_ui


BASELINE_ARGUMENTS = {
    "geometry": PRELIMINARY_VESSEL_GEOMETRY["v1"],
    "constraints": DALYAN_COMMISSION_CONSTRAINTS,
    "passenger_capacity": 24,
    "speed_knots": 10.0,
    "daily_distance_nm": 35.0,
    "form_factor": 0.15,
    "residual_resistance_n": 1500.0,
    "appendage_resistance_n": 100.0,
    "propulsive_efficiency": 0.60,
    "motor_efficiency": 0.95,
    "design_margin_fraction": 0.15,
    "battery_capacity_kwh": 80.0,
    "usable_energy_fraction": 0.90,
    "operational_reserve_fraction": 0.20,
    "hotel_load_kw": 1.5,
    "roof_length_fraction_of_loa": 0.80,
    "usable_roof_width_m": 3.0,
    "panel_coverage_fraction": 0.85,
    "panel_efficiency": 0.22,
    "peak_sun_hours": 5.5,
    "solar_derating_factor": 0.85,
}


def presentation(**overrides):
  scenario = evaluate_preliminary_technical_scenario(
      **(BASELINE_ARGUMENTS | overrides)
  )
  return build_technical_scenario_presentation(scenario)


def streamlit_mock(monkeypatch):
  streamlit = MagicMock()
  primary_columns = [MagicMock() for _ in range(5)]
  detail_columns = [MagicMock() for _ in range(2)]
  streamlit.columns.side_effect = [primary_columns, detail_columns]
  monkeypatch.setattr(technical_scenario_ui, "st", streamlit)
  return streamlit


def compliance_lines(streamlit):
  return [
      call.args[0] for call in streamlit.markdown.call_args_list
      if call.args and call.args[0].startswith(("✅", "❌"))
  ]


def test_wrong_presentation_type_is_rejected():
  with pytest.raises(
      TypeError,
      match="presentation must be a TechnicalScenarioPresentation",
  ):
    technical_scenario_ui.render_technical_scenario(object())


def test_pass_scenario_rendering_and_formatting(monkeypatch):
  streamlit = streamlit_mock(monkeypatch)

  technical_scenario_ui.render_technical_scenario(presentation())

  streamlit.success.assert_called_once_with("Teknik Komisyon kriterleri: UYGUN")
  streamlit.error.assert_not_called()
  assert streamlit.metric.call_count == 10
  assert [call.args[0] for call in streamlit.metric.call_args_list[:5]] == [
      "Kurulu Motor Gücü",
      "Elektriksel Giriş Gücü",
      "Yalnız Batarya ile Seyir Menzili",
      "Günlük Güneş Enerjisi Üretimi",
      "Güneş Sonrası Net Enerji İhtiyacı",
  ]
  assert [call.args[1] for call in streamlit.metric.call_args_list[:5]] == [
      "25,9 kW",
      "23,7 kW",
      "22,8 NM",
      "25,2 kWh/gün",
      "63,1 kWh/gün",
  ]
  assert [call.args[0] for call in streamlit.metric.call_args_list[5:]] == [
      "Efektif Güç",
      "Motor Çıkış Gücü",
      "Mil Başına Enerji Tüketimi",
      "Güneş Enerjisi Karşılama Oranı",
      "Fazla Güneş Enerjisi",
  ]
  assert [call.args[1] for call in streamlit.metric.call_args_list[5:]] == [
      "13,53 kW",
      "22,54 kW",
      "2,52 kWh/NM",
      "%28,5",
      "0,00 kWh/gün",
  ]

  lines = compliance_lines(streamlit)
  assert len(lines) == 6
  assert all(line.startswith("✅") for line in lines)
  assert [line.split(":", 1)[0] for line in lines] == [
      "✅ Tam Boy (LOA)",
      "✅ Yolcu Kapasitesi",
      "✅ Seyir Menzili",
      "✅ Motor Verimi",
      "✅ Batarya Kapasitesi",
      "✅ Çatı Uzunluğu / LOA",
  ]
  assert not any("Seçilen Senaryo Hızı" in line for line in lines)
  assert "Motor Verimi: %95 · Kriter: ≥ %95" in lines[3]
  assert "Çatı Uzunluğu / LOA: %80 · Kriter: ≥ %80" in lines[5]


def test_fail_scenario_uses_error_and_marks_failed_row(monkeypatch):
  streamlit = streamlit_mock(monkeypatch)

  technical_scenario_ui.render_technical_scenario(
      presentation(roof_length_fraction_of_loa=0.79)
  )

  streamlit.error.assert_called_once_with(
      "Teknik Komisyon kriterleri: UYGUN DEĞİL"
  )
  streamlit.success.assert_not_called()
  assert streamlit.metric.call_count == 10
  lines = compliance_lines(streamlit)
  assert len(lines) == 6
  assert all(line.startswith("✅") for line in lines[:5])
  assert lines[5].startswith("❌ Çatı Uzunluğu / LOA: %79 · Kriter: ≥ %80")


def test_render_structure_calls_are_exact(monkeypatch):
  streamlit = streamlit_mock(monkeypatch)

  technical_scenario_ui.render_technical_scenario(presentation())

  streamlit.divider.assert_called_once_with()
  streamlit.subheader.assert_called_once_with(
      "⚙️ Ön Teknik Uygunluk ve Enerji Değerlendirmesi"
  )
  assert streamlit.columns.call_args_list[0].args == (5,)
  assert streamlit.columns.call_args_list[1].args == (2,)
  streamlit.expander.assert_called_once_with(
      "Teknik Hesap Detayları",
      expanded=False,
  )
  assert [call.args[0] for call in streamlit.caption.call_args_list] == [
      "Bu bölüm, ön tasarım varsayımlarıyla hesaplanan teknik sonuçları "
      "ve Teknik Komisyon kriterlerine göre uygunluk durumunu gösterir. "
      "Operasyon seyir hızı güç ve enerji senaryosunun girdisidir. Komisyonun "
      "istediği tekne hız kabiliyeti, ayrı bir tasarım/azami hız değeri "
      "bulunmadığı için henüz değerlendirilmemiştir.",
      "⚠️ Güç, menzil, güneş enerjisi üretimi ve enerji ihtiyacı sonuçları "
      "ön tasarım tahminleridir; doğrulanmış nihai tekne performans değerleri "
      "değildir.",
      "Efektif güç, teknenin hidrodinamik direncini yenmek için gereken "
      "güçtür. Kurulu motor gücü ise sevk verimi ve tasarım marjı dikkate "
      "alınarak elde edilen ön boyutlandırma değeridir.",
  ]
  streamlit.info.assert_called_once_with(
      "Bu analiz ön mühendislik yapılabilirlik değerlendirmesi amacıyla "
      "hazırlanmıştır. Gerçek tekne geometrisi, direnç/CFD analizleri veya "
      "model deneyleri, pervane eşleştirmesi, üretici motor verileri ve deniz "
      "tecrübeleri ile doğrulanmadan nihai tasarım veya sertifikasyon hesabı "
      "olarak kullanılamaz."
  )
