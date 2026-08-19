import streamlit as st

from models.compliance import ComplianceStatus
from models.presentation import TechnicalScenarioPresentation


def _format_primary_value(value):
  if value.unit == "kW":
    return f"{value.value:.1f} kW"
  if value.unit == "NM":
    return f"{value.value:.1f} NM"
  if value.unit == "kWh/day":
    return f"{value.value:.1f} kWh/gün"
  return str(value.value)


def _format_compliance_actual(value):
  if value.criterion == "loa":
    return f"{value.actual_value:.1f} m"
  if value.criterion == "passenger_capacity":
    return f"{int(value.actual_value)}"
  if value.criterion == "minimum_speed":
    return f"{value.actual_value:.1f} knot"
  if value.criterion == "minimum_navigation_range":
    return f"{value.actual_value:.1f} NM"
  if value.criterion == "motor_efficiency":
    return f"{value.actual_value * 100:.1f}%"
  if value.criterion == "battery_capacity":
    return f"{value.actual_value:.1f} kWh"
  if value.criterion == "roof_length_fraction":
    return f"{value.actual_value * 100:.1f}% LOA"
  return str(value.actual_value)


def _format_detail_value(value):
  if value.key == "effective_power":
    return f"{value.value:.2f} kW"
  if value.key == "motor_output_power":
    return f"{value.value:.2f} kW"
  if value.key == "energy_per_nm":
    return f"{value.value:.2f} kWh/NM"
  if value.key == "solar_coverage":
    return f"{value.value * 100:.1f}%"
  if value.key == "excess_solar_energy":
    return f"{value.value:.2f} kWh/gün"
  return str(value.value)


def render_technical_scenario(
    presentation: TechnicalScenarioPresentation,
) -> None:
  if not isinstance(presentation, TechnicalScenarioPresentation):
    raise TypeError("presentation must be a TechnicalScenarioPresentation")

  st.divider()
  st.subheader("⚙️ Ön Teknik Uygunluk ve Enerji Analizi")
  st.caption(
      "Bu bölüm, ön tasarım varsayımlarıyla hesaplanan teknik sonuçları "
      "ve Teknik Komisyon kriterlerine göre uygunluk durumunu gösterir."
  )

  if presentation.overall_status is ComplianceStatus.PASS:
    st.success("Teknik Komisyon kriterleri: UYGUN")
  else:
    st.error("Teknik Komisyon kriterleri: UYGUN DEĞİL")

  primary_columns = st.columns(5)
  for column, value in zip(primary_columns, presentation.primary_values):
    with column:
      st.metric(value.label, _format_primary_value(value))

  st.caption(
      "⚠️ Güç, menzil, güneş üretimi ve enerji sonuçları "
      "ön tasarım tahminleridir; doğrulanmış nihai tekne performansı değildir."
  )

  st.markdown("#### Teknik Komisyon Kriterleri")
  for value in presentation.compliance_values:
    icon = "✅" if value.status is ComplianceStatus.PASS else "❌"
    actual = _format_compliance_actual(value)
    st.markdown(
        f"{icon} {value.label}: {actual} — Gereken: {value.required_value}"
    )

  with st.expander("Teknik Hesap Detayları", expanded=False):
    detail_columns = st.columns(2)
    detail_value_columns = (
        detail_columns[0],
        detail_columns[1],
        detail_columns[0],
        detail_columns[1],
        detail_columns[0],
    )
    for column, value in zip(detail_value_columns, presentation.detail_values):
      with column:
        st.metric(value.label, _format_detail_value(value))
    st.caption(
        "Effective power gövde direncini yenmek için gereken güçtür. "
        "Installed motor power ise propulsif verim ve tasarım marjı "
        "dahil ön boyutlandırma sonucudur."
    )

  st.info(
      "Bu analiz preliminary engineering feasibility amaçlıdır. "
      "Gerçek tekne geometrisi, direnç/CFD veya model deneyleri, "
      "pervane eşleştirmesi, üretici motor verileri ve deniz tecrübesi "
      "ile doğrulanmadan nihai tasarım veya sertifikasyon hesabı olarak kullanılamaz."
  )
