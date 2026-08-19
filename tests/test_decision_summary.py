from dataclasses import replace

import pytest

from calculations.decision_summary import (
    VesselDecisionSummaryRow,
    build_vessel_decision_summary,
)
from calculations.economic_comparison import (
    VesselEconomicComparisonRow,
    build_vessel_economic_comparison,
)
from calculations.vessel_comparison import (
    VesselTechnicalComparisonRow,
    build_vessel_technical_comparison,
)
from config.vessel_factory import build_vessel_specs
from models.compliance import ComplianceStatus


def technical_row(vessel_id, **overrides):
  values = {
      "vessel_id": vessel_id,
      "vessel_name": f"Tip {vessel_id[-1]}",
      "hull_type": "monohull",
      "passenger_capacity": 24,
      "selected_cruise_speed_knots": 6.0,
      "battery_capacity_kwh": 80.0,
      "calculated_cruise_power_kw": 10.0,
      "daily_propulsion_energy_kwh": 50.0,
      "solar_energy_contribution_kwh": 20.0,
      "net_grid_energy_requirement_kwh": 35.0,
      "estimated_navigation_range_nm": 25.0,
      "commission_compliance_status": ComplianceStatus.FAIL,
      "estimate_basis": "preliminary_technical_scenario",
  }
  values.update(overrides)
  return VesselTechnicalComparisonRow(**values)


def economic_row(vessel_id, **overrides):
  values = {
      "vessel_id": vessel_id,
      "vessel_name": f"Tip {vessel_id[-1]}",
      "investment_cost_tl": 6000000.0,
      "grant_amount_tl": 3000000.0,
      "net_investment_tl": 3000000.0,
      "daily_electrical_energy_requirement_kwh": 10.0,
      "annual_electrical_energy_requirement_kwh": 1800.0,
      "annual_electricity_cost_tl": 6300.0,
      "diesel_baseline_annual_fuel_cost_tl": 400000.0,
      "annual_operating_saving_tl": 350000.0,
      "simple_payback_seasons": 5.5,
      "annual_co2_reduction_t": 15.0,
  }
  values.update(overrides)
  return VesselEconomicComparisonRow(**values)


def joined_rows():
  technical = tuple(technical_row(key) for key in ("v1", "v2", "v3"))
  economic = tuple(economic_row(key) for key in ("v1", "v2", "v3"))
  return build_vessel_decision_summary(technical, economic)


def test_joins_exactly_v1_v2_v3_and_maps_fields():
  rows = joined_rows()

  assert all(isinstance(row, VesselDecisionSummaryRow) for row in rows)
  assert [row.vessel_id for row in rows] == ["v1", "v2", "v3"]
  row = rows[0]
  assert row.passenger_capacity == 24
  assert row.daily_propulsion_energy_kwh == 50.0
  assert row.solar_energy_contribution_kwh == 20.0
  assert row.net_grid_energy_requirement_kwh == 35.0
  assert row.investment_cost_tl == 6000000.0
  assert row.grant_amount_tl == 3000000.0
  assert row.annual_operating_saving_tl == 350000.0


def test_unavailable_values_are_preserved():
  technical = tuple(technical_row(key) for key in ("v1", "v2", "v3"))
  technical = (
      technical[0],
      replace(
          technical[1],
          estimated_navigation_range_nm=None,
          commission_compliance_status=None,
      ),
      technical[2],
  )
  economic = tuple(economic_row(key) for key in ("v1", "v2", "v3"))
  economic = (economic[0], replace(economic[1], simple_payback_seasons=None), economic[2])

  row = build_vessel_decision_summary(technical, economic)[1]

  assert row.estimated_navigation_range_nm is None
  assert row.commission_compliance_status is None
  assert row.simple_payback_seasons is None


def test_requires_exact_matching_vessel_ids():
  technical = tuple(technical_row(key) for key in ("v1", "v2"))
  economic = tuple(economic_row(key) for key in ("v1", "v2", "v3"))

  with pytest.raises(ValueError, match="technical_rows must contain exactly"):
    build_vessel_decision_summary(technical, economic)


def test_existing_builder_baselines_flow_through_unchanged():
  specs = build_vessel_specs(108100, 144140, 180180, 55.5)
  technical = build_vessel_technical_comparison(specs, 6.0, 35.0, 8.0)
  economic = build_vessel_economic_comparison(
      specs, 6.0, 35.0, 8.0, 180, 3.5, 81.81, 55.5
  )

  rows = build_vessel_decision_summary(technical, economic)

  assert rows[0].daily_propulsion_energy_kwh == pytest.approx(
      63.19910343132616
  )
  assert rows[0].estimated_navigation_range_nm == pytest.approx(
      28.019807111623393
  )
  assert rows[0].annual_operating_saving_tl == pytest.approx(
      540019.9295150795
  )
  assert rows[2].annual_co2_reduction_t == pytest.approx(39.3737162398229)
