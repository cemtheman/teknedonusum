"""Streamlit presentation for assumptions and source transparency."""

import pandas as pd
import streamlit as st

from calculations.assumptions_transparency import AssumptionSourceRow


def build_assumptions_table(rows):
  rows = tuple(rows)
  if any(not isinstance(row, AssumptionSourceRow) for row in rows):
    raise TypeError("rows must contain AssumptionSourceRow values")
  return pd.DataFrame([
      {
          "Parametre": row.parameter,
          "Mevcut değer": row.current_value,
          "Kaynak türü": row.source_type,
          "Kısa açıklama": row.description,
      }
      for row in rows
  ])


def render_assumptions_transparency(rows) -> None:
  table = build_assumptions_table(rows)

  with st.expander("ℹ️ Varsayımlar ve Veri Kaynakları", expanded=False):
    st.caption(
        "Ön mühendislik varsayımları doğrulanmış tekne tasarım verisi değildir. "
        "Teknik Komisyon kriterleri bu varsayımlardan ayrıdır. Canlı piyasa "
        "verileri erişilemezse statik yedek değerlere dönebilir."
    )
    st.dataframe(table, hide_index=True, use_container_width=True)
