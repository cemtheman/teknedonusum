"""Controlled Streamlit presentation for v0.2 normative sizing results."""

import streamlit as st

from calculations.normative_decision_summary import (
    build_normative_decision_summary,
)
from calculations.normative_sizing import calculate_normative_sizing
from models.normative_decision_summary import NormativeDecisionSummary
from ui.formatting import format_integer_tr


SPEED_MIN_KNOTS = 6.0
SPEED_MAX_KNOTS = 10.0

LIMITATION_LABELS = {
    "market_envelope_power_sizing": (
        "Güç boyutlandırması piyasa referans bandına dayanır."
    ),
    "not_manufacturer_certified": "Üretici sertifikalı performans verisi değildir.",
    "not_sea_trial_validated": "Deniz deneyi ile doğrulanmamıştır.",
    "propulsion_energy_only": "Enerji hesabı yalnız elektrikli tahrik yükünü kapsar.",
    "auxiliary_and_hotel_loads_excluded": "Yardımcı ve hotel yükleri dahil değildir.",
    "defined_motor_and_battery_cost_baseline_only": (
        "Maliyet kapsamı tanımlı motor ve batarya baseline'ı ile sınırlıdır."
    ),
    "solar_and_charging_infrastructure_excluded": (
        "Güneş sistemi ve şarj altyapısı maliyete dahil değildir."
    ),
}


def build_vessel_selection_map(vessel_specs):
  """Map existing user-facing V1/V2/V3 names to internal vessel IDs."""
  labels = {}
  for vessel_id in ("v1", "v2", "v3"):
    if vessel_id not in vessel_specs or not vessel_specs[vessel_id].get("name"):
      raise ValueError("V1/V2/V3 tekne tanımları mevcut değil.")
    label = vessel_specs[vessel_id]["name"].split(" (", 1)[0]
    if label in labels:
      raise ValueError("Tekne seçim etiketleri benzersiz olmalıdır.")
    labels[label] = vessel_id
  return labels


def build_normative_ui_summary(vessel_id, selected_speed_knots):
  """Build the decision summary through the public normative APIs."""
  if not SPEED_MIN_KNOTS <= selected_speed_knots <= SPEED_MAX_KNOTS:
    raise ValueError("Hizmet hızı normatif 6–10 knot aralığında olmalıdır.")
  sizing = calculate_normative_sizing(vessel_id, selected_speed_knots)
  return build_normative_decision_summary(sizing)


def build_primary_display_values(summary):
  """Format decision values without changing their underlying raw numbers."""
  if not isinstance(summary, NormativeDecisionSummary):
    raise TypeError("summary must be a NormativeDecisionSummary")
  return {
      "vessel": summary.vessel_type,
      "speed": f"{summary.selected_speed_knots:.1f} knot",
      "mechanical_reference": (
          f"{summary.reference_estimate_installed_mechanical_power_kw:.1f} kW"
      ),
      "mechanical_envelope": (
          f"{summary.min_envelope_installed_mechanical_power_kw:.1f}–"
          f"{summary.max_envelope_installed_mechanical_power_kw:.1f} kW"
      ),
      "energy_reference": (
          f"{summary.reference_estimate_daily_propulsion_energy_kwh:.1f} "
          "kWh/gün"
      ),
      "energy_envelope": (
          f"{summary.min_envelope_daily_propulsion_energy_kwh:.1f}–"
          f"{summary.max_envelope_daily_propulsion_energy_kwh:.1f} kWh/gün"
      ),
      "battery_reference": (
          f"{summary.reference_estimate_nominal_battery_capacity_kwh:.1f} kWh"
      ),
      "battery_envelope": (
          f"{summary.min_envelope_nominal_battery_capacity_kwh:.1f}–"
          f"{summary.max_envelope_nominal_battery_capacity_kwh:.1f} kWh"
      ),
      "cost_reference": (
          f"€{format_integer_tr(summary.reference_estimate_propulsion_system_cost)}"
      ),
      "cost_envelope": (
          f"€{format_integer_tr(summary.min_envelope_propulsion_system_cost)}–"
          f"€{format_integer_tr(summary.max_envelope_propulsion_system_cost)}"
      ),
  }


def render_normative_sizing_section(vessel_specs, selected_speed_knots):
  """Render a separate v0.2 section while preserving the legacy UI path."""
  st.divider()
  st.subheader("⚡ Elektrikli Tahrik Ön Boyutlandırması")
  st.caption(
      "Bu sonuçlar normatif piyasa referanslarına dayalı ön boyutlandırma "
      "tahminidir; nihai tasarım veya sertifikasyon sonucu değildir."
  )

  try:
    selection_map = build_vessel_selection_map(vessel_specs)
  except (TypeError, ValueError):
    st.error("Normatif tekne seçenekleri hazırlanamadı.")
    return None

  selected_label = st.selectbox(
      "Ön boyutlandırma tekne tipi",
      tuple(selection_map),
  )
  vessel_id = selection_map.get(selected_label)
  try:
    summary = build_normative_ui_summary(vessel_id, selected_speed_knots)
  except (TypeError, ValueError):
    st.error(
        "Normatif ön boyutlandırma hesaplanamadı. Hizmet hızı 6–10 knot "
        "aralığında olmalıdır."
    )
    return None

  values = build_primary_display_values(summary)
  st.write(f"Seçilen tekne: {values['vessel']} · Hizmet hızı: {values['speed']}")
  columns = st.columns(4)
  columns[0].metric(
      "Toplam kurulu mekanik güç",
      values["mechanical_reference"],
  )
  columns[0].caption(f"Ön zarf: {values['mechanical_envelope']}")
  columns[1].metric(
      "Günlük tahrik enerjisi",
      values["energy_reference"],
  )
  columns[1].caption(f"Ön zarf: {values['energy_envelope']}")
  columns[2].metric(
      "Nominal batarya kapasitesi",
      values["battery_reference"],
  )
  columns[2].caption(f"Ön zarf: {values['battery_envelope']}")
  columns[3].metric(
      "Motor + batarya maliyeti",
      values["cost_reference"],
  )
  columns[3].caption(f"Ön zarf: {values['cost_envelope']}")

  assumptions = summary.assumptions
  with st.expander("Varsayımlar ve metodoloji detayları", expanded=False):
    st.write(
        f"Reference electrical input: "
        f"{summary.reference_electrical_input_power_kw:.1f} kW"
    )
    st.write(
        f"Motor verimi: %{assumptions.motor_efficiency * 100:.0f} · "
        f"Operasyon: {assumptions.operating_hours_per_day:.1f} saat/gün · "
        f"Duty cycle: %{assumptions.duty_cycle * 100:.0f} · "
        f"Etkin güç çekişi: "
        f"{assumptions.effective_powered_hours_per_day:.1f} saat/gün"
    )
    st.write(
        f"Kullanılabilir enerji: %{assumptions.usable_energy_fraction * 100:.0f} · "
        f"Reserve: %{assumptions.reserve_fraction * 100:.0f} · "
        f"Motor baseline: "
        f"€{assumptions.motor_unit_cost_per_total_installed_kw:.0f}/kW · "
        f"Batarya baseline: "
        f"€{assumptions.battery_unit_cost_per_nominal_kwh:.0f}/kWh"
    )
    for limitation_id in summary.limitation_ids:
      st.write(f"- {LIMITATION_LABELS[limitation_id]}")

  return summary
