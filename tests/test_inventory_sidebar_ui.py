from pathlib import Path


SOURCE = Path(
    "ui/inputs.py"
).read_text(
    encoding="utf-8"
)


def test_sidebar_exposes_inventory_excel_module():
  assert (
      '"📊 Filo Envanteri & Dönüşüm Planı"'
      in SOURCE
  )
  assert "st.file_uploader(" in SOURCE
  assert '"Tekne Listesi (.xlsx)"' in SOURCE
  assert 'type=["xlsx"]' in SOURCE


def test_inventory_target_distribution_is_user_configurable():
  assert '"Tip 1 (%)"' in SOURCE
  assert '"Tip 2 (%)"' in SOURCE
  assert '"Tip 3 (%)"' in SOURCE

  assert (
      "target_col1, target_col2, target_col3 = ("
      in SOURCE
  )

  assert (
      "target_total_percent != 100"
      in SOURCE
  )


def test_inventory_uses_analysis_core():
  assert (
      "load_and_analyze_inventory_excel("
      in SOURCE
  )

  assert (
      "target_v1_percent / 100.0"
      in SOURCE
  )

  assert (
      "target_v2_percent / 100.0"
      in SOURCE
  )

  assert (
      "target_v3_percent / 100.0"
      in SOURCE
  )


def test_inventory_plan_requires_explicit_activation():
  assert (
      '"Envanter planını aktif senaryo olarak kullan"'
      in SOURCE
  )

  assert (
      "if inventory_plan_active:"
      in SOURCE
  )


def test_inventory_activation_requires_verified_cooperative_status():
  assert (
      "def _inventory_plan_can_activate("
      in SOURCE
  )

  assert (
      "COOPERATIVE_MEMBER"
      in SOURCE
  )

  assert (
      "disabled=not activation_allowed"
      in SOURCE
  )


def test_unverified_inventory_does_not_override_primary_counts():
  activation_position = SOURCE.index(
      "if inventory_plan_active:"
  )

  count_override_position = SOURCE.index(
      "count_v1 = int("
  )

  assert (
      count_override_position
      > activation_position
  )


def test_active_inventory_plan_overrides_primary_counts_only_after_guard():
  assert (
      "count_v1 = int("
      in SOURCE
  )

  assert (
      'target_counts["v1"]'
      in SOURCE
  )

  assert (
      'target_counts["v2"]'
      in SOURCE
  )

  assert (
      'target_counts["v3"]'
      in SOURCE
  )

  assert (
      "count_v4_24 = 0"
      in SOURCE
  )

  assert (
      "count_v4_32 = 0"
      in SOURCE
  )


def test_sidebar_no_longer_assumes_missing_membership_is_member():
  assert (
      "Excel'de kooperatif üyeliği "
      "bulunmadığından"
      not in SOURCE
  )

  assert (
      "mevcut kooperatif hibe senaryosu "
      "kullanılır"
      not in SOURCE
  )


def test_sidebar_exposes_phase_one_membership_quality():
  assert (
      "**Faz 1 Kooperatif Durumu**"
      in SOURCE
  )

  assert "Kooperatif dışı:" in SOURCE
  assert "Bilinmiyor:" in SOURCE


def test_sidebar_activation_guard_is_present_and_enforced():
  assert (
      "activation_allowed = ("
      in SOURCE
  )

  assert (
      "_inventory_plan_can_activate("
      in SOURCE
  )

  assert (
      "disabled=not activation_allowed"
      in SOURCE
  )

  assert (
      "if inventory_plan_active:"
      in SOURCE
  )
