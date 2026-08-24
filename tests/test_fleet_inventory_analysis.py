from io import BytesIO

import pandas as pd
import pytest

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
    COOPERATIVE_NON_MEMBER,
    COOPERATIVE_UNKNOWN,
    InventoryVessel,
    allocate_target_fleet,
    analyze_inventory,
    classify_inventory_vessel,
    discover_inventory_table,
    load_and_analyze_inventory_excel,
    load_inventory_excel,
    load_inventory_excel_with_report,
)


def _excel_bytes(
    rows,
    *,
    headers=None,
    title_rows=True,
    sheet_name="Mockup Tekne Listesi",
):
    if headers is None:
        headers = [
            "Tekne Adı",
            "Donatanı",
            "Tekne Cinsi",
            "Boyu (m)",
            "Eni (m)",
        ]

    data = []

    if title_rows:
        data.extend([
            [
                "Dalyan / Köyceğiz Mockup Tekne Listesi",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
                "Sentetik test verisi",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        ])

    data.append(headers)
    data.extend(rows)

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl",
    ) as writer:
        pd.DataFrame(data).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name=sheet_name,
        )

    buffer.seek(0)
    return buffer


def _multi_sheet_excel():
    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl",
    ) as writer:
        pd.DataFrame([
            ["Açıklama", "Değer"],
            ["Not", "Bu sheet envanter değil"],
        ]).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="Açıklama",
        )

        pd.DataFrame([
            ["Filo Envanteri", None, None],
            ["Tekne", "Tekne Türü", "Malik"],
            ["Martı", "Yolcu Motoru", "Ali"],
        ]).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="Tekneler",
        )

    buffer.seek(0)
    return buffer


def _vessel(
    index,
    vessel_type,
    *,
    cooperative_status=COOPERATIVE_UNKNOWN,
):
    return InventoryVessel(
        row_number=index,
        vessel_name=f"Tekne {index}",
        owner_name="Donatan",
        vessel_type=vessel_type,
        length_m=11.0,
        beam_m=3.5,
        cooperative_status=cooperative_status,
    )


def test_excel_loader_detects_header_after_title_rows():
    source = _excel_bytes([
        [
            "Martı",
            "Ali",
            "Yolcu Motoru",
            11.8,
            3.7,
        ],
        [
            "Ada",
            "Ayşe",
            "Özel Tekne",
            7.2,
            2.5,
        ],
    ])

    vessels = load_inventory_excel(source)

    assert len(vessels) == 2
    assert vessels[0].vessel_name == "Martı"
    assert vessels[0].vessel_type == "Yolcu Motoru"
    assert vessels[0].length_m == pytest.approx(11.8)
    assert vessels[1].owner_name == "Ayşe"


def test_discovery_finds_inventory_sheet_among_multiple_sheets():
    source = _multi_sheet_excel()

    sheet_name, header_row, mapping = (
        discover_inventory_table(source)
    )

    assert sheet_name == "Tekneler"
    assert header_row == 1
    assert "Tekne Adı" in mapping
    assert "Tekne Cinsi" in mapping


def test_loader_accepts_common_column_aliases():
    source = _excel_bytes(
        [
            [
                "Martı",
                "Ali",
                "Yolcu Motoru",
                11.8,
                3.7,
                24,
            ],
        ],
        headers=[
            "Tekne",
            "Malik",
            "Tekne Türü",
            "Boy",
            "En",
            "Yolcu Sayısı",
        ],
    )

    loaded = load_inventory_excel_with_report(
        source
    )

    vessel = loaded.vessels[0]

    assert vessel.vessel_name == "Martı"
    assert vessel.owner_name == "Ali"
    assert vessel.vessel_type == "Yolcu Motoru"
    assert vessel.length_m == pytest.approx(11.8)
    assert vessel.beam_m == pytest.approx(3.7)
    assert vessel.passenger_capacity == 24

    mappings = dict(
        loaded.data_quality.alias_mappings
    )

    assert mappings["Tekne"] == "Tekne Adı"
    assert mappings["Malik"] == "Donatanı"
    assert mappings["Tekne Türü"] == "Tekne Cinsi"


