"""Fleet inventory parsing, conversion phasing, and target-fleet planning."""

from dataclasses import dataclass
from io import BytesIO
from math import floor, isfinite

import pandas as pd


REQUIRED_COLUMNS = (
    "Tekne Adı",
    "Donatanı",
    "Tekne Cinsi",
    "Boyu (m)",
    "Eni (m)",
)

DIRECT_ELECTRIC_TYPES = {
    "yolcu motoru",
}

PHASE_2_TYPES = {
    "ticari yat",
    "gezinti / tenezzüh gemisi",
    "gezinti/tenezzüh gemisi",
}

PRIVATE_TYPES = {
    "özel tekne",
}

TARGET_PROFILE_IDS = ("v1", "v2", "v3")

DEFAULT_TARGET_SHARES = {
    "v1": 0.50,
    "v2": 0.30,
    "v3": 0.20,
}


@dataclass(frozen=True)
class InventoryVessel:
    row_number: int
    vessel_name: str
    owner_name: str
    vessel_type: str
    length_m: float
    beam_m: float


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
class FleetInventoryAnalysis:
    recommendations: tuple[VesselConversionRecommendation, ...]
    phase_counts: dict[str, int]
    review_count: int
    target_fleet: TargetFleetPlan


def _normalize_text(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_type(value) -> str:
    return " ".join(_normalize_text(value).casefold().split())


def _as_positive_float(value, field_name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc

    if not isfinite(result) or result <= 0:
        raise ValueError(f"{field_name} must be a positive finite number")

    return result


def _find_header_row(raw: pd.DataFrame) -> int:
    required = set(REQUIRED_COLUMNS)

    for row_index in range(len(raw)):
        values = {
            _normalize_text(value)
            for value in raw.iloc[row_index].tolist()
            if _normalize_text(value)
        }
        if required.issubset(values):
            return row_index

    raise ValueError(
        "Excel formatı tanınamadı. Gerekli sütunlar: "
        + ", ".join(REQUIRED_COLUMNS)
    )


def load_inventory_excel(source) -> tuple[InventoryVessel, ...]:
    """Read supported inventory workbook, allowing title/note rows above header."""
    if isinstance(source, (bytes, bytearray)):
        source = BytesIO(source)

    raw = pd.read_excel(source, header=None)
    header_row = _find_header_row(raw)

    # Rewind in-memory streams before second read.
    if hasattr(source, "seek"):
        source.seek(0)

    frame = pd.read_excel(source, header=header_row)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in frame.columns
    ]
    if missing:
        raise ValueError(
            "Eksik zorunlu sütunlar: " + ", ".join(missing)
        )

    frame = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    frame = frame.dropna(how="all")

    vessels = []

    for offset, row in frame.iterrows():
        vessel_name = _normalize_text(row["Tekne Adı"])
        vessel_type = _normalize_text(row["Tekne Cinsi"])

        if not vessel_name and not vessel_type:
            continue

        row_number = int(offset + header_row + 2)

        if not vessel_name:
            raise ValueError(f"Satır {row_number}: Tekne Adı boş")
        if not vessel_type:
            raise ValueError(f"Satır {row_number}: Tekne Cinsi boş")

        vessels.append(
            InventoryVessel(
                row_number=row_number,
                vessel_name=vessel_name,
                owner_name=_normalize_text(row["Donatanı"]),
                vessel_type=vessel_type,
                length_m=_as_positive_float(
                    row["Boyu (m)"], "Boyu (m)"
                ),
                beam_m=_as_positive_float(
                    row["Eni (m)"], "Eni (m)"
                ),
            )
        )

    if not vessels:
        raise ValueError("Excel dosyasında analiz edilebilir tekne kaydı yok")

    return tuple(vessels)


def classify_inventory_vessel(
    vessel: InventoryVessel,
) -> VesselConversionRecommendation:
    """Classify existing vessel by conversion policy, not future target geometry."""
    vessel_type = _normalize_type(vessel.vessel_type)

    if vessel_type in DIRECT_ELECTRIC_TYPES:
        return VesselConversionRecommendation(
            vessel=vessel,
            conversion_phase="Faz 1",
            conversion_priority=1,
            recommended_propulsion="Tam elektrikli",
            recommendation_status="Dönüşüm adayı",
            grant_status="Hibe statüsü doğrulanmalı",
            rationale=(
                "Yolcu motoru doğrudan elektrikli dönüşüm için birinci faz "
                "aday havuzuna alınır. Hedef Tip 1/2/3 dağılımı mevcut teknenin "
                "boy/en ölçüsünden değil kurumun filo planından belirlenir."
            ),
        )

    if vessel_type in PHASE_2_TYPES:
        return VesselConversionRecommendation(
            vessel=vessel,
            conversion_phase="Faz 2",
            conversion_priority=2,
            recommended_propulsion="Hibrit / jeneratör destekli elektrik",
            recommendation_status="Koşullu öneri",
            grant_status="Ayrı finansman senaryosu",
            rationale=(
                "Ticari yat ve gezinti/tenezzüh gemileri için operasyon profili, "
                "mevcut motor gücü ve görev çevrimi doğrulanmadan Faz 1 tam "
                "elektrik filosuna doğrudan alınmaz."
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
                "Özel tekneler ticari yolcu filosu sonrasında değerlendirilir. "
                "İlk planlama senaryosunda kamu hibesi varsayılmaz."
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
            f"{vessel.vessel_type} türü mevcut otomatik dönüşüm sınıflarının "
            "dışındadır; teknik ve operasyonel uygunluk ayrıca değerlendirilmelidir."
        ),
    )


def validate_target_shares(target_shares: dict[str, float]) -> None:
    if set(target_shares) != set(TARGET_PROFILE_IDS):
        raise ValueError("target_shares must contain exactly v1, v2, and v3")

    if any(
        not isfinite(float(value)) or float(value) < 0
        for value in target_shares.values()
    ):
        raise ValueError("target shares must be non-negative finite values")

    if abs(sum(float(v) for v in target_shares.values()) - 1.0) > 1e-9:
        raise ValueError("target shares must sum to 1.0")


def allocate_target_fleet(
    eligible_vessels: int,
    target_shares: dict[str, float] | None = None,
) -> TargetFleetPlan:
    """Allocate exact fleet count using largest-remainder apportionment."""
    if not isinstance(eligible_vessels, int) or eligible_vessels < 0:
        raise ValueError("eligible_vessels must be a non-negative integer")

    shares = dict(
        DEFAULT_TARGET_SHARES if target_shares is None else target_shares
    )
    validate_target_shares(shares)

    quotas = {
        profile_id: eligible_vessels * float(shares[profile_id])
        for profile_id in TARGET_PROFILE_IDS
    }

    counts = {
        profile_id: floor(quotas[profile_id])
        for profile_id in TARGET_PROFILE_IDS
    }

    remainder = eligible_vessels - sum(counts.values())

    ranked = sorted(
        TARGET_PROFILE_IDS,
        key=lambda profile_id: (
            -(quotas[profile_id] - counts[profile_id]),
            TARGET_PROFILE_IDS.index(profile_id),
        ),
    )

    for profile_id in ranked[:remainder]:
        counts[profile_id] += 1

    if sum(counts.values()) != eligible_vessels:
        raise RuntimeError("target fleet allocation failed to preserve total")

    return TargetFleetPlan(
        eligible_phase_one_vessels=eligible_vessels,
        target_shares=shares,
        target_counts=counts,
    )


def analyze_inventory(
    vessels: tuple[InventoryVessel, ...] | list[InventoryVessel],
    *,
    target_shares: dict[str, float] | None = None,
) -> FleetInventoryAnalysis:
    recommendations = tuple(
        classify_inventory_vessel(vessel)
        for vessel in vessels
    )

    phase_counts: dict[str, int] = {}

    for recommendation in recommendations:
        phase = recommendation.conversion_phase
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    phase_one_count = phase_counts.get("Faz 1", 0)

    return FleetInventoryAnalysis(
        recommendations=recommendations,
        phase_counts=phase_counts,
        review_count=phase_counts.get("Özel İnceleme", 0),
        target_fleet=allocate_target_fleet(
            phase_one_count,
            target_shares=target_shares,
        ),
    )


def load_and_analyze_inventory_excel(
    source,
    *,
    target_shares: dict[str, float] | None = None,
) -> FleetInventoryAnalysis:
    return analyze_inventory(
        load_inventory_excel(source),
        target_shares=target_shares,
    )
