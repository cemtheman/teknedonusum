"""Management-facing assumptions and data-source transparency model."""

from dataclasses import dataclass

from calculations.wetted_surface import check_wetted_surface_sanity
from config.commission_constraints import DALYAN_COMMISSION_CONSTRAINTS
from config.geometry import PRELIMINARY_VESSEL_GEOMETRY
from config.preliminary_scenario import V1_PRELIMINARY_SCENARIO_ASSUMPTIONS


USER_INPUT = "Kullanıcı girdisi"
LIVE_MARKET_DATA = "Canlı piyasa verisi — canlı"
FALLBACK_MARKET_DATA = "Canlı piyasa verisi — statik yedek"
COMMISSION_CRITERION = "Teknik Komisyon kriteri"
ENGINEERING_ASSUMPTION = "Ön mühendislik varsayımı"
CALIBRATED_ESTIMATE = "Kalibre ön tahmin"
CALCULATED_RESULT = "Hesaplanan sonuç"


@dataclass(frozen=True)
class AssumptionSourceRow:
  parameter: str
  current_value: str
  source_type: str
  description: str


def _decimal(value, unit=""):
  formatted = f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")
  return f"{formatted} {unit}".strip()


def build_assumptions_transparency(
    inputs,
    vessel_specs,
    eur_is_live: bool,
    diesel_is_live: bool,
) -> tuple[AssumptionSourceRow, ...]:
  """Describe key current values without changing their calculation paths."""
  constraints = DALYAN_COMMISSION_CONSTRAINTS
  assumptions = V1_PRELIMINARY_SCENARIO_ASSUMPTIONS
  v1_geometry = PRELIMINARY_VESSEL_GEOMETRY["v1"]
  wetted_surface = check_wetted_surface_sanity(v1_geometry)

  return (
      AssumptionSourceRow(
          "Seyir hızı",
          _decimal(inputs.cruise_speed, "knot"),
          USER_INPUT,
          "Sidebar'da seçilen operasyon senaryosu hızı.",
      ),
      AssumptionSourceRow(
          "Günlük rota mesafesi",
          _decimal(inputs.daily_miles, "NM/gün"),
          USER_INPUT,
          "Sidebar'da seçilen günlük operasyon mesafesi.",
      ),
      AssumptionSourceRow(
          "Güneşlenme süresi",
          _decimal(inputs.sun_hours, "saat/gün"),
          USER_INPUT,
          "Sidebar'da seçilen günlük güneş girdisi.",
      ),
      AssumptionSourceRow(
          "EUR/TRY kuru",
          _decimal(inputs.eur_rate, "TL/EUR"),
          LIVE_MARKET_DATA if eur_is_live else FALLBACK_MARKET_DATA,
          "TCMB erişilemezse statik yedek değer kullanılır.",
      ),
      AssumptionSourceRow(
          "Dizel fiyatı",
          _decimal(inputs.diesel_price, "TL/L"),
          LIVE_MARKET_DATA if diesel_is_live else FALLBACK_MARKET_DATA,
          "Piyasa servisi erişilemezse statik yedek değer kullanılır.",
      ),
      AssumptionSourceRow(
          "Elektrik fiyatı",
          _decimal(inputs.elec_price, "TL/kWh"),
          USER_INPUT,
          "Sidebar'da seçilen liman şebeke elektrik fiyatı.",
      ),
      AssumptionSourceRow(
          "Tekne maliyetleri (v1 / v2 / v3)",
          " / ".join(
              f"€{vessel_specs[key]['totalCostEur']:,.0f}"
              for key in ("v1", "v2", "v3")
          ),
          USER_INPUT,
          "Sidebar maliyet girdilerinden ve güncel EUR/TRY kurundan türetilir.",
      ),
      AssumptionSourceRow(
          "Batarya kapasiteleri (v1 / v2 / v3)",
          " / ".join(
              _decimal(vessel_specs[key]["batCapacity"], "kWh")
              for key in ("v1", "v2", "v3")
          ),
          CALIBRATED_ESTIMATE,
          "Mevcut tekne konfigürasyonundaki kalibre ön değerler.",
      ),
      AssumptionSourceRow(
          "Komisyon hız kriteri",
          _decimal(constraints.minimum_required_speed_knots, "knot"),
          COMMISSION_CRITERION,
          "Operasyon seyir hızından ayrı, gerekli tekne hız kabiliyeti; henüz "
          "değerlendirilmemiştir.",
      ),
      AssumptionSourceRow(
          "Komisyon asgari menzili",
          _decimal(constraints.minimum_navigation_range_nm, "NM"),
          COMMISSION_CRITERION,
          "Mühendislik varsayımı değil, ayrı uygunluk eşiği.",
      ),
      AssumptionSourceRow(
          "Komisyon motor verimi eşiği",
          _decimal(constraints.minimum_motor_efficiency * 100, "%"),
          COMMISSION_CRITERION,
          "Teknik uygunluk için minimum verim kriteri.",
      ),
      AssumptionSourceRow(
          "Form faktörü",
          _decimal(assumptions.form_factor),
          ENGINEERING_ASSUMPTION,
          "v1 direnç duyarlılığı için doğrulanmamış ön varsayım.",
      ),
      AssumptionSourceRow(
          "Artık direnç",
          _decimal(assumptions.residual_resistance_n, "N"),
          ENGINEERING_ASSUMPTION,
          "v1 senaryosuna dışarıdan verilen ön direnç girdisi.",
      ),
      AssumptionSourceRow(
          "Eklenti direnci",
          _decimal(assumptions.appendage_resistance_n, "N"),
          ENGINEERING_ASSUMPTION,
          "v1 senaryosuna dışarıdan verilen ön direnç girdisi.",
      ),
      AssumptionSourceRow(
          "Sevk verimi",
          _decimal(assumptions.propulsive_efficiency * 100, "%"),
          ENGINEERING_ASSUMPTION,
          "Pervane tasarımı veya doğrulanmış sevk eşleştirmesi değildir.",
      ),
      AssumptionSourceRow(
          "Kullanılabilir batarya payı",
          _decimal(assumptions.usable_energy_fraction * 100, "%"),
          ENGINEERING_ASSUMPTION,
          "Nominal bataryanın normalde kullanılabilir kabul edilen bölümü.",
      ),
      AssumptionSourceRow(
          "Operasyon rezervi",
          _decimal(assumptions.operational_reserve_fraction * 100, "%"),
          ENGINEERING_ASSUMPTION,
          "Kullanılabilir enerjiden görev için harcanmayan rezerv.",
      ),
      AssumptionSourceRow(
          "Otel yükü",
          _decimal(assumptions.hotel_load_kw, "kW"),
          ENGINEERING_ASSUMPTION,
          "v1 yardımcı elektrik yükü için ön varsayım.",
      ),
      AssumptionSourceRow(
          "Güneş paneli verimi",
          _decimal(assumptions.panel_efficiency * 100, "%"),
          ENGINEERING_ASSUMPTION,
          "Doğrulanmış üretici panel seçimi değildir.",
      ),
      AssumptionSourceRow(
          "Güneş sistemi derating faktörü",
          _decimal(assumptions.solar_derating_factor),
          ENGINEERING_ASSUMPTION,
          "Toplam PV sistem kayıpları için ön varsayım.",
      ),
      AssumptionSourceRow(
          "Kullanılan ıslak yüzey alanı (v1)",
          _decimal(wetted_surface.assumed_wetted_surface_area_m2, "m²"),
          ENGINEERING_ASSUMPTION,
          "Direnç hesabında kullanılan varsayım; hidrostatik veri değildir.",
      ),
      AssumptionSourceRow(
          "Islak yüzey sanity tahmini (v1)",
          _decimal(wetted_surface.estimated_wetted_surface_area_m2, "m²"),
          CALCULATED_RESULT,
          "Yalnız geometri çapraz kontrolüdür; direnç hesabına girmez.",
      ),
  )
