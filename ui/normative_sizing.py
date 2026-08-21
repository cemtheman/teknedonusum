"""Streamlit presentation for the primary electric-propulsion sizing result."""

import streamlit as st

from calculations.normative_decision_summary import (
    build_normative_decision_summary,
)
from calculations.normative_sizing import calculate_normative_sizing
from calculations.taxation import calculate_turnkey_tax_breakdown
from config.tax_assumptions import (
    SPECIAL_CONSUMPTION_TAX_RATE,
    VALUE_ADDED_TAX_RATE,
)
from config.operational_speed import (
    MAX_OPERATION_SPEED_KNOTS as SPEED_MAX_KNOTS,
    MIN_OPERATION_SPEED_KNOTS as SPEED_MIN_KNOTS,
)
from config.operational_methodology import cruise_methodology_label_tr
from models.normative_decision_summary import NormativeDecisionSummary
from ui.formatting import format_integer_tr


VESSEL_LABELS = {
    "v1": "Tip 1 — 12 m Tek Gövdeli",
    "v2": "Tip 2 — 13,5 m Katamaran",
    "v3": "Tip 3 — 14 m Katamaran",
}

LIMITATION_LABELS = {
    "market_envelope_power_sizing": (
        "Kurulu motor gücü, piyasa/normatif referans aralığına dayalıdır."
    ),
    "not_manufacturer_certified": "Üretici sertifikalı performans verisi değildir.",
    "not_sea_trial_validated": "Deniz deneyi ile doğrulanmamıştır.",
    "propulsion_energy_only": "Enerji hesabı yalnız elektrikli tahrik yükünü kapsar.",
    "auxiliary_and_hotel_loads_excluded": (
        "Yardımcı elektrik yükleri enerji hesabına dahil değildir."
    ),
}


def build_vessel_selection_map(vessel_specs):
  labels = {}
  for vessel_id in ("v1", "v2", "v3"):
    if vessel_id not in vessel_specs:
      raise ValueError("Tip 1/2/3 tekne tanımları mevcut değil.")
    labels[VESSEL_LABELS[vessel_id]] = vessel_id
  return labels


def build_normative_ui_summary(
    vessel_id,
    selected_speed_knots,
    daily_distance_nm=35.0,
):
  if not SPEED_MIN_KNOTS <= selected_speed_knots <= SPEED_MAX_KNOTS:
    raise ValueError("Hizmet hızı 5–10 knot aralığında olmalıdır.")
  sizing = calculate_normative_sizing(
      vessel_id,
      selected_speed_knots,
      daily_distance_nm,
  )
  return build_normative_decision_summary(sizing)


def _format_decimal_tr(value):
  return f"{value:.1f}".replace(".", ",")


def build_primary_display_values(summary, turnkey_cost_eur):
  if not isinstance(summary, NormativeDecisionSummary):
    raise TypeError("summary must be a NormativeDecisionSummary")

  tax = calculate_turnkey_tax_breakdown(float(turnkey_cost_eur))
  return {
      "speed": f"{_format_decimal_tr(summary.selected_speed_knots)} kn",
      "mechanical_reference": (
          f"{_format_decimal_tr(summary.reference_estimate_installed_mechanical_power_kw)} kW"
      ),
      "mechanical_envelope": (
          f"{_format_decimal_tr(summary.min_envelope_installed_mechanical_power_kw)}–"
          f"{_format_decimal_tr(summary.max_envelope_installed_mechanical_power_kw)} kW"
      ),
      "energy_reference": (
          f"{_format_decimal_tr(summary.reference_estimate_daily_propulsion_energy_kwh)} "
          "kWh/gün"
      ),
      "energy_envelope": (
          f"{_format_decimal_tr(summary.min_envelope_daily_propulsion_energy_kwh)}–"
          f"{_format_decimal_tr(summary.max_envelope_daily_propulsion_energy_kwh)} kWh/gün"
      ),
      "battery_reference": (
          f"{_format_decimal_tr(summary.reference_estimate_nominal_battery_capacity_kwh)} "
          "kWh"
      ),
      "battery_envelope": (
          f"{_format_decimal_tr(summary.min_envelope_nominal_battery_capacity_kwh)}–"
          f"{_format_decimal_tr(summary.max_envelope_nominal_battery_capacity_kwh)} kWh"
      ),
      "turnkey_cost": f"€{format_integer_tr(turnkey_cost_eur)}",
      "tax_inclusive_cost": f"€{format_integer_tr(tax.gross_price_eur)}",
  }


