"""Registry boundary for complete normative hydrostatic profiles.

V1, V2, and V3 are intentionally not instantiated yet. Their required BWL, C_P,
LCB, hull-form, transom, and related hydrostatic inputs do not exist in the
repository. An empty registry is safer and more type-safe than fake defaults or
partially valid engineering objects.
"""

from types import MappingProxyType


PENDING_NORMATIVE_HYDROSTATIC_PROFILE_IDS = ("v1", "v2", "v3")
NORMATIVE_HYDROSTATIC_PROFILES = MappingProxyType({})
