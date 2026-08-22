"""Solar-resource assumptions for the v0.2 seasonal energy model."""

PVGIS_API_VERSION = "5_3"
PVGIS_PV_TECH_CHOICE = "crystSi2025"
PVGIS_SYSTEM_LOSS_PERCENT = 14.0

# Boat hardtop modules are treated as essentially horizontal.
PVGIS_PANEL_ANGLE_DEGREES = 0.0
PVGIS_PANEL_ASPECT_DEGREES = 0.0

# Conservative modern high-efficiency module-level power density.
# 0.24 kWp/m² corresponds to 240 Wp/m².
SOLAR_MODULE_POWER_DENSITY_KWP_PER_M2 = 0.24

DEFAULT_LOCATION_NAME = "Dalyan, Muğla"
DEFAULT_LATITUDE = 36.8350
DEFAULT_LONGITUDE = 28.6424