def test_missing_vessel_name_gets_traceable_assumed_identifier():
    source = _excel_bytes(
        [
            [
                None,
                "Ali",
                "Yolcu Motoru",
                11.8,
                3.7,
            ],
        ],
    )

    vessel = load_inventory_excel(source)[0]

    assert vessel.vessel_name.startswith(
        "Tekne #"
    )
    assert "Tekne Adı" in vessel.assumed_fields


def test_missing_owner_is_marked_unknown():
    source = _excel_bytes(
        [
            [
                "Martı",
                None,
                "Yolcu Motoru",
                11.8,
                3.7,
            ],
        ],
    )

    vessel = load_inventory_excel(source)[0]

    assert vessel.owner_name == "Bilinmiyor"
    assert "Donatanı" in vessel.assumed_fields


def test_missing_geometry_is_preserved_as_unknown_not_invented():
    source = _excel_bytes(
        [
            [
                "Martı",
                "Ali",
                "Yolcu Motoru",
                None,
                None,
            ],
        ],
    )

    vessel = load_inventory_excel(source)[0]

    assert vessel.length_m is None
    assert vessel.beam_m is None
    assert "Boyu (m)" in vessel.missing_fields
    assert "Eni (m)" in vessel.missing_fields


def test_missing_passenger_capacity_is_not_silently_guessed():
    source = _excel_bytes(
        [
            [
                "Martı",
                "Ali",
                "Yolcu Motoru",
                11.8,
                3.7,
            ],
        ],
    )

    vessel = load_inventory_excel(source)[0]

    assert vessel.passenger_capacity is None
    assert (
        "Yolcu Kapasitesi"
        in vessel.missing_fields
    )


@pytest.mark.parametrize(
    (
        "membership",
        "cooperative",
        "expected_status",
    ),
    [
        (
            "Evet",
            "Dalyan Kooperatifi",
            COOPERATIVE_MEMBER,
        ),
        (
            "Hayır",
            "",
            COOPERATIVE_NON_MEMBER,
        ),
        (
            None,
            "Çandır Kooperatifi",
            COOPERATIVE_MEMBER,
        ),
        (
            None,
            "",
            COOPERATIVE_UNKNOWN,
        ),
    ],
)
def test_cooperative_status_is_normalized(
    membership,
    cooperative,
    expected_status,
):
    source = _excel_bytes(
        [
            [
                "Martı",
                "Ali",
                "Yolcu Motoru",
                11.8,
                3.7,
                cooperative,
                membership,
            ],
        ],
        headers=[
            "Tekne Adı",
            "Donatanı",
            "Tekne Cinsi",
            "Boyu (m)",
            "Eni (m)",
            "Kooperatif",
            "Kooperatif Üyeliği",
        ],
    )

    vessel = load_inventory_excel(source)[0]

    assert (
        vessel.cooperative_status
        == expected_status
    )


def test_missing_cooperative_information_remains_unknown():
    source = _excel_bytes([
        [
            "Martı",
            "Ali",
            "Yolcu Motoru",
            11.8,
            3.7,
        ],
    ])

    vessel = load_inventory_excel(source)[0]

    assert (
        vessel.cooperative_status
        == COOPERATIVE_UNKNOWN
    )
    assert (
        "Kooperatif Üyeliği"
        in vessel.missing_fields
    )


def test_data_quality_report_counts_assumed_and_missing_values():
    source = _excel_bytes(
        [
            [
                None,
                None,
                "Yolcu Motoru",
                None,
                3.7,
            ],
        ],
    )

    loaded = load_inventory_excel_with_report(
        source
    )

    assumed = dict(
        loaded.data_quality.assumed_value_counts
    )
    missing = dict(
        loaded.data_quality.missing_value_counts
    )

    assert assumed["Tekne Adı"] == 1
    assert assumed["Donatanı"] == 1
    assert missing["Boyu (m)"] == 1
    assert missing["Yolcu Kapasitesi"] == 1
    assert missing["Kooperatif Üyeliği"] == 1


def test_analysis_carries_data_quality_report():
    source = _excel_bytes([
        [
            "Martı",
            "Ali",
            "Yolcu Motoru",
            11.8,
            3.7,
        ],
    ])

    result = load_and_analyze_inventory_excel(
        source
    )

    assert result.data_quality is not None
    assert result.data_quality.vessel_count == 1


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
    assert result.recommended_propulsion == (
        "Tam elektrikli"
    )
    assert result.recommendation_status == (
        "Dönüşüm adayı"
    )


