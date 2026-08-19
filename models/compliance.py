from dataclasses import dataclass
from enum import Enum


class ComplianceStatus(str, Enum):
  PASS = "pass"
  FAIL = "fail"


@dataclass(frozen=True)
class ComplianceCheck:
  criterion: str
  actual_value: float | int
  required_value: str
  status: ComplianceStatus


@dataclass(frozen=True)
class CommissionComplianceResult:
  checks: tuple[ComplianceCheck, ...]
  overall_status: ComplianceStatus

  def __post_init__(self):
    if not self.checks:
      raise ValueError("checks must not be empty")

    all_pass = all(check.status is ComplianceStatus.PASS for check in self.checks)
    any_fail = any(check.status is ComplianceStatus.FAIL for check in self.checks)
    if self.overall_status is ComplianceStatus.PASS and not all_pass:
      raise ValueError("overall PASS requires every check to PASS")
    if self.overall_status is ComplianceStatus.FAIL and not any_fail:
      raise ValueError("overall FAIL requires at least one FAIL check")
