from pathlib import Path


SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")


def test_inventory_target_shares_use_three_columns():
  assert "target_col1, target_col2, target_col3 = st.columns(3)" in SOURCE
  assert '"Tip 1 (%)"' in SOURCE
  assert '"Tip 2 (%)"' in SOURCE
  assert '"Tip 3 (%)"' in SOURCE


def test_inventory_sidebar_no_longer_uses_four_phase_metrics():
  assert "p1, p2, p3, p4 = st.columns(4)" not in SOURCE
  assert "Faz 1:" in SOURCE
  assert "Faz 2:" in SOURCE
  assert "Faz 3:" in SOURCE
  assert "İnceleme:" in SOURCE


def test_inventory_sidebar_uses_compact_active_plan_message():
  assert "Aktif envanter senaryosu:" in SOURCE
  assert "Tip 4 hedefleri sıfırlandı." in SOURCE


def test_inventory_sidebar_keeps_grant_assumption_explicit():
  assert "Excel'de kooperatif üyeliği bulunmadığından" in SOURCE
  assert "Gerçek uygunluk ayrıca doğrulanmalıdır." in SOURCE
