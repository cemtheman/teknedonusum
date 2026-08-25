from pathlib import Path
from types import SimpleNamespace

import pytest

import ui.fleet_inventory_dashboard as dashboard_module
from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
    InventoryVessel,
    analyze_inventory,
)
from calculations.inventory_target_allocation import (
    allocate_inventory_target_fleet,
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


def _function_source(
    source,
    function_name,
    next_function_name,
):
  return (
      source
      .split(
          f"def {function_name}(",
          1,
      )[1]
      .split(
          f"def {next_function_name}(",
          1,
      )[0]
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


def _mixed_phase_one_analysis():
  vessels = []

  for index in range(1, 6):
    vessels.append(
        _vessel(
            index,
            f"Üye {index}",
            f"Donatan {index}",
            "Yolcu Motoru",
            cooperative_status=COOPERATIVE_MEMBER,
        )
    )

  for index in range(6, 11):
    vessels.append(
        _vessel(
            index,
            f"Dışı {index}",
            f"Donatan {index}",
            "Yolcu Motoru",
            cooperative_status=COOPERATIVE_NON_MEMBER,
        )
    )

  return analyze_inventory(vessels)


def _allocation(analysis):
  return allocate_inventory_target_fleet(
      analysis,
      member_target_shares={
          "v1": 0.50,
          "v2": 0.30,
          "v3": 0.20,
      },
      non_member_target_shares={
          "v4_24": 0.60,
          "v4_32": 0.40,
      },
  )


def test_sidebar_persists_inventory_analysis_in_session_state():
  assert (
      '"fleet_inventory_analysis"'
      in INPUTS_SOURCE
  )

  assert (
      "inventory_analysis"
      in INPUTS_SOURCE
  )

  assert (
      'st.session_state["fleet_inventory_analysis"]'
      in INPUTS_SOURCE
  )

  assert (
      '"fleet_inventory_plan_active"'
      in INPUTS_SOURCE
  )


def test_sidebar_persists_status_aware_inventory_allocation():
  assert (
      '"fleet_inventory_allocation"'
      in INPUTS_SOURCE
  )

  assert (
      'st.session_state["fleet_inventory_allocation"]'
      in INPUTS_SOURCE
  )

  assert (
      "inventory_allocation"
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
      '"fleet_inventory_allocation"'
      in INPUTS_SOURCE
  )

  assert (
      "] = None"
      in INPUTS_SOURCE
  )


def test_app_passes_inventory_allocation_to_dashboard():
  assert (
      'st.session_state.get("fleet_inventory_allocation")'
      in APP_SOURCE
  )

  assert (
      "allocation="
      in APP_SOURCE
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
      "Faz 1 · Yolcu Motorları",
      "Faz 1 Finansman Profil Dağılımı",
      "Faz 1 Finansman İhtiyacı",
      "Tekne bazlı dönüşüm kararları",
  ):
    assert label in DASHBOARD_SOURCE


def test_inventory_dashboard_contains_cooperative_fleet_breakdown():
  assert (
      "Kooperatif Bazlı Filo Dağılımı"
      in DASHBOARD_SOURCE
  )

  for column_label in (
      "Kooperatif",
      "Toplam",
      "Faz 1",
      "Faz 2",
      "Yolcu Motoru",
      "Gezinti / Tenezzüh",
  ):
    assert column_label in DASHBOARD_SOURCE

  assert (
      "analysis.cooperative_summary"
      in DASHBOARD_SOURCE
  )


def test_inventory_dashboard_financing_scope_is_explicit():
  assert (
      "Bu finansman özeti yalnız Faz 1 hedef filosunu kapsar."
      in DASHBOARD_SOURCE
  )

  assert (
      "Faz 2 ve Faz 3 için"
      in DASHBOARD_SOURCE
  )

  assert (
      "Faz 2 hibrit tekneler"
      not in DASHBOARD_SOURCE
  )

  assert (
      "Faz 2 · Hibrit"
      not in DASHBOARD_SOURCE
  )


def test_dashboard_no_longer_uses_obsolete_all_member_financing_copy():
  assert (
      "bütün Faz 1 filosunu "
      "kooperatif üyesi kabul ederek hibe hesaplamak"
      not in DASHBOARD_SOURCE
  )

  assert (
      "yeni hibe tahsis "
      "yöntemi kesinleştirildikten sonra"
      not in DASHBOARD_SOURCE
  )

  assert (
      "yalnız kooperatif üyeliği doğrulanmış Faz 1"
      not in DASHBOARD_SOURCE
  )


def test_dashboard_explains_status_aware_financing():
  assert (
      "Tip 1/2/3"
      in DASHBOARD_SOURCE
  )

  assert (
      "Tip 4A/4B"
      in DASHBOARD_SOURCE
  )

  assert (
      "kooperatif dışı"
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
  assert (
      "st.selectbox("
      in DASHBOARD_SOURCE
  )

  assert (
      '"Dönüşüm fazı"'
      in DASHBOARD_SOURCE
  )

  assert (
      "st.multiselect("
      in DASHBOARD_SOURCE
  )

  assert (
      '"Tekne cinsi"'
      in DASHBOARD_SOURCE
  )


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

  allocation = _allocation(
      analysis
  )

  assert (
      inventory_financing_is_ready(
          allocation
      )
      is False
  )


def test_financing_is_ready_for_non_member_phase_one_vessel():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_NON_MEMBER
  )

  allocation = _allocation(
      analysis
  )

  assert (
      inventory_financing_is_ready(
          allocation
      )
      is True
  )


def test_financing_is_ready_for_member_phase_one_vessel():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_MEMBER
  )

  allocation = _allocation(
      analysis
  )

  assert (
      inventory_financing_is_ready(
          allocation
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

  allocation = _allocation(
      analysis
  )

  assert (
      inventory_financing_is_ready(
          allocation
      )
      is False
  )


def test_calculate_financing_rejects_unknown_membership():
  analysis = _analysis(
      phase_one_status=COOPERATIVE_UNKNOWN
  )

  allocation = _allocation(
      analysis
  )

  with pytest.raises(
      ValueError,
      match="üyeliği bilinmeyen",
  ):
    calculate_inventory_financing(
        allocation,
        vessel_specs={},
        grants_per_type={},
        inputs=None,
    )


def test_calculate_financing_uses_all_five_status_aware_profiles(
    monkeypatch,
):
  analysis = _mixed_phase_one_analysis()

  allocation = _allocation(
      analysis
  )

  vessel_specs = {
      "v1": {
          "totalCost": 100.0,
      },
      "v2": {
          "totalCost": 100.0,
      },
      "v3": {
          "totalCost": 100.0,
      },
      "v4_24": {
          "totalCost": 100.0,
      },
      "v4_32": {
          "totalCost": 100.0,
      },
  }

  grants_per_type = {
      "v1": 50.0,
      "v2": 50.0,
      "v3": 50.0,
      "v4_24": 40.0,
      "v4_32": 40.0,
  }

  inputs = SimpleNamespace(
      grant_budget_ministry_tl=1_000_000.0,
      grant_budget_geka_tl=0.0,
      grant_budget_yikob_tl=0.0,
      grant_budget_zero_waste_tl=0.0,
  )

  fake_program = SimpleNamespace(
      funded_vessels=10,
      unlocked_investment_tl=1000.0,
      allocated_grant_tl=460.0,
  )

  monkeypatch.setattr(
      dashboard_module,
      "calculate_first_year_grant_program",
      lambda *args, **kwargs: fake_program,
  )

  financing = calculate_inventory_financing(
      allocation,
      vessel_specs,
      grants_per_type,
      inputs,
  )

  assert financing["counts"] == {
      "v1": 3,
      "v2": 1,
      "v3": 1,
      "v4_24": 3,
      "v4_32": 2,
  }

  assert (
      sum(
          financing["counts"].values()
      )
      == 10
  )

  assert (
      financing["total_investment_tl"]
      == pytest.approx(1000.0)
  )

  assert (
      financing["total_grant_need_tl"]
      == pytest.approx(450.0)
  )

  assert (
      financing["total_owner_equity_tl"]
      == pytest.approx(550.0)
  )


def test_dashboard_financing_uses_supplied_allocation():
  assert (
      "allocation,"
      in DASHBOARD_SOURCE
  )

  assert (
      "allocation.target_counts"
      in DASHBOARD_SOURCE
  )

  assert (
      'counts["v4_24"]'
      in DASHBOARD_SOURCE
      or '"v4_24":'
      in DASHBOARD_SOURCE
  )

  assert (
      'counts["v4_32"]'
      in DASHBOARD_SOURCE
      or '"v4_32":'
      in DASHBOARD_SOURCE
  )


def test_dashboard_only_blocks_unknown_membership():
  assert (
      "allocation.unknown_vessels"
      in DASHBOARD_SOURCE
  )

  assert (
      "üyeliği bilinmeyen"
      in DASHBOARD_SOURCE
  )

  assert (
      "COOPERATIVE_MEMBER"
      not in DASHBOARD_SOURCE
  )


def test_main_inventory_summary_prioritizes_phase_one():
  render_source = (
      DASHBOARD_SOURCE.split(
          "def render_fleet_inventory_dashboard(",
          1,
      )[1]
  )

  assert (
      "Faz 1 · Yolcu Motorları"
      in render_source
  )

  assert (
      "st.columns(3)"
      in render_source
  )

  assert (
      "st.columns(5)"
      not in render_source
  )

  assert (
      '"Kooperatif Üyesi"'
      in render_source
  )

  assert (
      '"Kooperatif Dışı"'
      in render_source
  )


def test_unknown_membership_is_quiet_when_zero():
  assert (
      "Üyelik verisi eksik:"
      in DASHBOARD_SOURCE
  )

  phase_status_source = _function_source(
      DASHBOARD_SOURCE,
      "_render_phase_one_cooperative_status",
      "_render_target_allocation",
  )

  assert (
      "st.columns(4)"
      not in phase_status_source
  )


def test_target_allocation_uses_scenario_not_optimum_language():
  target_source = _function_source(
      DASHBOARD_SOURCE,
      "_render_target_allocation",
      "_render_financing",
  )

  assert (
      "Faz 1 Finansman Profil Dağılımı"
      in target_source
  )

  assert (
      '"Finansman Profili"'
      in target_source
  )

  assert (
      '"Senaryo Payı"'
      in target_source
  )

  assert (
      "Faz 1 Hedef Filo Dağılımı"
      not in target_source
  )

  assert (
      '"Hedef Tekne Tipi"'
      not in target_source
  )

  assert (
      '"Grup İçi Hedef Pay"'
      not in target_source
  )


def test_financing_metrics_do_not_use_four_column_layout():
  financing_source = _function_source(
      DASHBOARD_SOURCE,
      "_render_financing",
      "render_fleet_inventory_dashboard",
  )

  assert (
      "st.columns(4)"
      not in financing_source
  )

  assert (
      "st.columns(2)"
      in financing_source
  )


def test_secondary_inventory_details_are_collapsible():
  assert (
      "Kooperatif bazlı filo ayrıntısı"
      in DASHBOARD_SOURCE
  )

  assert (
      "Tekne bazlı dönüşüm kararları"
      in DASHBOARD_SOURCE
  )

  assert (
      DASHBOARD_SOURCE.count(
          "with st.expander("
      )
      >= 2
  )


def test_phase_two_is_not_presented_as_locked_hybrid_solution():
  assert (
      "Faz 2 · Hibrit"
      not in DASHBOARD_SOURCE
  )

  assert (
      "Faz 2 hibrit"
      not in DASHBOARD_SOURCE
  )