"""Preliminary engineering inputs for the v1 technical reference scenario.

These values are preliminary engineering scenario assumptions. They are not a
verified vessel design and are not Technical Commission criteria. They will be
replaced when actual GA, hydrostatics, resistance, propeller, and PV data become
available.

The ``motor_efficiency`` value of 0.95 numerically matches the commission minimum
threshold, but here it is a preliminary scenario input. The commission threshold
is sourced separately from ``config/commission_constraints.py``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreliminaryScenarioAssumptions:
  form_factor: float
  residual_resistance_n: float
  appendage_resistance_n: float
  propulsive_efficiency: float
  motor_efficiency: float
  design_margin_fraction: float
  usable_energy_fraction: float
  operational_reserve_fraction: float
  hotel_load_kw: float
  roof_length_fraction_of_loa: float
  usable_roof_width_m: float
  panel_coverage_fraction: float
  panel_efficiency: float
  peak_sun_hours: float
  solar_derating_factor: float

  def __post_init__(self):
    if not self.form_factor >= 0:
      raise ValueError("form_factor must be non-negative")
    if not self.residual_resistance_n >= 0:
      raise ValueError("residual_resistance_n must be non-negative")
    if not self.appendage_resistance_n >= 0:
      raise ValueError("appendage_resistance_n must be non-negative")
    if not 0 < self.propulsive_efficiency <= 1:
      raise ValueError(
          "propulsive_efficiency must be greater than zero and at most one"
      )
    if not 0 < self.motor_efficiency <= 1:
      raise ValueError("motor_efficiency must be greater than zero and at most one")
    if not self.design_margin_fraction >= 0:
      raise ValueError("design_margin_fraction must be non-negative")
    if not 0 < self.usable_energy_fraction <= 1:
      raise ValueError(
          "usable_energy_fraction must be greater than zero and at most one"
      )
    if not 0 <= self.operational_reserve_fraction < 1:
      raise ValueError(
          "operational_reserve_fraction must be non-negative and less than one"
      )
    if not self.hotel_load_kw >= 0:
      raise ValueError("hotel_load_kw must be non-negative")
    if not 0 < self.roof_length_fraction_of_loa <= 1:
      raise ValueError(
          "roof_length_fraction_of_loa must be greater than zero and at most one"
      )
    if not self.usable_roof_width_m > 0:
      raise ValueError("usable_roof_width_m must be positive")
    if not 0 < self.panel_coverage_fraction <= 1:
      raise ValueError(
          "panel_coverage_fraction must be greater than zero and at most one"
      )
    if not 0 < self.panel_efficiency <= 1:
      raise ValueError("panel_efficiency must be greater than zero and at most one")
    if not self.peak_sun_hours >= 0:
      raise ValueError("peak_sun_hours must be non-negative")
    if not 0 < self.solar_derating_factor <= 1:
      raise ValueError(
          "solar_derating_factor must be greater than zero and at most one"
      )


V1_PRELIMINARY_SCENARIO_ASSUMPTIONS = PreliminaryScenarioAssumptions(
    form_factor=0.15,
    residual_resistance_n=1500.0,
    appendage_resistance_n=100.0,
    propulsive_efficiency=0.60,
    motor_efficiency=0.95,
    design_margin_fraction=0.15,
    usable_energy_fraction=0.90,
    operational_reserve_fraction=0.20,
    hotel_load_kw=1.5,
    roof_length_fraction_of_loa=0.80,
    usable_roof_width_m=3.0,
    panel_coverage_fraction=0.85,
    panel_efficiency=0.22,
    peak_sun_hours=5.5,
    solar_derating_factor=0.85,
)
