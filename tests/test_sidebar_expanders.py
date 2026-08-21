from pathlib import Path


SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")


def test_sidebar_uses_five_logical_expander_groups():
  for title in (
      "🚢 Filo Dönüşüm Hedefleri",
      "⚓ Operasyon Profili",
      "💶 Anahtar Teslim Piyasa Bedelleri",
      "🌐 Piyasa & Enerji Fiyatları",
      "☀️ Lokasyon, Sezon & Solar Kaynak",
  ):
    assert f'st.expander("{title}"' in SOURCE



def test_all_sidebar_groups_start_collapsed():
  for title in (
      "🚢 Filo Dönüşüm Hedefleri",
      "⚓ Operasyon Profili",
      "💶 Anahtar Teslim Piyasa Bedelleri",
      "🌐 Piyasa & Enerji Fiyatları",
      "☀️ Lokasyon, Sezon & Solar Kaynak",
  ):
    assert f'st.expander("{title}", expanded=False)' in SOURCE


def test_operational_inputs_are_kept_in_operational_profile():
  operation_start = SOURCE.index(
      'with st.expander("⚓ Operasyon Profili", expanded=False):'
  )
  cost_start = SOURCE.index(
      'with st.expander("💶 Anahtar Teslim Piyasa Bedelleri", expanded=False):'
  )
  operation_block = SOURCE[operation_start:cost_start]

  assert '"Günlük Rota Mesafesi (NM)"' in operation_block
  assert '"Ortalama Seyir Hızı (Knot)"' in operation_block
