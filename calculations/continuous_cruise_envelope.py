from calculations.continuous_cruise import calculate_continuous_cruise_power
from config.continuous_cruise_assumptions import CONTINUOUS_CRUISE_CALIBRATIONS


def calculate_continuous_cruise_envelope(vessel_id, speed_knots):
  speed_knots = float(speed_knots)
  if vessel_id not in CONTINUOUS_CRUISE_CALIBRATIONS:
    raise ValueError("vessel_id must be one of v1, v2, or v3")
  if not 5.0 <= speed_knots <= 6.0:
    raise ValueError(
        "continuous-cruise calibration is valid only from 5 to 6 knots"
    )

  c = CONTINUOUS_CRUISE_CALIBRATIONS[vessel_id]
  residuals = (
      c.min_residual_resistance_n,
      c.reference_residual_resistance_n,
      c.max_residual_resistance_n,
  )
  return tuple(
      calculate_continuous_cruise_power(
          speed_knots=speed_knots,
          waterline_length_m=c.waterline_length_m,
          wetted_surface_area_m2=c.wetted_surface_area_m2,
          form_factor=c.form_factor,
          residual_resistance_n=residual,
          appendage_resistance_n=c.appendage_resistance_n,
          propulsive_efficiency=c.propulsive_efficiency,
          motor_efficiency=c.motor_efficiency,
      )
      for residual in residuals
  )


def calculate_v1_continuous_cruise_envelope(speed_knots):
  """Backward-compatible V1 wrapper."""
  return calculate_continuous_cruise_envelope("v1", speed_knots)
