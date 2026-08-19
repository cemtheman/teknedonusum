"""Preliminary vessel geometry assumptions for future engineering studies.

This dataset contains preliminary engineering assumptions. PROJECT_CONFIG marks
only dimensions already present in the current project configuration; it does not
mean verified naval-architecture data. PRELIMINARY_ASSUMPTION values must be
replaced when actual GA plans, hydrostatic particulars, designer data, or model/CFD
results become available. This dataset is not yet used directly for production
power prediction.
"""

from models.geometry import (
    GeometryDataSource,
    GeometryValue,
    PreliminaryVesselGeometry,
)


PRELIMINARY_VESSEL_GEOMETRY = {
    "v1": PreliminaryVesselGeometry(
        loa_m=GeometryValue(12.0, GeometryDataSource.PROJECT_CONFIG),
        lwl_m=GeometryValue(11.4, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        beam_m=GeometryValue(3.8, GeometryDataSource.PROJECT_CONFIG),
        draft_m=GeometryValue(0.65, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        displacement_t=GeometryValue(
            9.22,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        wetted_surface_area_m2=GeometryValue(
            30.0,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        demi_hull_beam_m=None,
        hull_centerline_spacing_m=None,
    ),
    "v2": PreliminaryVesselGeometry(
        loa_m=GeometryValue(13.5, GeometryDataSource.PROJECT_CONFIG),
        lwl_m=GeometryValue(12.8, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        beam_m=GeometryValue(4.2, GeometryDataSource.PROJECT_CONFIG),
        draft_m=GeometryValue(0.60, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        displacement_t=GeometryValue(
            11.36,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        wetted_surface_area_m2=GeometryValue(
            34.0,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        demi_hull_beam_m=GeometryValue(
            1.15,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        hull_centerline_spacing_m=GeometryValue(
            3.05,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
    ),
    "v3": PreliminaryVesselGeometry(
        loa_m=GeometryValue(14.0, GeometryDataSource.PROJECT_CONFIG),
        lwl_m=GeometryValue(13.3, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        beam_m=GeometryValue(4.5, GeometryDataSource.PROJECT_CONFIG),
        draft_m=GeometryValue(0.70, GeometryDataSource.PRELIMINARY_ASSUMPTION),
        displacement_t=GeometryValue(
            15.22,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        wetted_surface_area_m2=GeometryValue(
            40.0,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        demi_hull_beam_m=GeometryValue(
            1.25,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
        hull_centerline_spacing_m=GeometryValue(
            3.25,
            GeometryDataSource.PRELIMINARY_ASSUMPTION,
        ),
    ),
}