def test_phase_one_does_not_imply_cooperative_membership():
    result = classify_inventory_vessel(
        _vessel(
            4,
            "Yolcu Motoru",
            cooperative_status=COOPERATIVE_UNKNOWN,
        )
    )

    assert result.conversion_phase == "Faz 1"
    assert result.grant_status == (
        "Kooperatif üyeliği bilinmiyor — "
        "doğrulama gerekli"
    )


def test_phase_one_member_status_is_preserved():
    result = classify_inventory_vessel(
        _vessel(
            5,
            "Yolcu Motoru",
            cooperative_status=COOPERATIVE_MEMBER,
        )
    )

    assert result.conversion_phase == "Faz 1"
    assert "Kooperatif üyesi" in (
        result.grant_status
    )


def test_phase_one_non_member_status_is_preserved():
    result = classify_inventory_vessel(
        _vessel(
            6,
            "Yolcu Motoru",
            cooperative_status=COOPERATIVE_NON_MEMBER,
        )
    )

    assert result.conversion_phase == "Faz 1"
    assert "Kooperatif dışı" in (
        result.grant_status
    )


@pytest.mark.parametrize(
    (
        "vessel_type",
        "expected_phase",
        "expected_propulsion",
    ),
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
    result = classify_inventory_vessel(
        _vessel(10, vessel_type)
    )

    assert (
        result.conversion_phase
        == expected_phase
    )
    assert (
        result.recommended_propulsion
        == expected_propulsion
    )


def test_unknown_type_goes_to_special_review():
    result = classify_inventory_vessel(
        _vessel(20, "Araba Ferisi")
    )

    assert (
        result.conversion_phase
        == "Özel İnceleme"
    )
    assert (
        result.grant_status
        == "Otomatik hibe tahsisi yok"
    )


def test_default_target_fleet_uses_50_30_20_policy():
    plan = allocate_target_fleet(266)

    assert plan.target_counts == {
        "v1": 133,
        "v2": 80,
        "v3": 53,
    }
    assert (
        sum(plan.target_counts.values())
        == 266
    )


def test_largest_remainder_preserves_small_fleet_total():
    plan = allocate_target_fleet(7)

    assert (
        sum(plan.target_counts.values())
        == 7
    )
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
        {
            "v1": 0.5,
            "v2": 0.5,
        },
        {
            "v1": 0.5,
            "v2": 0.3,
            "v3": 0.3,
        },
        {
            "v1": -0.1,
            "v2": 0.6,
            "v3": 0.5,
        },
    ],
)
def test_invalid_target_shares_are_rejected(
    shares,
):
    with pytest.raises(ValueError):
        allocate_target_fleet(
            10,
            shares,
        )


def test_analysis_builds_phases_and_target_fleet():
    vessels = (
        [
            _vessel(i, "Yolcu Motoru")
            for i in range(1, 11)
        ]
        + [_vessel(20, "Ticari Yat")]
        + [
            _vessel(
                21,
                "Gezinti / Tenezzüh Gemisi",
            )
        ]
        + [_vessel(22, "Özel Tekne")]
        + [
            _vessel(
                23,
                "Balık Avlama Teknesi",
            )
        ]
    )

    result = analyze_inventory(vessels)

    assert result.phase_counts["Faz 1"] == 10
    assert result.phase_counts["Faz 2"] == 2
    assert result.phase_counts["Faz 3"] == 1
    assert (
        result.phase_counts["Özel İnceleme"]
        == 1
    )

    assert result.target_fleet.target_counts == {
        "v1": 5,
        "v2": 3,
        "v3": 2,
    }

    assert result.review_count == 1


def test_loader_rejects_rows_without_vessel_type():
    source = _excel_bytes(
        [
            [
                "Martı",
                "Ali",
                None,
                11.8,
                3.7,
            ],
        ],
    )

    with pytest.raises(
        ValueError,
        match="Tekne Cinsi boş",
    ):
        load_inventory_excel(source)


def test_loader_rejects_unrecognized_excel_format():
    buffer = BytesIO()

    pd.DataFrame(
        [
            ["Foo", "Bar"],
            [1, 2],
        ]
    ).to_excel(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with pytest.raises(
        ValueError,
        match="Excel formatı tanınamadı",
    ):
        load_inventory_excel(buffer)
