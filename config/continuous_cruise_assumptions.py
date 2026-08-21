from dataclasses import dataclass


@dataclass(frozen=True)
class ContinuousCruiseCalibration:
  waterline_length_m: float
  wetted_surface_area_m2: float
  form_factor: float
  min_residual_resistance_n: float
  reference_residual_resistance_n: float
  max_residual_resistance_n: float
  appendage_resistance_n: float
  propulsive_efficiency: float
  motor_efficiency: float
  source_status: str


V1_CONTINUOUS_CRUISE_CALIBRATION = ContinuousCruiseCalibration(
    waterline_length_m=11.4,
    wetted_surface_area_m2=30.0,
    form_factor=0.15,
    min_residual_resistance_n=500.0,
    reference_residual_resistance_n=800.0,
    max_residual_resistance_n=1000.0,
    appendage_resistance_n=100.0,
    propulsive_efficiency=0.60,
    motor_efficiency=0.95,
    source_status="provisional field-calibration band",
)


# V2/V3 are deliberately derived from the V1 provisional low-speed calibration,
# rather than from the legacy V^2.85 speed-power law.
#
# Geometry basis:
# - LWL ~= 0.95 * LOA
# - wetted surface and appendage resistance scale with displacement^(2/3)
# - residual band uses the same displacement scale with an explicit 0.75
#   slender-catamaran factor. This factor remains provisional and must be
#   replaced when catamaran-specific resistance data / sea-trial data exist.
#
# These are transparent engineering assumptions, not certified predictions.

V2_CONTINUOUS_CRUISE_CALIBRATION = ContinuousCruiseCalibration(
    waterline_length_m=12.825,       # 0.95 * 13.5 m
    wetted_surface_area_m2=33.88,    # 30 * (7.8 / 6.5)^(2/3)
    form_factor=0.10,
    min_residual_resistance_n=425.0,
    reference_residual_resistance_n=675.0,
    max_residual_resistance_n=850.0,
    appendage_resistance_n=115.0,
    propulsive_efficiency=0.60,
    motor_efficiency=0.95,
    source_status=(
        "provisional V1-scaled narrow-catamaran calibration; "
        "displacement^(2/3) scaling with 0.75 residual factor"
    ),
)

V3_CONTINUOUS_CRUISE_CALIBRATION = ContinuousCruiseCalibration(
    waterline_length_m=13.30,        # 0.95 * 14.0 m
    wetted_surface_area_m2=38.64,    # 30 * (9.5 / 6.5)^(2/3)
    form_factor=0.10,
    min_residual_resistance_n=500.0,
    reference_residual_resistance_n=775.0,
    max_residual_resistance_n=975.0,
    appendage_resistance_n=130.0,
    propulsive_efficiency=0.60,
    motor_efficiency=0.95,
    source_status=(
        "provisional V1-scaled narrow-catamaran calibration; "
        "displacement^(2/3) scaling with 0.75 residual factor"
    ),
)

CONTINUOUS_CRUISE_CALIBRATIONS = {
    "v1": V1_CONTINUOUS_CRUISE_CALIBRATION,
    "v2": V2_CONTINUOUS_CRUISE_CALIBRATION,
    "v3": V3_CONTINUOUS_CRUISE_CALIBRATION,
}
