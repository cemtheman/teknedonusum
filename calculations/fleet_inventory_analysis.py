"""Fleet inventory discovery, normalization, conversion phasing, and planning."""

from dataclasses import dataclass
from io import BytesIO
from math import floor, isfinite
import re
import unicodedata

import pandas as pd


CANONICAL_FIELDS = (
    "Tekne Adı",
    "Donatanı",
    "Tekne Cinsi",
    "Boyu (m)",
    "Eni (m)",
    "Yolcu Kapasitesi",
    "Kooperatif",
    "Kooperatif Üyeliği",
)

REQUIRED_SEMANTIC_FIELDS = (
    "Tekne Cinsi",
)

TARGET_PROFILE_IDS = ("v1", "v2", "v3")

DEFAULT_TARGET_SHARES = {
    "v1": 0.50,
    "v2": 0.30,
    "v3": 0.20,
}

DIRECT_ELECTRIC_TYPES = {
    "yolcu motoru",
}

PHASE_2_TYPES = {
    "ticari yat",
    "gezinti / tenezzüh gemisi",
    "gezinti/tenezzüh gemisi",
}

EXCURSION_TYPES = {
    "gezinti / tenezzüh gemisi",
    "gezinti/tenezzüh gemisi",
}

PRIVATE_TYPES = {
    "özel tekne",
}

COOPERATIVE_MEMBER = "Kooperatif üyesi"
COOPERATIVE_NON_MEMBER = "Kooperatif dışı"
COOPERATIVE_UNKNOWN = "Bilinmiyor"


FIELD_ALIASES = {
    "Tekne Adı": {
        "tekne adı",
        "tekne adi",
        "tekne",
        "gemi adı",
        "gemi adi",
        "gemi ismi",
        "tekne ismi",
        "adı",
        "adi",
    },
    "Donatanı": {
        "donatanı",
        "donatani",
        "donatan",
        "malik",
        "tekne sahibi",
        "sahibi",
        "işletmeci",
        "isletmeci",
    },
    "Tekne Cinsi": {
        "tekne cinsi",
        "tekne türü",
        "tekne turu",
        "gemi cinsi",
        "gemi türü",
        "gemi turu",
        "cinsi",
        "türü",
        "turu",
    },
    "Boyu (m)": {
        "boyu (m)",
        "boyu",
        "boy (m)",
        "boy",
        "uzunluk (m)",
        "uzunluk",
        "tam boy",
        "loa",
    },
    "Eni (m)": {
        "eni (m)",
        "eni",
        "en (m)",
        "en",
        "genişlik",
        "genislik",
        "beam",
    },
    "Yolcu Kapasitesi": {
        "yolcu kapasitesi",
        "yolcu sayısı",
        "yolcu sayisi",
        "kapasite",
        "kişi kapasitesi",
        "kisi kapasitesi",
        "azami yolcu",
        "maksimum yolcu",
    },
    "Kooperatif": {
        "kooperatif",
        "kooperatif adı",
        "kooperatif adi",
        "kooperatif ismi",
        "bağlı kooperatif",
        "bagli kooperatif",
    },
    "Kooperatif Üyeliği": {
        "kooperatif üyeliği",
        "kooperatif uyeligi",
        "kooperatif üyesi",
        "kooperatif uyesi",
        "üye mi",
        "uye mi",
        "üyelik",
        "uyelik",
    },
}


MEMBER_VALUES = {
    "evet",
    "e",
    "yes",
    "y",
    "üye",
    "uye",
    "üyesi",
    "uyesi",
    "kooperatif üyesi",
    "kooperatif uyesi",
    "1",
    "true",
}

NON_MEMBER_VALUES = {
    "hayır",
    "hayir",
    "h",
    "no",
    "n",
    "değil",
    "degil",
    "üye değil",
    "uye degil",
    "kooperatif dışı",
    "kooperatif disi",
    "0",
    "false",
}

UNKNOWN_VALUES = {
    "",
    "bilinmiyor",
    "bilgi yok",
    "yok",
    "n/a",
    "na",
    "-",
    "?",
}


@dataclass(frozen=True)
class InventoryVessel:
    row_number: int
    vessel_name: str
    owner_name: str
    vessel_type: str
    length_m: float | None
    beam_m: float | None
    passenger_capacity: int | None = None
    cooperative_name: str = ""
    cooperative_status: str = COOPERATIVE_UNKNOWN
    assumed_fields: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    source_columns: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class VesselConversionRecommendation:
    vessel: InventoryVessel
    conversion_phase: str
    conversion_priority: int | None
    recommended_propulsion: str
    recommendation_status: str
    grant_status: str
    rationale: str


