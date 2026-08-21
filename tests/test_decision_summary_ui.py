from unittest.mock import MagicMock

import pytest

from calculations.assumptions_transparency import AssumptionSourceRow
from calculations.decision_summary import VesselDecisionSummaryRow
from ui import decision_summary as decision_summary_ui


def rows():
  common = {
      "selected_cruise_speed_knots": 6.0,
      "battery_capacity_kwh": 100.0,
      "daily_propulsion_energy_kwh": 43.4758,
      "solar_energy_contribution_kwh": 54.432,
      "net_grid_energy_requirement_kwh": 0.0,
      "investment_cost_tl": 7999770.0,
      "grant_amount_tl": 4399873.0,
      "net_investment_tl": 3599897.0,
      "annual_operating_saving_tl": 647576.146,
      "annual_co2_reduction_t": 19.6869,
  }
  return (
      VesselDecisionSummaryRow(
          vessel_id="v1",
          vessel_name="Tip 1",
          passenger_capacity=24,
          estimated_navigation_range_nm=28.0198,
          commission_compliance_status=None,
          simple_payback_seasons=4.9994,
          **common,
      ),
      VesselDecisionSummaryRow(
          vessel_id="v2",
          vessel_name="Tip 2",
          passenger_capacity=32,
          estimated_navigation_range_nm=None,
          commission_compliance_status=None,
          simple_payback_seasons=None,
          **common,
      ),
      VesselDecisionSummaryRow(
          vessel_id="v3",
          vessel_name="Tip 3",
          passenger_capacity=54,
          estimated_navigation_range_nm=None,
          commission_compliance_status=None,
          simple_payback_seasons=2.2005,
          **common,
      ),
  )


def assumption_rows():
  return (
      AssumptionSourceRow(
          "Seyir hızı",
          "6 knot",
          "Kullanıcı girdisi",
          "Mevcut operasyon senaryosu.",
      ),
  )


def test_turkish_formatting_and_unavailable_labels():
  table = decision_summary_ui.build_decision_summary_table(rows())

  assert len(table) == 3
  assert table.loc[0, "Seçilen hız (knot)"] == "6,0"
  assert table.loc[0, "Günlük sevk enerjisi (kWh/gün)"] == "43,5"
  assert table.loc[0, "Yatırım maliyeti"] == "₺7.999.770"
  assert table.loc[0, "Yıllık işletme tasarrufu"] == "₺647.576"
  assert table.loc[0, "Geri ödeme (sezon)"] == "5,0"
  assert table.loc[0, "CO₂ azaltımı (ton/yıl)"] == "19,7"
  assert table.loc[1, "Tahmini menzil (deniz mili)"] == "Mevcut değil"
  assert table.loc[1, "Geri ödeme (sezon)"] == "Mevcut değil"
  assert list(table["Teknik uygunluk"]) == [
      "Henüz değerlendirilmedi",
      "Henüz değerlendirilmedi",
      "Henüz değerlendirilmedi",
  ]


def test_renderer_is_compact_and_renders_three_rows(monkeypatch):
  streamlit = MagicMock()
  monkeypatch.setattr(decision_summary_ui, "st", streamlit)

  decision_summary_ui.render_vessel_decision_summary(rows(), assumption_rows())

  streamlit.expander.assert_called_once_with(
      "Eski model / karşılaştırma amaçlı v0.1 sonuçları",
      expanded=False,
  )
  streamlit.warning.assert_called_once_with(
      "Bu bölüm v0.1 legacy karşılaştırma modelidir; V1/V2/V3 "
      "aynı fizik zincirini kullanmaz. Güç ve batarya değerleri yeni "
      "normative ön boyutlandırmayla doğrudan karşılaştırılmamalıdır. "
      "Ekonomik maliyet bütün tekne yatırım senaryosunu kapsar; primary "
      "v0.2 teknik karar çıktısı yukarıdaki normative bölümdür."
  )
  table = streamlit.dataframe.call_args.args[0]
  assert len(table) == 3
  streamlit.subheader.assert_called_once_with("📊 Tekne Alternatifleri Karar Özeti")
  streamlit.caption.assert_called_once_with(
      "Sonuçlar ön karar-destek tahminleridir; v1 ile v2/v3 şu aşamada "
      "farklı teknik hesap derinliği kullanır. Tam teknik uygunluk, "
      "doğrulanmış tekne hız kabiliyeti dahil tüm kriterler "
      "değerlendirildiğinde belirlenebilir."
  )
  streamlit.dataframe.assert_called_once_with(
      table,
      hide_index=True,
      width="stretch",
  )
  download = streamlit.download_button.call_args
  assert download.args[0] == "📥 Karar Özetini İndir"
  assert isinstance(download.kwargs["data"], bytes)
  assert download.kwargs["file_name"] == "sessiz_akim_karar_ozeti.xlsx"
  assert download.kwargs["mime"] == (
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  )


def test_rejects_wrong_row_type():
  with pytest.raises(TypeError, match="VesselDecisionSummaryRow"):
    decision_summary_ui.build_decision_summary_table([object()])
