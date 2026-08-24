import calculations.inventory_target_allocation as allocation

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
    InventoryVessel,
    analyze_inventory,
)


def _phase_one_vessels(
    count,
    cooperative_status,
    *,
    start=1,
):
    return [
        InventoryVessel(
            row_number=index,
            vessel_name=f"Tekne {index}",
            owner_name=f"Donatan {index}",
            vessel_type="Yolcu Motoru",
            length_m=11.0,
            beam_m=3.5,
            cooperative_status=cooperative_status,
        )
        for index in range(
            start,
            start + count,
        )
    ]


def test_inventory_target_allocation_splits_member_and_non_member_fleet():
    vessels = (
        _phase_one_vessels(
            142,
            COOPERATIVE_MEMBER,
        )
        + _phase_one_vessels(
            124,
            COOPERATIVE_NON_MEMBER,
            start=143,
        )
    )

    analysis = analyze_inventory(vessels)

    plan = allocation.allocate_inventory_target_fleet(
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

    assert plan.phase_one_total == 266
    assert plan.member_vessels == 142
    assert plan.non_member_vessels == 124
    assert plan.unknown_vessels == 0

    assert plan.target_counts == {
        "v1": 71,
        "v2": 43,
        "v3": 28,
        "v4_24": 74,
        "v4_32": 50,
    }

    assert sum(plan.target_counts.values()) == 266
    assert plan.activation_ready is True


def test_unknown_membership_is_not_silently_allocated():
    vessels = (
        _phase_one_vessels(
            10,
            COOPERATIVE_MEMBER,
        )
        + _phase_one_vessels(
            4,
            COOPERATIVE_NON_MEMBER,
            start=11,
        )
        + _phase_one_vessels(
            2,
            COOPERATIVE_UNKNOWN,
            start=15,
        )
    )

    analysis = analyze_inventory(vessels)

    plan = allocation.allocate_inventory_target_fleet(
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

    assert plan.phase_one_total == 16
    assert plan.member_vessels == 10
    assert plan.non_member_vessels == 4
    assert plan.unknown_vessels == 2

    assert sum(plan.target_counts.values()) == 14
    assert plan.activation_ready is False