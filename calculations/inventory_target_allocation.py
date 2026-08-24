"""Allocate Phase 1 inventory into existing financial/technical fleet profiles."""

from dataclasses import dataclass
from math import floor, isfinite

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
)


MEMBER_PROFILE_IDS = (
    "v1",
    "v2",
    "v3",
)

NON_MEMBER_PROFILE_IDS = (
    "v4_24",
    "v4_32",
)


@dataclass(frozen=True)
class InventoryTargetAllocation:
    phase_one_total: int
    member_vessels: int
    non_member_vessels: int
    unknown_vessels: int
    target_counts: dict[str, int]
    member_target_shares: dict[str, float]
    non_member_target_shares: dict[str, float]
    activation_ready: bool


def _validate_target_shares(
    target_shares: dict[str, float],
    expected_profile_ids: tuple[str, ...],
) -> None:
    if set(target_shares) != set(expected_profile_ids):
        raise ValueError(
            "target shares do not match expected profile ids"
        )

    if any(
        not isfinite(float(value))
        or float(value) < 0
        for value in target_shares.values()
    ):
        raise ValueError(
            "target shares must be non-negative finite values"
        )

    if (
        abs(
            sum(
                float(value)
                for value in target_shares.values()
            )
            - 1.0
        )
        > 1e-9
    ):
        raise ValueError(
            "target shares must sum to 1.0"
        )


def _allocate_counts(
    vessel_count: int,
    target_shares: dict[str, float],
    profile_ids: tuple[str, ...],
) -> dict[str, int]:
    if (
        not isinstance(vessel_count, int)
        or vessel_count < 0
    ):
        raise ValueError(
            "vessel_count must be a non-negative integer"
        )

    _validate_target_shares(
        target_shares,
        profile_ids,
    )

    quotas = {
        profile_id: (
            vessel_count
            * float(target_shares[profile_id])
        )
        for profile_id in profile_ids
    }

    counts = {
        profile_id: floor(quotas[profile_id])
        for profile_id in profile_ids
    }

    remainder = (
        vessel_count
        - sum(counts.values())
    )

    ranked = sorted(
        profile_ids,
        key=lambda profile_id: (
            -(
                quotas[profile_id]
                - counts[profile_id]
            ),
            profile_ids.index(profile_id),
        ),
    )

    for profile_id in ranked[:remainder]:
        counts[profile_id] += 1

    if sum(counts.values()) != vessel_count:
        raise RuntimeError(
            "target allocation failed to preserve total"
        )

    return counts


def _phase_one_status_counts(
    analysis,
) -> dict[str, int]:
    counts = {
        COOPERATIVE_MEMBER: 0,
        COOPERATIVE_NON_MEMBER: 0,
        COOPERATIVE_UNKNOWN: 0,
    }

    for recommendation in analysis.recommendations:
        if recommendation.conversion_phase != "Faz 1":
            continue

        status = recommendation.vessel.cooperative_status

        if status not in counts:
            status = COOPERATIVE_UNKNOWN

        counts[status] += 1

    return counts


def allocate_inventory_target_fleet(
    analysis,
    *,
    member_target_shares: dict[str, float],
    non_member_target_shares: dict[str, float],
) -> InventoryTargetAllocation:
    status_counts = _phase_one_status_counts(
        analysis
    )

    member_vessels = status_counts[
        COOPERATIVE_MEMBER
    ]

    non_member_vessels = status_counts[
        COOPERATIVE_NON_MEMBER
    ]

    unknown_vessels = status_counts[
        COOPERATIVE_UNKNOWN
    ]

    phase_one_total = (
        member_vessels
        + non_member_vessels
        + unknown_vessels
    )

    member_counts = _allocate_counts(
        member_vessels,
        member_target_shares,
        MEMBER_PROFILE_IDS,
    )

    non_member_counts = _allocate_counts(
        non_member_vessels,
        non_member_target_shares,
        NON_MEMBER_PROFILE_IDS,
    )

    target_counts = {
        **member_counts,
        **non_member_counts,
    }

    return InventoryTargetAllocation(
        phase_one_total=phase_one_total,
        member_vessels=member_vessels,
        non_member_vessels=non_member_vessels,
        unknown_vessels=unknown_vessels,
        target_counts=target_counts,
        member_target_shares=dict(
            member_target_shares
        ),
        non_member_target_shares=dict(
            non_member_target_shares
        ),
        activation_ready=(
            phase_one_total > 0
            and unknown_vessels == 0
        ),
    )