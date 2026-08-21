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
