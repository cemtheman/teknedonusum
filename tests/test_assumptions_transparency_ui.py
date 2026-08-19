from unittest.mock import MagicMock

import pytest

from calculations.assumptions_transparency import AssumptionSourceRow
from ui import assumptions_transparency as transparency_ui


def rows():
  return (
      AssumptionSourceRow(
          parameter="Seyir hızı",
          current_value="6 knot",
          source_type="Kullanıcı girdisi",
          description="Operasyon senaryosu.",
      ),
      AssumptionSourceRow(
          parameter="Komisyon asgari hızı",
          current_value="10 knot",
          source_type="Teknik Komisyon kriteri",
          description="Ayrı uygunluk eşiği.",
      ),
  )


def test_table_has_required_columns():
  table = transparency_ui.build_assumptions_table(rows())

  assert list(table.columns) == [
      "Parametre",
      "Mevcut değer",
      "Kaynak türü",
      "Kısa açıklama",
  ]
  assert len(table) == 2


def test_expander_and_transparency_notice_render(monkeypatch):
  streamlit = MagicMock()
  monkeypatch.setattr(transparency_ui, "st", streamlit)

  transparency_ui.render_assumptions_transparency(rows())

  streamlit.expander.assert_called_once_with(
      "ℹ️ Varsayımlar ve Veri Kaynakları",
      expanded=False,
  )
  streamlit.caption.assert_called_once_with(
      "Ön mühendislik varsayımları doğrulanmış tekne tasarım verisi değildir. "
      "Teknik Komisyon kriterleri bu varsayımlardan ayrıdır. Canlı piyasa "
      "verileri erişilemezse statik yedek değerlere dönebilir."
  )
  table = streamlit.dataframe.call_args.args[0]
  assert len(table) == 2
  streamlit.dataframe.assert_called_once_with(
      table,
      hide_index=True,
      use_container_width=True,
  )


def test_rejects_wrong_row_type():
  with pytest.raises(TypeError, match="AssumptionSourceRow"):
    transparency_ui.build_assumptions_table([object()])