@dataclass(frozen=True)
class TargetFleetPlan:
    eligible_phase_one_vessels: int
    target_shares: dict[str, float]
    target_counts: dict[str, int]


@dataclass(frozen=True)
class InventoryDataQuality:
    sheet_name: str
    header_row_number: int
    detected_columns: tuple[str, ...]
    missing_canonical_fields: tuple[str, ...]
    alias_mappings: tuple[tuple[str, str], ...]
    vessel_count: int
    assumed_value_counts: tuple[tuple[str, int], ...]
    missing_value_counts: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class InventoryLoadResult:
    vessels: tuple[InventoryVessel, ...]
    data_quality: InventoryDataQuality


@dataclass(frozen=True)
class FleetInventoryAnalysis:
    recommendations: tuple[VesselConversionRecommendation, ...]
    phase_counts: dict[str, int]
    review_count: int
    target_fleet: TargetFleetPlan
    cooperative_summary: dict[str, dict[str, int]]
    data_quality: InventoryDataQuality | None = None


def _normalize_text(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_lookup_text(value) -> str:
    text = _normalize_text(value).casefold()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.replace("_", " ")
    text = re.sub(r"[^\w\s()/]", " ", text)
    text = " ".join(text.split())

    return text


def _normalize_type(value) -> str:
    return " ".join(_normalize_text(value).casefold().split())


def _alias_lookup() -> dict[str, str]:
    lookup = {}

    for canonical, aliases in FIELD_ALIASES.items():
        lookup[_normalize_lookup_text(canonical)] = canonical

        for alias in aliases:
            lookup[_normalize_lookup_text(alias)] = canonical

    return lookup


ALIAS_LOOKUP = _alias_lookup()


def _canonical_field_name(value) -> str | None:
    normalized = _normalize_lookup_text(value)

    if not normalized:
        return None

    return ALIAS_LOOKUP.get(normalized)


def _as_optional_positive_float(value) -> float | None:
    text = _normalize_text(value)

    if not text:
        return None

    try:
        result = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None

    if not isfinite(result) or result <= 0:
        return None

    return result


def _as_optional_positive_int(value) -> int | None:
    text = _normalize_text(value)

    if not text:
        return None

    try:
        numeric = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None

    if (
        not isfinite(numeric)
        or numeric <= 0
        or abs(numeric - round(numeric)) > 1e-9
    ):
        return None

    return int(round(numeric))


def _normalize_cooperative_status(
    membership_value,
    cooperative_name,
) -> str:
    membership = _normalize_lookup_text(membership_value)
    cooperative = _normalize_text(cooperative_name)

    if membership in MEMBER_VALUES:
        return COOPERATIVE_MEMBER

    if membership in NON_MEMBER_VALUES:
        return COOPERATIVE_NON_MEMBER

    if membership and membership not in UNKNOWN_VALUES:
        return COOPERATIVE_UNKNOWN

    if cooperative:
        normalized_cooperative = _normalize_lookup_text(cooperative)

        if normalized_cooperative not in UNKNOWN_VALUES:
            return COOPERATIVE_MEMBER

    return COOPERATIVE_UNKNOWN


def _header_mapping_from_row(
    row_values,
) -> dict[str, tuple[int, str]]:
    mapping: dict[str, tuple[int, str]] = {}

    for column_index, value in enumerate(row_values):
        canonical = _canonical_field_name(value)

        if canonical is None:
            continue

        if canonical not in mapping:
            mapping[canonical] = (
                column_index,
                _normalize_text(value),
            )

    return mapping


def _candidate_score(
    mapping: dict[str, tuple[int, str]],
) -> tuple[int, int]:
    required_found = sum(
        field in mapping
        for field in REQUIRED_SEMANTIC_FIELDS
    )

    return required_found, len(mapping)


def _read_workbook_bytes(source) -> bytes | None:
    if isinstance(source, bytes):
        return source

    if isinstance(source, bytearray):
        return bytes(source)

    if hasattr(source, "read") and hasattr(source, "seek"):
        current_position = source.tell()
        source.seek(0)
        data = source.read()
        source.seek(current_position)

        if isinstance(data, bytes):
            return data

    return None


def _excel_source_for_reuse(source):
    data = _read_workbook_bytes(source)

    if data is not None:
        return BytesIO(data)

    return source


def discover_inventory_table(source):
    """Find the most plausible inventory table in all workbook sheets."""

    reusable_source = _excel_source_for_reuse(source)
    excel_file = pd.ExcelFile(reusable_source)

    best_candidate = None

    for sheet_name in excel_file.sheet_names:
        raw = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            header=None,
        )

        scan_limit = min(len(raw), 50)

        for row_index in range(scan_limit):
            mapping = _header_mapping_from_row(
                raw.iloc[row_index].tolist()
            )

            score = _candidate_score(mapping)

            if score[0] < len(REQUIRED_SEMANTIC_FIELDS):
                continue

            candidate = (
                score,
                sheet_name,
                row_index,
                mapping,
            )

            if (
                best_candidate is None
                or candidate[0] > best_candidate[0]
            ):
                best_candidate = candidate

    if best_candidate is None:
        raise ValueError(
            "Excel formatı tanınamadı. En azından tekne cinsini "
            "tanımlayan bir sütun bulunmalıdır."
        )

    _, sheet_name, header_row, mapping = best_candidate

    return sheet_name, header_row, mapping


