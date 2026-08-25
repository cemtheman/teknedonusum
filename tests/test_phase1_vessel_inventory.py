from dataclasses import FrozenInstanceError, fields

import pytest

from models.phase1_supply_demand_capacity import (
  ActivityGroup,
  VerificationStatus,
  VesselInventory,
)


def _valid_vessel(**overrides):
  values = {
    "vessel_id": "vessel-001",
    "plate_number": "T-001",
    "vessel_name": "Martı Gecesi",
    "owner_name": "Ali Arslan",
    "vessel_type": "Yolcu Motoru",
    "activity_group": ActivityGroup.COMMERCIAL,
    "length_m": 11.76,
    "beam_m": 3.50,
    "cooperative_id": "dalyan-kooperatifi",
    "verification_status": VerificationStatus.SYNTHETIC,
  }
  values.update(overrides)
  return VesselInventory(**values)


def test_commercial_vessel_accepts_t_plate():
  vessel = _valid_vessel()

  assert vessel.vessel_id == "vessel-001"
  assert vessel.plate_number == "T-001"
  assert vessel.activity_group is ActivityGroup.COMMERCIAL


def test_private_vessel_accepts_o_plate():
  vessel = _valid_vessel(
    plate_number="Ö-001",
    vessel_type="Özel Tekne",
    activity_group=ActivityGroup.PRIVATE,
    cooperative_id=None,
  )

  assert vessel.plate_number == "Ö-001"
  assert vessel.activity_group is ActivityGroup.PRIVATE


@pytest.mark.parametrize(
  "plate_number",
  [
    "",
    " ",
    "T001",
    "T-01",
    "T-000",
    "T-0001",
    "t-001",
    "Ö001",
    "Ö-000",
    "O-001",
    "X-001",
    " T-001 ",
  ],
)
def test_vessel_rejects_invalid_plate_format(plate_number):
  with pytest.raises(ValueError):
    _valid_vessel(plate_number=plate_number)


@pytest.mark.parametrize(
  ("plate_number", "activity_group"),
  [
    ("T-001", ActivityGroup.PRIVATE),
    ("Ö-001", ActivityGroup.COMMERCIAL),
  ],
)
def test_vessel_rejects_plate_and_activity_mismatch(
  plate_number,
  activity_group,
):
  with pytest.raises(ValueError):
    _valid_vessel(
      plate_number=plate_number,
      activity_group=activity_group,
    )


@pytest.mark.parametrize(
  "field_name",
  [
    "vessel_id",
    "vessel_name",
    "owner_name",
    "vessel_type",
  ],
)
def test_vessel_rejects_blank_required_text(field_name):
  with pytest.raises(ValueError):
    _valid_vessel(**{field_name: "  "})


@pytest.mark.parametrize(
  ("field_name", "invalid_value"),
  [
    ("length_m", 0.0),
    ("length_m", -0.1),
    ("beam_m", 0.0),
    ("beam_m", -0.1),
  ],
)
def test_vessel_rejects_invalid_dimensions(
  field_name,
  invalid_value,
):
  with pytest.raises(ValueError):
    _valid_vessel(**{field_name: invalid_value})


def test_vessel_accepts_highest_three_digit_plate_numbers():
  commercial = _valid_vessel(plate_number="T-999")
  private = _valid_vessel(
    plate_number="Ö-999",
    vessel_type="Özel Tekne",
    activity_group=ActivityGroup.PRIVATE,
    cooperative_id=None,
  )

  assert commercial.plate_number == "T-999"
  assert private.plate_number == "Ö-999"


def test_vessel_rejects_blank_cooperative_id_when_present():
  with pytest.raises(ValueError):
    _valid_vessel(cooperative_id="  ")


def test_vessel_requires_activity_group_enum():
  with pytest.raises(ValueError):
    _valid_vessel(activity_group="commercial")


def test_vessel_requires_verification_status_enum():
  with pytest.raises(ValueError):
    _valid_vessel(verification_status="synthetic")


def test_vessel_inventory_is_immutable():
  vessel = _valid_vessel()

  with pytest.raises(FrozenInstanceError):
    vessel.plate_number = "T-002"


def test_vessel_inventory_has_no_redundant_inventory_id():
  model_fields = {field.name for field in fields(VesselInventory)}

  assert "vessel_id" in model_fields
  assert "plate_number" in model_fields
  assert "inventory_id" not in model_fields