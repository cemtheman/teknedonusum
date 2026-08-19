from copy import deepcopy

from config.vessels import BASE_VESSEL_SPECS


def build_vessel_specs(cost_eur_v1, cost_eur_v2, cost_eur_v3, eur_rate):
  vessel_specs = deepcopy(BASE_VESSEL_SPECS)
  costs_eur = {
      "v1": cost_eur_v1,
      "v2": cost_eur_v2,
      "v3": cost_eur_v3,
      "v4_24": cost_eur_v1,
      "v4_32": cost_eur_v2,
  }

  for vessel_key, base_spec in vessel_specs.items():
    cost_eur = costs_eur[vessel_key]
    spec = {}
    for field, value in base_spec.items():
      spec[field] = value
      if field == "C":
        spec["totalCostEur"] = cost_eur
        spec["totalCost"] = int(cost_eur * eur_rate)
      elif field == "grantRate":
        spec["maxGrant"] = int(cost_eur * eur_rate * value)
    vessel_specs[vessel_key] = spec

  return vessel_specs