def _prepare_inventory_frame(
    source,
    sheet_name,
    header_row,
    mapping,
):
    reusable_source = _excel_source_for_reuse(source)

    frame = pd.read_excel(
        reusable_source,
        sheet_name=sheet_name,
        header=header_row,
    )

    column_renames = {}

    for canonical, (_, original_name) in mapping.items():
        if original_name in frame.columns:
            column_renames[original_name] = canonical

    frame = frame.rename(columns=column_renames)

    selected = [
        field
        for field in CANONICAL_FIELDS
        if field in frame.columns
    ]

    frame = frame.loc[:, selected].copy()
    frame = frame.dropna(how="all")

    return frame


def _field_source_pairs(mapping):
    pairs = []

    for canonical in CANONICAL_FIELDS:
        if canonical in mapping:
            _, original_name = mapping[canonical]
            pairs.append((canonical, original_name))

    return tuple(pairs)


def load_inventory_excel_with_report(source) -> InventoryLoadResult:
    """Discover and normalize a fleet workbook without inventing hard facts."""

    sheet_name, header_row, mapping = discover_inventory_table(source)

    frame = _prepare_inventory_frame(
        source,
        sheet_name,
        header_row,
        mapping,
    )

    source_columns = _field_source_pairs(mapping)

    vessels = []
    assumed_counts: dict[str, int] = {}
    missing_counts: dict[str, int] = {}

    for offset, row in frame.iterrows():
        vessel_type = _normalize_text(
            row.get("Tekne Cinsi")
        )

        vessel_name = _normalize_text(
            row.get("Tekne Adı")
        )

        if not vessel_type and not vessel_name:
            continue

        row_number = int(offset + header_row + 2)

        if not vessel_type:
            raise ValueError(
                f"Satır {row_number}: Tekne Cinsi boş. "
                "Dönüşüm fazı belirlenemediği için kayıt "
                "otomatik tamamlanamaz."
            )

        assumed_fields = []
        missing_fields = []

        if not vessel_name:
            vessel_name = f"Tekne #{row_number}"
            assumed_fields.append("Tekne Adı")

        owner_name = _normalize_text(
            row.get("Donatanı")
        )

        if not owner_name:
            owner_name = "Bilinmiyor"
            assumed_fields.append("Donatanı")

        length_m = _as_optional_positive_float(
            row.get("Boyu (m)")
        )
        if length_m is None:
            missing_fields.append("Boyu (m)")

        beam_m = _as_optional_positive_float(
            row.get("Eni (m)")
        )
        if beam_m is None:
            missing_fields.append("Eni (m)")

        passenger_capacity = _as_optional_positive_int(
            row.get("Yolcu Kapasitesi")
        )
        if passenger_capacity is None:
            missing_fields.append("Yolcu Kapasitesi")

        cooperative_name = _normalize_text(
            row.get("Kooperatif")
        )

        cooperative_status = _normalize_cooperative_status(
            row.get("Kooperatif Üyeliği"),
            cooperative_name,
        )

        if cooperative_status == COOPERATIVE_UNKNOWN:
            missing_fields.append("Kooperatif Üyeliği")

        for field in assumed_fields:
            assumed_counts[field] = (
                assumed_counts.get(field, 0) + 1
            )

        for field in missing_fields:
            missing_counts[field] = (
                missing_counts.get(field, 0) + 1
            )

        vessels.append(
            InventoryVessel(
                row_number=row_number,
                vessel_name=vessel_name,
                owner_name=owner_name,
                vessel_type=vessel_type,
                length_m=length_m,
                beam_m=beam_m,
                passenger_capacity=passenger_capacity,
                cooperative_name=cooperative_name,
                cooperative_status=cooperative_status,
                assumed_fields=tuple(assumed_fields),
                missing_fields=tuple(missing_fields),
                source_columns=source_columns,
            )
        )

    if not vessels:
        raise ValueError(
            "Excel dosyasında analiz edilebilir tekne kaydı yok"
        )

    detected_columns = tuple(
        field
        for field in CANONICAL_FIELDS
        if field in mapping
    )

    missing_canonical_fields = tuple(
        field
        for field in CANONICAL_FIELDS
        if field not in mapping
    )

    alias_mappings = tuple(
        (
            original_name,
            canonical,
        )
        for canonical, (_, original_name) in mapping.items()
        if _normalize_lookup_text(original_name)
        != _normalize_lookup_text(canonical)
    )

    data_quality = InventoryDataQuality(
        sheet_name=sheet_name,
        header_row_number=header_row + 1,
        detected_columns=detected_columns,
        missing_canonical_fields=missing_canonical_fields,
        alias_mappings=alias_mappings,
        vessel_count=len(vessels),
        assumed_value_counts=tuple(
            sorted(assumed_counts.items())
        ),
        missing_value_counts=tuple(
            sorted(missing_counts.items())
        ),
    )

    return InventoryLoadResult(
        vessels=tuple(vessels),
        data_quality=data_quality,
    )


