"""Join existing technical and economic comparison results for decisions."""

from dataclasses import dataclass

from calculations.economic_comparison import VesselEconomicComparisonRow
from calculations.vessel_comparison import VesselTechnicalComparisonRow
from models.compliance import ComplianceStatus


@dataclass(frozen=True)
class VesselDecisionSummaryRow:
  vessel_id: str
  vessel_name: str
  passenger_capacity: int
  selected_cruise_speed_knots: float
  battery_capacity_kwh: float
  daily_energy_requirement_kwh: float
  solar_energy_contribution_kwh: float
  net_grid_energy_requirement_kwh: float
  estimated_navigation_range_nm: float | None
  commission_compliance_status: ComplianceStatus | None
  investment_cost_tl: float
  grant_amount_tl: float
  net_investment_tl: float
  annual_operating_saving_tl: float
  simple_payback_seasons: float | None
  annual_co2_reduction_t: float


def build_vessel_decision_summary(
    technical_rows,
    economic_rows,
) -> tuple[VesselDecisionSummaryRow, ...]:
  """Join existing comparison rows without adding calculation formulas."""
  technical_rows = tuple(technical_rows)
  economic_rows = tuple(economic_rows)
  expected_ids = ("v1", "v2", "v3")
  if (
      not all(
          isinstance(row, VesselTechnicalComparisonRow)
          for row in technical_rows
      )
      or tuple(row.vessel_id for row in technical_rows) != expected_ids
  ):
    raise ValueError("technical_rows must contain exactly v1, v2, and v3")
  if (
      not all(
          isinstance(row, VesselEconomicComparisonRow)
          for row in economic_rows
      )
      or tuple(row.vessel_id for row in economic_rows) != expected_ids
  ):
    raise ValueError("economic_rows must contain exactly v1, v2, and v3")
  technical_by_id = {row.vessel_id: row for row in technical_rows}
  economic_by_id = {row.vessel_id: row for row in economic_rows}

  return tuple(
      VesselDecisionSummaryRow(
          vessel_id=vessel_id,
          vessel_name=technical_by_id[vessel_id].vessel_name,
          passenger_capacity=(
              technical_by_id[vessel_id].passenger_capacity
          ),
          selected_cruise_speed_knots=(
              technical_by_id[vessel_id].selected_cruise_speed_knots
          ),
          battery_capacity_kwh=(
              technical_by_id[vessel_id].battery_capacity_kwh
          ),
          daily_energy_requirement_kwh=(
              technical_by_id[vessel_id].daily_propulsion_energy_kwh
          ),
          solar_energy_contribution_kwh=(
              technical_by_id[vessel_id].solar_energy_contribution_kwh
          ),
          net_grid_energy_requirement_kwh=(
              technical_by_id[vessel_id].net_grid_energy_requirement_kwh
          ),
          estimated_navigation_range_nm=(
              technical_by_id[vessel_id].estimated_navigation_range_nm
          ),
          commission_compliance_status=(
              technical_by_id[vessel_id].commission_compliance_status
          ),
          investment_cost_tl=economic_by_id[vessel_id].investment_cost_tl,
          grant_amount_tl=economic_by_id[vessel_id].grant_amount_tl,
          net_investment_tl=economic_by_id[vessel_id].net_investment_tl,
          annual_operating_saving_tl=(
              economic_by_id[vessel_id].annual_operating_saving_tl
          ),
          simple_payback_seasons=(
              economic_by_id[vessel_id].simple_payback_seasons
          ),
          annual_co2_reduction_t=(
              economic_by_id[vessel_id].annual_co2_reduction_t
          ),
      )
      for vessel_id in expected_ids
  )
