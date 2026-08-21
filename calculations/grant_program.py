from dataclasses import dataclass
from itertools import groupby


GEKA_PRIORITY = {
    "v3": 1,
    "v2": 2,
    "v1": 3,
    "v4_24": 4,
    "v4_32": 4,
}


@dataclass(frozen=True)
class GrantProgramResult:
  total_annual_budget_tl: float
  total_grant_need_tl: float
  budget_coverage_ratio: float
  allocated_coverage_ratio: float
  funded_vessels: int
  funded_by_type: dict
  allocated_grant_tl: float
  remaining_budget_tl: float
  unlocked_investment_tl: float
  required_owner_equity_tl: float


def calculate_first_year_grant_program(
    vessel_specs,
    counts,
    grants_per_type,
    *,
    ministry_budget_tl=0.0,
    geka_budget_tl=0.0,
    yikob_budget_tl=0.0,
    zero_waste_budget_tl=0.0,
):
  budgets = (
      ministry_budget_tl,
      geka_budget_tl,
      yikob_budget_tl,
      zero_waste_budget_tl,
  )
  if any(value < 0 for value in budgets):
    raise ValueError("Grant budgets must be non-negative")

  total_budget = float(sum(budgets))
  total_need = float(
      sum(counts[key] * grants_per_type[key] for key in counts)
  )

  funded_by_type = {key: 0 for key in counts}
  remaining = total_budget
  allocated = 0.0
  unlocked_investment = 0.0
  owner_equity = 0.0

  ordered_types = sorted(
      counts,
      key=lambda key: (
          GEKA_PRIORITY.get(key, 999),
          grants_per_type[key],
          key,
      ),
  )

  stop_after_priority = False

  for priority, grouped in groupby(
      ordered_types,
      key=lambda key: GEKA_PRIORITY.get(key, 999),
  ):
    priority_keys = list(grouped)

    for key in priority_keys:
      per_vessel_grant = float(grants_per_type[key])
      if per_vessel_grant <= 0:
        continue

      requested = int(counts[key])
      if requested <= 0:
        continue

      affordable = int(remaining // per_vessel_grant)
      funded = min(requested, affordable)

      if funded > 0:
        funded_by_type[key] = funded
        grant_amount = funded * per_vessel_grant
        allocated += grant_amount
        remaining -= grant_amount

        total_cost = float(vessel_specs[key]["totalCost"])
        unlocked_investment += funded * total_cost
        owner_equity += funded * (total_cost - per_vessel_grant)

      if funded < requested:
        stop_after_priority = True
        break

    if stop_after_priority:
      break

  funded_vessels = sum(funded_by_type.values())
  budget_coverage_ratio = (
      min(total_budget, total_need) / total_need
      if total_need else 0.0
  )
  allocated_coverage_ratio = (
      allocated / total_need
      if total_need else 0.0
  )

  return GrantProgramResult(
      total_annual_budget_tl=total_budget,
      total_grant_need_tl=total_need,
      budget_coverage_ratio=budget_coverage_ratio,
      allocated_coverage_ratio=allocated_coverage_ratio,
      funded_vessels=funded_vessels,
      funded_by_type=funded_by_type,
      allocated_grant_tl=allocated,
      remaining_budget_tl=remaining,
      unlocked_investment_tl=unlocked_investment,
      required_owner_equity_tl=owner_equity,
  )
