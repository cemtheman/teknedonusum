import pytest

from calculations.grant_program import calculate_first_year_grant_program


def test_first_year_allocation_respects_geka_priority_and_complete_vessels():
  specs = {
      "v1": {"totalCost": 1000},
      "v2": {"totalCost": 1200},
      "v3": {"totalCost": 1500},
      "v4_24": {"totalCost": 1000},
      "v4_32": {"totalCost": 1200},
  }
  counts = {"v1": 2, "v2": 2, "v3": 2, "v4_24": 2, "v4_32": 2}
  grants = {"v1": 400, "v2": 500, "v3": 600, "v4_24": 300, "v4_32": 350}

  result = calculate_first_year_grant_program(
      specs,
      counts,
      grants,
      ministry_budget_tl=1200,
      geka_budget_tl=500,
  )

  assert result.total_annual_budget_tl == pytest.approx(1700)
  assert result.funded_by_type["v3"] == 2
  assert result.funded_by_type["v2"] == 1
  assert result.funded_vessels == 3
  assert result.allocated_grant_tl == pytest.approx(1700)
  assert result.remaining_budget_tl == pytest.approx(0)


def test_equal_priority_uses_lower_per_vessel_grant_first():
  specs = {
      "v4_24": {"totalCost": 1000},
      "v4_32": {"totalCost": 1200},
  }
  counts = {"v4_24": 2, "v4_32": 2}
  grants = {"v4_24": 300, "v4_32": 500}

  result = calculate_first_year_grant_program(
      specs,
      counts,
      grants,
      ministry_budget_tl=600,
  )

  assert result.funded_by_type["v4_24"] == 2
  assert result.funded_by_type["v4_32"] == 0


def test_negative_budget_is_rejected():
  with pytest.raises(ValueError):
    calculate_first_year_grant_program(
        {"v3": {"totalCost": 1000}},
        {"v3": 1},
        {"v3": 500},
        ministry_budget_tl=-1,
    )