def render_normative_sizing_section(
    vessel_specs,
    selected_speed_knots,
    daily_distance_nm=35.0,
):
  st.divider()
  st.subheader("⚡ Elektrikli Tahrik Ön Boyutlandırması")
  st.caption(
      "Seçilen tekne tipi, hizmet hızı ve günlük rota için ön boyutlandırma "
      "sonuçlarıdır; nihai tasarım veya sertifikasyon sonucu değildir."
  )

  try:
    selection_map = build_vessel_selection_map(vessel_specs)
  except (TypeError, ValueError):
    st.error("Tekne seçenekleri hazırlanamadı.")
    return None

  selected_label = st.selectbox("Tekne tipi", tuple(selection_map))
  vessel_id = selection_map.get(selected_label)

  try:
    summary = build_normative_ui_summary(
        vessel_id,
        selected_speed_knots,
        daily_distance_nm,
    )
  except (TypeError, ValueError):
    st.error(
        "Ön boyutlandırma hesaplanamadı. Hizmet hızı 5–10 knot aralığında "
        "olmalıdır."
    )
    return None

  turnkey_cost_eur = vessel_specs[vessel_id]["totalCostEur"]
  values = build_primary_display_values(summary, turnkey_cost_eur)

  st.write(
      f"{selected_label} · {values['speed']} hizmet hızı · "
      f"{_format_decimal_tr(daily_distance_nm)} deniz mili/gün"
  )
  st.caption(
      "Seyir/enerji hesap yöntemi: "
      f"{cruise_methodology_label_tr(summary.selected_speed_knots)}."
  )

  columns = st.columns(4)
  columns[0].metric("Toplam kurulu motor gücü", values["mechanical_reference"])
  columns[0].caption(
      f"Ön değerlendirme aralığı: {values['mechanical_envelope']}"
  )

  columns[1].metric("Günlük tahrik enerjisi", values["energy_reference"])
  columns[1].caption(
      f"Ön değerlendirme aralığı: {values['energy_envelope']}"
  )

  columns[2].metric("Gerekli nominal batarya", values["battery_reference"])
  columns[2].caption(
      f"Ön değerlendirme aralığı: {values['battery_envelope']}"
  )

  columns[3].metric("Anahtar teslim piyasa bedeli", values["turnkey_cost"])
  columns[3].caption(
      f"%8 ÖTV ve %20 KDV hariç · vergiler dahil yaklaşık "
      f"{values['tax_inclusive_cost']}"
  )

  assumptions = summary.assumptions
  with st.expander("Hesap ayrıntıları", expanded=False):
    st.write(
        "Seyir elektrik gücü: "
        f"{_format_decimal_tr(summary.reference_electrical_input_power_kw)} kW"
    )
    st.write(
        f"Günlük rota: {_format_decimal_tr(daily_distance_nm)} deniz mili · "
        f"Tahmini seyir süresi: "
        f"{_format_decimal_tr(assumptions.operating_hours_per_day)} saat/gün"
    )
    st.write(
        f"Motor verimi: %{assumptions.motor_efficiency * 100:.0f} · "
        f"Kullanılabilir batarya oranı: "
        f"%{assumptions.usable_energy_fraction * 100:.0f} · "
        f"Enerji rezervi: %{assumptions.reserve_fraction * 100:.0f}"
    )
    st.write(
        f"Vergi varsayımı: ÖTV %{SPECIAL_CONSUMPTION_TAX_RATE * 100:.0f} · "
        f"KDV %{VALUE_ADDED_TAX_RATE * 100:.0f}"
    )
    for limitation_id in (
        "market_envelope_power_sizing",
        "not_manufacturer_certified",
        "not_sea_trial_validated",
        "propulsion_energy_only",
        "auxiliary_and_hotel_loads_excluded",
    ):
      if limitation_id in summary.limitation_ids:
        st.write(f"- {LIMITATION_LABELS[limitation_id]}")

  return summary
