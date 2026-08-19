from models.compliance import (
    CommissionComplianceResult,
    ComplianceCheck,
    ComplianceStatus,
)
from models.constraints import CommissionTechnicalConstraints


def evaluate_commission_compliance(
    constraints: CommissionTechnicalConstraints,
    loa_m: float,
    passenger_capacity: int,
    navigation_range_nm: float,
    motor_efficiency: float,
    battery_capacity_kwh: float,
    roof_length_fraction_of_loa: float,
) -> CommissionComplianceResult:
  if not isinstance(constraints, CommissionTechnicalConstraints):
    raise TypeError("constraints must be CommissionTechnicalConstraints")
  if not loa_m > 0:
    raise ValueError("loa_m must be positive")
  if not passenger_capacity > 0:
    raise ValueError("passenger_capacity must be positive")
  if not navigation_range_nm >= 0:
    raise ValueError("navigation_range_nm must be non-negative")
  if not 0 < motor_efficiency <= 1:
    raise ValueError("motor_efficiency must be greater than zero and at most one")
  if not battery_capacity_kwh > 0:
    raise ValueError("battery_capacity_kwh must be positive")
  if not 0 < roof_length_fraction_of_loa <= 1:
    raise ValueError(
        "roof_length_fraction_of_loa must be greater than zero and at most one"
    )

  checks = (
      ComplianceCheck(
          criterion="loa",
          actual_value=loa_m,
          required_value=(
              f"{constraints.minimum_loa_m:.1f}–{constraints.maximum_loa_m:.1f} m"
          ),
          status=(
              ComplianceStatus.PASS
              if constraints.minimum_loa_m <= loa_m <= constraints.maximum_loa_m
              else ComplianceStatus.FAIL
          ),
      ),
      ComplianceCheck(
          criterion="passenger_capacity",
          actual_value=passenger_capacity,
          required_value=(
              " / ".join(str(value) for value in constraints.allowed_passenger_capacities)
              + " yolcu"
          ),
          status=(
              ComplianceStatus.PASS
              if passenger_capacity in constraints.allowed_passenger_capacities
              else ComplianceStatus.FAIL
          ),
      ),
      ComplianceCheck(
          criterion="minimum_navigation_range",
          actual_value=navigation_range_nm,
          required_value=f"≥ {constraints.minimum_navigation_range_nm:.1f} NM",
          status=(
              ComplianceStatus.PASS
              if navigation_range_nm >= constraints.minimum_navigation_range_nm
              else ComplianceStatus.FAIL
          ),
      ),
      ComplianceCheck(
          criterion="motor_efficiency",
          actual_value=motor_efficiency,
          required_value=f"≥ %{constraints.minimum_motor_efficiency * 100:.1f}",
          status=(
              ComplianceStatus.PASS
              if motor_efficiency >= constraints.minimum_motor_efficiency
              else ComplianceStatus.FAIL
          ),
      ),
      ComplianceCheck(
          criterion="battery_capacity",
          actual_value=battery_capacity_kwh,
          required_value=f"≥ {constraints.minimum_battery_capacity_kwh:.1f} kWh",
          status=(
              ComplianceStatus.PASS
              if battery_capacity_kwh >= constraints.minimum_battery_capacity_kwh
              else ComplianceStatus.FAIL
          ),
      ),
      ComplianceCheck(
          criterion="roof_length_fraction",
          actual_value=roof_length_fraction_of_loa,
          required_value=(
              "≥ LOA'nın "
              f"%{constraints.minimum_roof_length_fraction_of_loa * 100:.1f}'ı"
          ),
          status=(
              ComplianceStatus.PASS
              if roof_length_fraction_of_loa
              >= constraints.minimum_roof_length_fraction_of_loa
              else ComplianceStatus.FAIL
          ),
      ),
  )
  overall_status = (
      ComplianceStatus.PASS
      if all(check.status is ComplianceStatus.PASS for check in checks)
      else ComplianceStatus.FAIL
  )
  return CommissionComplianceResult(checks=checks, overall_status=overall_status)
