"""Create a propulsion-system cost envelope from power and battery bands."""

from math import isfinite

from config.vessels import BASE_VESSEL_SPECS
from models.battery_capacity_envelope import (
    NominalBatteryCapacityEnvelopeResult,
)
from models.power_envelope import InstalledMechanicalPowerEnvelopeResult
from models.propulsion_cost_envelope import PropulsionSystemCostEnvelopeResult


# Existing baseline in calculations/economics.py. It is kept local because the
# production cost module is explicitly outside this commit's change scope.
_EXISTING_MOTOR_COST_PER_KW_EUR = 400.0
_EXISTING_TWIN_MOTOR_SYSTEM_MULTIPLIER = 1.20


def calculate_propulsion_system_cost_envelope(
    vessel_id: str,
    power_envelope: InstalledMechanicalPowerEnvelopeResult,
    battery_envelope: NominalBatteryCapacityEnvelopeResult,
) -> PropulsionSystemCostEnvelopeResult:
  """Apply existing EUR motor and nominal-kWh battery cost assumptions."""
  if vessel_id not in BASE_VESSEL_SPECS:
    raise ValueError("vessel_id must identify an existing vessel specification")
  if not isinstance(power_envelope, InstalledMechanicalPowerEnvelopeResult):
    raise TypeError(
        "power_envelope must be an InstalledMechanicalPowerEnvelopeResult"
    )
  if not isinstance(battery_envelope, NominalBatteryCapacityEnvelopeResult):
    raise TypeError(
        "battery_envelope must be a NominalBatteryCapacityEnvelopeResult"
    )
  if battery_envelope.vessel_id != vessel_id:
    raise ValueError("battery envelope vessel_id must match vessel_id")
  if battery_envelope.speed_knots != power_envelope.speed_knots:
    raise ValueError("power and battery envelope speeds must match")

  spec = BASE_VESSEL_SPECS[vessel_id]
  motor_count = spec["motors"]
  motor_multiplier = (
      _EXISTING_TWIN_MOTOR_SYSTEM_MULTIPLIER
      if motor_count == 2
      else 1.0
  )
  battery_cost_per_kwh = spec["batCostEur"] / spec["batCapacity"]
  if not isfinite(battery_cost_per_kwh) or battery_cost_per_kwh <= 0:
    raise ValueError("existing battery cost per kWh must be finite and positive")

  power = (
      power_envelope.min_installed_mechanical_power_kw,
      power_envelope.reference_installed_power_kw,
      power_envelope.max_installed_mechanical_power_kw,
  )
  battery = (
      battery_envelope.min_nominal_battery_capacity_kwh,
      battery_envelope.reference_nominal_battery_capacity_kwh,
      battery_envelope.max_nominal_battery_capacity_kwh,
  )
  if any(value <= 0 or not isfinite(value) for value in power + battery):
    raise ValueError("power and battery capacity values must be finite and positive")

  motor_cost = tuple(
      value * _EXISTING_MOTOR_COST_PER_KW_EUR * motor_multiplier
      for value in power
  )
  battery_cost = tuple(value * battery_cost_per_kwh for value in battery)
  total_cost = tuple(
      motor + battery_value
      for motor, battery_value in zip(motor_cost, battery_cost)
  )

  return PropulsionSystemCostEnvelopeResult(
      vessel_id=vessel_id,
      speed_knots=power_envelope.speed_knots,
      currency="EUR",
      min_installed_mechanical_power_kw=power[0],
      reference_installed_mechanical_power_kw=power[1],
      max_installed_mechanical_power_kw=power[2],
      min_nominal_battery_capacity_kwh=battery[0],
      reference_nominal_battery_capacity_kwh=battery[1],
      max_nominal_battery_capacity_kwh=battery[2],
      motor_count=motor_count,
      motor_cost_per_total_installed_kw=_EXISTING_MOTOR_COST_PER_KW_EUR,
      motor_system_multiplier=motor_multiplier,
      battery_cost_per_nominal_kwh=battery_cost_per_kwh,
      cost_basis_provenance=(
          "Existing calculations/economics.py motor baseline and "
          "config/vessels.py battery baseline"
      ),
      min_motor_system_cost=motor_cost[0],
      reference_motor_system_cost=motor_cost[1],
      max_motor_system_cost=motor_cost[2],
      min_battery_system_cost=battery_cost[0],
      reference_battery_system_cost=battery_cost[1],
      max_battery_system_cost=battery_cost[2],
      min_total_propulsion_system_cost=total_cost[0],
      reference_total_propulsion_system_cost=total_cost[1],
      max_total_propulsion_system_cost=total_cost[2],
  )
