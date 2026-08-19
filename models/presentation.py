from dataclasses import dataclass
from enum import Enum

from models.compliance import ComplianceStatus


class TechnicalValueCategory(str, Enum):
  COMMISSION_CRITERION = "commission_criterion"
  PRELIMINARY_ESTIMATE = "preliminary_estimate"


@dataclass(frozen=True)
class TechnicalDisplayValue:
  key: str
  label: str
  value: float
  unit: str
  category: TechnicalValueCategory


@dataclass(frozen=True)
class ComplianceDisplayValue:
  criterion: str
  label: str
  actual_value: float | int
  required_value: str
  status: ComplianceStatus


@dataclass(frozen=True)
class TechnicalScenarioPresentation:
  overall_status: ComplianceStatus
  primary_values: tuple[TechnicalDisplayValue, ...]
  compliance_values: tuple[ComplianceDisplayValue, ...]
  detail_values: tuple[TechnicalDisplayValue, ...]

  def __post_init__(self):
    if not self.primary_values:
      raise ValueError("primary_values must not be empty")
    if not self.compliance_values:
      raise ValueError("compliance_values must not be empty")

    all_pass = all(
        value.status is ComplianceStatus.PASS
        for value in self.compliance_values
    )
    any_fail = any(
        value.status is ComplianceStatus.FAIL
        for value in self.compliance_values
    )
    if self.overall_status is ComplianceStatus.PASS and not all_pass:
      raise ValueError("overall PASS requires every compliance value to PASS")
    if self.overall_status is ComplianceStatus.FAIL and not any_fail:
      raise ValueError("overall FAIL requires at least one compliance value to FAIL")
