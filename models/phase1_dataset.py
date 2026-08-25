"""Faz 1 veri kümesi ve kayıtlar arası ilişki bütünlüğü.

Bu modül tekne envanteri, enerji talebi, arz noktası ve kapasite
kayıtlarını tek bir veri kümesinde toplar. Yalnız kimlik benzersizliği
ve referans bütünlüğü doğrulanır.

Tekne-arz noktası ataması, dönüşüm önceliği, tahrik sistemi önerisi,
sıralama veya optimizasyon sonucu üretilmez.
"""

from dataclasses import dataclass

from models.phase1_supply_demand_capacity import (
  CapacitySnapshot,
  EnergyDemandResult,
  OperationalDemandInput,
  SupplyAvailabilityProfile,
  SupplyPoint,
  VesselInventory,
)


def _unique_values(
  records: tuple,
  field_name: str,
) -> set[str]:
  values = set()

  for record in records:
    value = getattr(record, field_name)

    if value in values:
      raise ValueError(
        f"Tekrarlanan {field_name}: {value}"
      )

    values.add(value)

  return values


def _require_known_references(
  records: tuple,
  *,
  record_id_field: str,
  reference_field: str,
  known_values: set[str],
) -> None:
  for record in records:
    record_id = getattr(
      record,
      record_id_field,
    )
    reference_value = getattr(
      record,
      reference_field,
    )

    if reference_value not in known_values:
      raise ValueError(
        f"{record_id} kaydı bilinmeyen "
        f"{reference_field} içeriyor: "
        f"{reference_value}"
      )


@dataclass(frozen=True)
class Phase1DataSet:
  """Birbiriyle ilişkili Faz 1 veri kayıtlarının değişmez bütünü."""

  vessels: tuple[VesselInventory, ...]
  demand_inputs: tuple[OperationalDemandInput, ...]
  demand_results: tuple[EnergyDemandResult, ...]
  supply_points: tuple[SupplyPoint, ...]
  supply_profiles: tuple[
    SupplyAvailabilityProfile,
    ...,
  ]
  capacity_snapshots: tuple[CapacitySnapshot, ...]

  def __post_init__(self) -> None:
    vessel_ids = _unique_values(
      self.vessels,
      "vessel_id",
    )
    _unique_values(
      self.vessels,
      "plate_number",
    )

    demand_input_ids = _unique_values(
      self.demand_inputs,
      "demand_input_id",
    )
    _require_known_references(
      self.demand_inputs,
      record_id_field="demand_input_id",
      reference_field="vessel_id",
      known_values=vessel_ids,
    )

    _unique_values(
      self.demand_results,
      "demand_result_id",
    )
    _require_known_references(
      self.demand_results,
      record_id_field="demand_result_id",
      reference_field="demand_input_id",
      known_values=demand_input_ids,
    )

    supply_point_ids = _unique_values(
      self.supply_points,
      "supply_point_id",
    )

    _unique_values(
      self.supply_profiles,
      "supply_profile_id",
    )
    _require_known_references(
      self.supply_profiles,
      record_id_field="supply_profile_id",
      reference_field="supply_point_id",
      known_values=supply_point_ids,
    )

    _unique_values(
      self.capacity_snapshots,
      "capacity_snapshot_id",
    )
    _require_known_references(
      self.capacity_snapshots,
      record_id_field="capacity_snapshot_id",
      reference_field="supply_point_id",
      known_values=supply_point_ids,
    )