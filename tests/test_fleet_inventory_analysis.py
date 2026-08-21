from io import BytesIO

import pandas as pd
import pytest

from calculations.fleet_inventory_analysis import (
    InventoryVessel,
    allocate_target_fleet,
    analyze_inventory,
    classify_inventory_vessel,
    load_inventory_excel,
)


def _excel_bytes(rows):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame([
            ["Dalyan / Köyceğiz Mockup Tekne Listesi", None, None, None, None],
            ["Sentetik test verisi", None, None, None, None],
            ["Tekne Adı", "Donatanı", "Tekne Cinsi", "Boyu (m)", "Eni (m)"],
            *rows,
        ]).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="Mockup Tekne Listesi",
        )

    buffer.seek(0)
    return buffer


def _vessel(index, vessel_type):
    return InventoryVessel(
        row_number=index,
        vessel_name=f"Tekne {index}",
        owner_name="Donatan",
        vessel_type=vessel_type,
        length_m=11.0,
        beam_m=3.5,
    )


def test_excel_loader_detects_header_after_title_rows():
    source = _excel_bytes([
        ["Martı", "Ali", "Yolcu Motoru", 11.8, 3.7],
        ["Ada", "Ayşe", "Özel Tekne", 7.2, 2.5],
    ])

    vessels = load_inventory_excel(source)

    assert len(vessels) == 2
    assert vessels[0].vessel_name == "Martı"
    assert vessels[0].vessel_type == "Yolcu Motoru"
    assert vessels[0].length_m == pytest.approx(11.8)
    assert vessels[1].owner_name == "Ayşe"


def test_passenger_motor_enters_phase_one_without_geometry_profile_guess():
    result = classify_inventory_vessel(
        InventoryVessel(
            row_number=4,
            vessel_name="Martı",
            owner_name="Ali",
            vessel_type="Yolcu Motoru",
            length_m=8.0,
            beam_m=2.5,
        )
    )

    assert result.conversion_phase == "Faz 1"
    assert result.conversion_priority == 1
    assert result.recommended_propulsion == "Tam elektrikli"
    assert result.recommendation_status == "Dönüşüm adayı"


@pytest.mark.parametrize(
    ("vessel_type", "expected_phase", "expected_propulsion"),
    [
        (
            "Ticari Yat",
            "Faz 2",
            "Hibrit / jeneratör destekli elektrik",
        ),
        (
            "Gezinti / Tenezzüh Gemisi",
            "Faz 2",
            "Hibrit / jeneratör destekli elektrik",
        ),
        (
            "Özel Tekne",
            "Faz 3",
            "Elektrikli / hibrit",
        ),
    ],
)
def test_supported_categories_have_explicit_conversion_policy(
    vessel_type,
    expected_phase,
    expected_propulsion,
):
    result = classify_inventory_vessel(_vessel(10, vessel_type))

    assert result.conversion_phase == expected_phase
    assert result.recommended_propulsion == expected_propulsion


def test_unknown_type_goes_to_special_review():
    result = classify_inventory_vessel(_vessel(20, "Araba Ferisi"))

    assert result.conversion_phase == "Özel İnceleme"
    assert result.grant_status == "Otomatik hibe tahsisi yok"


def test_default_target_fleet_uses_50_30_20_policy():
    plan = allocate_target_fleet(266)

    assert plan.target_counts == {
        "v1": 133,
        "v2": 80,
        "v3": 53,
    }
    assert sum(plan.target_counts.values()) == 266


def test_largest_remainder_preserves_small_fleet_total():
    plan = allocate_target_fleet(7)

    assert sum(plan.target_counts.values()) == 7
    assert plan.target_counts == {
        "v1": 4,
        "v2": 2,
        "v3": 1,
    }


def test_custom_target_shares_are_supported():
    plan = allocate_target_fleet(
        10,
        {
            "v1": 0.20,
            "v2": 0.30,
            "v3": 0.50,
        },
    )

    assert plan.target_counts == {
        "v1": 2,
        "v2": 3,
        "v3": 5,
    }


@pytest.mark.parametrize(
    "shares",
    [
        {"v1": 0.5, "v2": 0.5},
        {"v1": 0.5, "v2": 0.3, "v3": 0.3},
        {"v1": -0.1, "v2": 0.6, "v3": 0.5},
    ],
)
def test_invalid_target_shares_are_rejected(shares):
    with pytest.raises(ValueError):
        allocate_target_fleet(10, shares)


def test_analysis_builds_phases_and_target_fleet():
    vessels = (
        [_vessel(i, "Yolcu Motoru") for i in range(1, 11)]
        + [_vessel(20, "Ticari Yat")]
        + [_vessel(21, "Gezinti / Tenezzüh Gemisi")]
        + [_vessel(22, "Özel Tekne")]
        + [_vessel(23, "Balık Avlama Teknesi")]
    )

    result = analyze_inventory(vessels)

    assert result.phase_counts["Faz 1"] == 10
    assert result.phase_counts["Faz 2"] == 2
    assert result.phase_counts["Faz 3"] == 1
    assert result.phase_counts["Özel İnceleme"] == 1
    assert result.target_fleet.target_counts == {
        "v1": 5,
        "v2": 3,
        "v3": 2,
    }
    assert result.review_count == 1


def test_loader_rejects_unrecognized_excel_format():
    buffer = BytesIO()
    pd.DataFrame(
        [["Foo", "Bar"], [1, 2]]
    ).to_excel(buffer, index=False, header=False)
    buffer.seek(0)

    with pytest.raises(ValueError, match="Excel formatı tanınamadı"):
        load_inventory_excel(buffer)