def load_inventory_excel(source) -> tuple[InventoryVessel, ...]:
    """Backward-compatible inventory loader."""

    return load_inventory_excel_with_report(source).vessels


def _phase_one_grant_status(vessel: InventoryVessel) -> str:
    if vessel.cooperative_status == COOPERATIVE_MEMBER:
        return (
            "Kooperatif üyesi — hibe oranı finansman "
            "aşamasında uygulanacak"
        )

    if vessel.cooperative_status == COOPERATIVE_NON_MEMBER:
        return (
            "Kooperatif dışı — hibe oranı finansman "
            "aşamasında uygulanacak"
        )

    return "Kooperatif üyeliği bilinmiyor — doğrulama gerekli"


def classify_inventory_vessel(
    vessel: InventoryVessel,
) -> VesselConversionRecommendation:
    """Classify conversion phase independently from financing status."""

    vessel_type = _normalize_type(vessel.vessel_type)

    if vessel_type in DIRECT_ELECTRIC_TYPES:
        return VesselConversionRecommendation(
            vessel=vessel,
            conversion_phase="Faz 1",
            conversion_priority=1,
            recommended_propulsion="Tam elektrikli",
            recommendation_status="Dönüşüm adayı",
            grant_status=_phase_one_grant_status(vessel),
            rationale=(
                "Yolcu motoru doğrudan elektrikli dönüşüm için "
                "birinci faz aday havuzuna alınır. Kooperatif "
                "üyeliği dönüşüm fazını belirlemez; finansman "
                "statüsü ayrı değerlendirilir."
            ),
        )

    if vessel_type in PHASE_2_TYPES:
        return VesselConversionRecommendation(
            vessel=vessel,
            conversion_phase="Faz 2",
            conversion_priority=2,
            recommended_propulsion=(
                "Hibrit / jeneratör destekli elektrik"
            ),
            recommendation_status="Koşullu öneri",
            grant_status="Ayrı finansman senaryosu",
            rationale=(
                "Ticari yat ve gezinti/tenezzüh gemileri için "
                "operasyon profili, mevcut motor gücü ve görev "
                "çevrimi doğrulanmadan Faz 1 tam elektrik "
                "filosuna doğrudan alınmaz."
            ),
        )

    if vessel_type in PRIVATE_TYPES:
        return VesselConversionRecommendation(
            vessel=vessel,
            conversion_phase="Faz 3",
            conversion_priority=3,
            recommended_propulsion="Elektrikli / hibrit",
            recommendation_status="Malik kararı",
            grant_status="Varsayılan olarak özkaynak",
            rationale=(
                "Özel tekneler ticari yolcu filosu sonrasında "
                "değerlendirilir. İlk planlama senaryosunda "
                "kamu hibesi varsayılmaz."
            ),
        )

    return VesselConversionRecommendation(
        vessel=vessel,
        conversion_phase="Özel İnceleme",
        conversion_priority=None,
        recommended_propulsion="Teknik inceleme gerekli",
        recommendation_status="İnceleme",
        grant_status="Otomatik hibe tahsisi yok",
        rationale=(
            f"{vessel.vessel_type} türü mevcut otomatik dönüşüm "
            "sınıflarının dışındadır; teknik ve operasyonel "
            "uygunluk ayrıca değerlendirilmelidir."
        ),
    )


