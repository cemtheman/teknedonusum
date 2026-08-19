import streamlit as st

from models.compliance import ComplianceStatus
from models.presentation import TechnicalScenarioPresentation


def _format_decimal(value, decimal_places):
  return f"{value:.{decimal_places}f}".replace(".", ",")


def _format_percentage(value):
  percentage = value * 100
  if percentage.is_integer():
    return f"%{int(percentage)}"
  return f"%{_format_decimal(percentage, 1)}"


def _format_primary_value(value):
  if value.unit == "kW":
    return f"{_format_decimal(value.value, 1)} kW"
  if value.unit == "NM":
    return f"{_format_decimal(value.value, 1)} NM"
  if value.unit == "kWh/day":
    return f"{_format_decimal(value.value, 1)} kWh/gün"
  return str(value.value)


def _format_compliance_actual(value):
  if value.criterion == "loa":
    return f"{_format_decimal(value.actual_value, 1)} m"
  if value.criterion == "passenger_capacity":
    return f"{int(value.actual_value)}"
  if value.criterion == "minimum_speed":
    return f"{_format_decimal(value.actual_value, 1)} knot"
  if value.criterion == "minimum_navigation_range":
    return f"{_format_decimal(value.actual_value, 1)} NM"
  if value.criterion == "motor_efficiency":
    return _format_percentage(value.actual_value)
  if value.criterion == "battery_capacity":
    return f"{_format_decimal(value.actual_value, 1)} kWh"
  if value.criterion == "roof_length_fraction":
    return _format_percentage(value.actual_value)
  return str(value.actual_value)


def _format_compliance_required(value):
  if value.criterion == "roof_length_fraction":
    percentage = value.required_value.split("%", 1)[1].split("'", 1)[0]
    return f"≥ %{percentage.replace('.0', '').replace('.', ',')}"
  if value.criterion == "motor_efficiency":
    return value.required_value.replace(".0", "").replace(".", ",")
  return value.required_value.replace(".", ",")


def _format_detail_value(value):
  if value.key == "effective_power":
    return f"{_format_decimal(value.value, 2)} kW"
  if value.key == "motor_output_power":
    return f"{_format_decimal(value.value, 2)} kW"
  if value.key == "energy_per_nm":
    return f"{_format_decimal(value.value, 2)} kWh/NM"
  if value.key == "solar_coverage":
    return _format_percentage(value.value)
  if value.key == "excess_solar_energy":
    return f"{_format_decimal(value.value, 2)} kWh/gün"
  return str(value.value)


def render_technical_scenario(
    presentation: TechnicalScenarioPresentation,
) -> None:
  if not isinstance(presentation, TechnicalScenarioPresentation):
    raise TypeError("presentation must be a TechnicalScenarioPresentation")

  st.divider()
  st.subheader("⚙️ Ön Teknik Uygunluk ve Enerji Değerlendirmesi")
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
      "⚠️ Güç, menzil, güneş enerjisi üretimi ve enerji ihtiyacı sonuçları "
      "ön tasarım tahminleridir; doğrulanmış nihai tekne performans değerleri "
      "değildir."
  )

  st.markdown("#### Teknik Komisyon Kriterleri")
  for value in presentation.compliance_values:
    icon = "✅" if value.status is ComplianceStatus.PASS else "❌"
    actual = _format_compliance_actual(value)
    required = _format_compliance_required(value)
    st.markdown(
        f"{icon} {value.label}: {actual} · Kriter: {required}"
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
        "Efektif güç, teknenin hidrodinamik direncini yenmek için gereken "
        "güçtür. Kurulu motor gücü ise sevk verimi ve tasarım marjı dikkate "
        "alınarak elde edilen ön boyutlandırma değeridir."
    )

  st.info(
      "Bu analiz ön mühendislik yapılabilirlik değerlendirmesi amacıyla "
      "hazırlanmıştır. Gerçek tekne geometrisi, direnç/CFD analizleri veya "
      "model deneyleri, pervane eşleştirmesi, üretici motor verileri ve deniz "
      "tecrübeleri ile doğrulanmadan nihai tasarım veya sertifikasyon hesabı "
      "olarak kullanılamaz."
  )
