import pytest

from calculations.grant_program import calculate_first_year_grant_program


def test_coverage_distinguishes_budget_capacity_from_actual_allocation():
  specs = {
      "v3": {"totalCost": 1000},
  }
  counts = {"v3": 2}
  grants = {"v3": 600}

  result = calculate_first_year_grant_program(
      specs,
      counts,
      grants,
      ministry_budget_tl=1000,
  )

  assert result.total_grant_need_tl == pytest.approx(1200)
  assert result.budget_coverage_ratio == pytest.approx(1000 / 1200)
  assert result.allocated_grant_tl == pytest.approx(600)
  assert result.allocated_coverage_ratio == pytest.approx(600 / 1200)
  assert result.funded_vessels == 1
  assert result.remaining_budget_tl == pytest.approx(400)
