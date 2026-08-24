from pathlib import Path

import pytest

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
    InventoryVessel,
    analyze_inventory,
)
from ui.fleet_inventory_dashboard import (
    build_inventory_decision_table,
    build_phase_one_cooperative_summary,
    calculate_inventory_financing,
    inventory_financing_is_ready,
)


APP_SOURCE = Path(
    "app.py"
).read_text(
    encoding="utf-8"
)

INPUTS_SOURCE = Path(
    "ui/inputs.py"
).read_text(
    encoding="utf-8"
)

DASHBOARD_SOURCE = Path(
    "ui/fleet_inventory_dashboard.py"
).read_text(
    encoding="utf-8"
)


def _vessel(
    row_number,
    name,
    owner,
    vessel_type,
    *,
    cooperative_status=COOPERATIVE_UNKNOWN,
):
  return InventoryVessel(
      row_number=row_number,
      vessel_name=name,
      owner_name=owner,
      vessel_type=vessel_type,
      length_m=11.5,
      beam_m=3.5,
      passenger_capacity=24,
      cooperative_status=cooperative_status,
  )


def _analysis(
    *,
    phase_one_status=COOPERATIVE_UNKNOWN,
):
  return analyze_inventory([
      _vessel(
          1,
          "Martı",
          "Ali",
          "Yolcu Motoru",
          cooperative_status=phase_one_status,
      ),
      _vessel(
          2,
          "Ada",
          "Ayşe",
          "Özel Tekne",
      ),
  ])


def test_sidebar_persists_inventory_analysis_in_session_state():
  assert (
      '"fleet_inventory_analysis"'
      in INPUTS_SOURCE
  )

  assert (
      "= inventory_analysis"
      in INPUTS_SOURCE
  )

  assert (
      '"fleet_inventory_plan_active"'
      in INPUTS_SOURCE
  )


def test_sidebar_clears_stale_inventory_when_file_is_removed():
  assert (
      "if inventory_file is None:"
      in INPUTS_SOURCE
  )

  assert (
      '"fleet_inventory_analysis"'
      in INPUTS_SOURCE
  )

  assert (
      "] = None"
      in INPUTS_SOURCE
  )


def test_app_renders_inventory_dashboard_before_fleet_dashboard():
  inventory_pos = APP_SOURCE.index(
      "render_fleet_inventory_dashboard("
  )

  fleet_pos = APP_SOURCE.index(
      "render_fleet_dashboard("
  )

  assert inventory_pos < fleet_pos


def test_inventory_dashboard_contains_expected_sections():
  for label in (
      "📊 Envanter Dönüşüm Analizi",
      "Faz 1 Hedef Filo Dağılımı",
      "Faz 1 Kooperatif Statüsü",
      "Faz 1 Finansman İhtiyacı",
      "Tekne Bazlı Dönüşüm Kararları",
  ):
    assert label in DASHBOARD_SOURCE


def test_inventory_dashboard_financing_scope_is_explicit():
  assert (
      "Bu finansman özeti yalnız Faz 1 hedef filosunu kapsar. "
      in DASHBOARD_SOURCE
  )

  assert (
      "Faz 2 hibrit tekneler ile Faz 3 özel tekneler "
      in DASHBOARD_SOURCE
  )


def test_dashboard_no_longer_assumes_missing_membership_is_member():
  assert (
      "Excel dosyasında kooperatif üyeliği bulunmadığından"
      not in DASHBOARD_SOURCE
  )

  assert (
      "bütün Faz 1 filosunu "
      in DASHBOARD_SOURCE
  )

  assert (
      "kooperatif üyesi kabul ederek hibe hesaplamak "
      in DASHBOARD_SOURCE
  )

  assert (
      "doğru değildir."
      in DASHBOARD_SOURCE
  )


