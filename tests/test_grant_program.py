import pytest

from calculations.grant_program import calculate_first_year_grant_program


def _specs():
  return {
      "v1": {"totalCost": 1000},
      "v2": {"totalCost": 1200},
      "v3": {"totalCost": 1500},
      "v4_24": {"totalCost": 1000},
      "v4_32": {"totalCost": 1200},
  }


def test_strict_priority_does_not_skip_to_lower_priority():
  counts = {"v1": 5, "v2": 5, "v3": 5, "v4_24": 5, "v4_32": 5}
  grants = {"v1": 400, "v2": 500, "v3": 600, "v4_24": 300, "v4_32": 350}

  result = calculate_first_year_grant_program(
      _specs(),
      counts,
      grants,
      ministry_budget_tl=1700,
  )

  # Priority 1 can fund only two of five v3 vessels (1200 TL).
  # Remaining 500 TL must NOT be redirected to v2/v1/v4.
  assert result.funded_by_type["v3"] == 2
  assert result.funded_by_type["v2"] == 0
  assert result.funded_by_type["v1"] == 0
  assert result.funded_by_type["v4_24"] == 0
  assert result.funded_by_type["v4_32"] == 0
  assert result.remaining_budget_tl == pytest.approx(500)


def test_lower_priority_opens_only_after_higher_priority_is_fully_funded():
  counts = {"v1": 2, "v2": 2, "v3": 2, "v4_24": 2, "v4_32": 2}
  grants = {"v1": 400, "v2": 500, "v3": 600, "v4_24": 300, "v4_32": 350}

  result = calculate_first_year_grant_program(
      _specs(),
      counts,
      grants,
      ministry_budget_tl=2200,
  )

  assert result.funded_by_type["v3"] == 2
  assert result.funded_by_type["v2"] == 2
  assert result.funded_by_type["v1"] == 0


def test_equal_priority_still_uses_lower_per_vessel_grant_first():
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
