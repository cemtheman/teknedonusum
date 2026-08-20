"""Explicit operating assumption for normative propulsion-energy envelopes."""

from models.operational_energy_envelope import OperationalEnergyAssumption


NORMATIVE_OPERATIONAL_ENERGY_ASSUMPTION = OperationalEnergyAssumption(
    operating_hours_per_day=8.0,
    duty_cycle=0.75,
    assumption_status="normative preliminary operating scenario",
    provenance=(
        "Commit 53 preliminary assumption: selected-speed propulsion power is "
        "drawn during 75% of an 8-hour daily operating window"
    ),
)