def test_decision_table_exposes_vessel_level_recommendation():
  table = build_inventory_decision_table(
      _analysis()
  )

  assert list(table.columns) == [
      "Tekne Adı",
      "Donatanı",
      "Tekne Cinsi",
      "Boyu (m)",
      "Eni (m)",
      "Yolcu Kapasitesi",
      "Kooperatif",
      "Kooperatif Üyeliği",
      "Dönüşüm Fazı",
      "Önerilen Tahrik",
      "Karar Durumu",
      "Hibe Yaklaşımı",
      "Karar Gerekçesi",
  ]

  assert (
      table.loc[0, "Tekne Adı"]
      == "Martı"
  )

  assert (
      table.loc[0, "Dönüşüm Fazı"]
      == "Faz 1"
  )

  assert (
      table.loc[0, "Kooperatif Üyeliği"]
      == COOPERATIVE_UNKNOWN
  )

  assert (
      table.loc[1, "Dönüşüm Fazı"]
      == "Faz 3"
  )


def test_inventory_dashboard_has_phase_and_type_filters():
  assert "st.selectbox(" in DASHBOARD_SOURCE
  assert '"Dönüşüm fazı"' in DASHBOARD_SOURCE

  assert "st.multiselect(" in DASHBOARD_SOURCE
  assert '"Tekne cinsi"' in DASHBOARD_SOURCE


def test_phase_one_cooperative_summary_separates_statuses():
  analysis = analyze_inventory([
      _vessel(
          1,
          "A",
          "Ali",
          "Yolcu Motoru",
          cooperative_status=COOPERATIVE_MEMBER,
      ),
      _vessel(
          2,
          "B",
          "Ayşe",
          "Yolcu Motoru",
          cooperative_status=COOPERATIVE_NON_MEMBER,
      ),
      _vessel(
          3,
          "C",
          "Can",
          "Yolcu Motoru",
          cooperative_status=COOPERATIVE_UNKNOWN,
      ),
      _vessel(
          4,
          "D",
          "Deniz",
          "Özel Tekne",
          cooperative_status=COOPERATIVE_MEMBER,
      ),
  ])

  summary = build_phase_one_cooperative_summary(
      analysis
  )

  assert summary == {
      "total": 3,
      "member": 1,
      "non_member": 1,
      "unknown": 1,
  }


def test_financing_is_not_ready_when_membership_is_unknown():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_UNKNOWN
  )

  assert (
      inventory_financing_is_ready(
          analysis
      )
      is False
  )


def test_financing_is_not_ready_for_non_member_phase_one_vessel():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_NON_MEMBER
  )

  assert (
      inventory_financing_is_ready(
          analysis
      )
      is False
  )


def test_financing_is_ready_when_all_phase_one_members_are_verified():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_MEMBER
  )

  assert (
      inventory_financing_is_ready(
          analysis
      )
      is True
  )


def test_financing_is_not_ready_without_phase_one_vessels():
  analysis = analyze_inventory([
      _vessel(
          1,
          "Ada",
          "Ayşe",
          "Özel Tekne",
      ),
  ])

  assert (
      inventory_financing_is_ready(
          analysis
      )
      is False
  )


def test_calculate_financing_rejects_unverified_membership():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_UNKNOWN
  )

  with pytest.raises(
      ValueError,
      match=(
          "tüm Faz 1 teknelerinin "
          "kooperatif üyeliği"
      ),
  ):
    calculate_inventory_financing(
        analysis,
        vessel_specs={},
        grants_per_type={},
        inputs=None,
    )


def test_dashboard_explains_financing_guard():
  assert (
      "Envanter kaynaklı hibe hesabı "
      "henüz oluşturulmadı."
      in DASHBOARD_SOURCE
  )

  assert (
      "tekne bazlı kooperatif statüsü "
      in DASHBOARD_SOURCE
  )

  assert (
      "yeni hibe tahsis "
      in DASHBOARD_SOURCE
  )

  assert (
      "yöntemi kesinleştirildikten sonra "
      in DASHBOARD_SOURCE
  )
