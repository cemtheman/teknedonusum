"""Explicit Technical Commission minimum and allowed criteria.

These values represent explicit Technical Commission minimum/allowed criteria, not
preliminary naval-architecture assumptions.
"""

from models.constraints import CommissionTechnicalConstraints


# Each value below is an explicit Technical Commission criterion: LOA bounds,
# allowed passenger capacities, minimum speed and navigation range, minimum motor
# efficiency and battery capacity, and minimum roof-length fraction of LOA.
DALYAN_COMMISSION_CONSTRAINTS = CommissionTechnicalConstraints(
    minimum_loa_m=12.0,
    maximum_loa_m=14.0,
    allowed_passenger_capacities=(24, 32, 54),
    minimum_required_speed_knots=10.0,
    minimum_navigation_range_nm=15.0,
    minimum_motor_efficiency=0.95,
    minimum_battery_capacity_kwh=20.0,
    minimum_roof_length_fraction_of_loa=0.80,
)