def validate_target_shares(
    target_shares: dict[str, float],
) -> None:
    if set(target_shares) != set(TARGET_PROFILE_IDS):
        raise ValueError(
            "target_shares must contain exactly v1, v2, and v3"
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


def allocate_target_fleet(
    eligible_vessels: int,
    target_shares: dict[str, float] | None = None,
) -> TargetFleetPlan:
    """Allocate exact fleet count using largest-remainder apportionment."""

    if (
        not isinstance(eligible_vessels, int)
        or eligible_vessels < 0
    ):
        raise ValueError(
            "eligible_vessels must be a non-negative integer"
        )

    shares = dict(
        DEFAULT_TARGET_SHARES
        if target_shares is None
        else target_shares
    )

    validate_target_shares(shares)

    quotas = {
        profile_id: (
            eligible_vessels
            * float(shares[profile_id])
        )
        for profile_id in TARGET_PROFILE_IDS
    }

    counts = {
        profile_id: floor(quotas[profile_id])
        for profile_id in TARGET_PROFILE_IDS
    }

    remainder = (
        eligible_vessels
        - sum(counts.values())
    )

    ranked = sorted(
        TARGET_PROFILE_IDS,
        key=lambda profile_id: (
            -(
                quotas[profile_id]
                - counts[profile_id]
            ),
            TARGET_PROFILE_IDS.index(profile_id),
        ),
    )

    for profile_id in ranked[:remainder]:
        counts[profile_id] += 1

    if sum(counts.values()) != eligible_vessels:
        raise RuntimeError(
            "target fleet allocation failed to preserve total"
        )

    return TargetFleetPlan(
        eligible_phase_one_vessels=eligible_vessels,
        target_shares=shares,
        target_counts=counts,
    )


def _build_cooperative_summary(
    recommendations: tuple[
        VesselConversionRecommendation,
        ...
    ],
) -> dict[str, dict[str, int]]:
    """Build cooperative-level fleet and conversion-phase counts."""

    summary: dict[str, dict[str, int]] = {}

    for recommendation in recommendations:
        vessel = recommendation.vessel
        cooperative_name = _normalize_text(
            vessel.cooperative_name
        )

        if not cooperative_name:
            continue

        if cooperative_name not in summary:
            summary[cooperative_name] = {
                "total": 0,
                "phase_1": 0,
                "phase_2": 0,
                "passenger_motor": 0,
                "excursion": 0,
            }

        cooperative = summary[cooperative_name]

        cooperative["total"] += 1

        if recommendation.conversion_phase == "Faz 1":
            cooperative["phase_1"] += 1

        if recommendation.conversion_phase == "Faz 2":
            cooperative["phase_2"] += 1

        vessel_type = _normalize_type(
            vessel.vessel_type
        )

        if vessel_type in DIRECT_ELECTRIC_TYPES:
            cooperative["passenger_motor"] += 1

        if vessel_type in EXCURSION_TYPES:
            cooperative["excursion"] += 1

    return summary


def analyze_inventory(
    vessels: (
        tuple[InventoryVessel, ...]
        | list[InventoryVessel]
    ),
    *,
    target_shares: dict[str, float] | None = None,
    data_quality: InventoryDataQuality | None = None,
) -> FleetInventoryAnalysis:
    recommendations = tuple(
        classify_inventory_vessel(vessel)
        for vessel in vessels
    )

    phase_counts: dict[str, int] = {}

    for recommendation in recommendations:
        phase = recommendation.conversion_phase
        phase_counts[phase] = (
            phase_counts.get(phase, 0) + 1
        )

    phase_one_count = phase_counts.get(
        "Faz 1",
        0,
    )

    cooperative_summary = _build_cooperative_summary(
        recommendations
    )

    return FleetInventoryAnalysis(
        recommendations=recommendations,
        phase_counts=phase_counts,
        review_count=phase_counts.get(
            "Özel İnceleme",
            0,
        ),
        target_fleet=allocate_target_fleet(
            phase_one_count,
            target_shares=target_shares,
        ),
        cooperative_summary=cooperative_summary,
        data_quality=data_quality,
    )


def load_and_analyze_inventory_excel(
    source,
    *,
    target_shares: dict[str, float] | None = None,
) -> FleetInventoryAnalysis:
    loaded = load_inventory_excel_with_report(source)

    return analyze_inventory(
        loaded.vessels,
        target_shares=target_shares,
        data_quality=loaded.data_quality,
    )