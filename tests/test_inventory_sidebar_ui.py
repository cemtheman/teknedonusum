from pathlib import Path


SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")


def test_sidebar_exposes_inventory_excel_module():
  assert '"📊 Filo Envanteri & Dönüşüm Planı"' in SOURCE
  assert 'st.file_uploader(' in SOURCE
  assert '"Tekne Listesi (.xlsx)"' in SOURCE
  assert 'type=["xlsx"]' in SOURCE


def test_inventory_target_distribution_is_user_configurable():
  assert '"Tip 1 hedef payı (%)"' in SOURCE
  assert '"Tip 2 hedef payı (%)"' in SOURCE
  assert '"Tip 3 hedef payı (%)"' in SOURCE
  assert "target_total_percent != 100" in SOURCE


def test_inventory_uses_analysis_core():
  assert "load_and_analyze_inventory_excel(" in SOURCE
  assert '"v1": target_v1_percent / 100.0' in SOURCE
  assert '"v2": target_v2_percent / 100.0' in SOURCE
  assert '"v3": target_v3_percent / 100.0' in SOURCE


def test_inventory_plan_requires_explicit_activation():
  assert '"Envanter planını aktif senaryo olarak kullan"' in SOURCE
  assert "if inventory_plan_active:" in SOURCE


def test_active_inventory_plan_overrides_primary_counts_only():
  assert 'count_v1 = int(target_counts["v1"])' in SOURCE
  assert 'count_v2 = int(target_counts["v2"])' in SOURCE
  assert 'count_v3 = int(target_counts["v3"])' in SOURCE
  assert "count_v4_24 = 0" in SOURCE
  assert "count_v4_32 = 0" in SOURCE


def test_inventory_financing_assumption_is_explicit():
  assert "Excel dosyasında kooperatif üyeliği" in SOURCE
  assert "planlama varsayımıdır" in SOURCE
