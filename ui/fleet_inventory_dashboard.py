import pandas as pd
import streamlit as st

from calculations.grant_program import calculate_first_year_grant_program
from ui.formatting import format_integer_tr


PHASE_ORDER = (
    "Faz 1",
    "Faz 2",
    "Faz 3",
    "Özel İnceleme",
)

PROFILE_LABELS = {
    "v1": "Tip 1 · 12 m Tek Gövdeli · 24 yolcu",
    "v2": "Tip 2 · 13,5 m Katamaran · 32 yolcu",
    "v3": "Tip 3 · 14 m Katamaran · 54 yolcu",
    "v4_24": "Tip 4A · 12 m Tek Gövdeli · 24 yolcu",
    "v4_32": "Tip 4B · 13,5 m Katamaran · 32 yolcu",
}

PROFILE_GROUPS = {
    "v1": "Kooperatif Üyesi",
    "v2": "Kooperatif Üyesi",
    "v3": "Kooperatif Üyesi",
    "v4_24": "Kooperatif Dışı",
    "v4_32": "Kooperatif Dışı",
}


def build_inventory_decision_table(analysis):
  rows = []

  for recommendation in analysis.recommendations:
    vessel = recommendation.vessel

    rows.append({
        "Tekne Adı": vessel.vessel_name,
        "Donatanı": vessel.owner_name,
        "Tekne Cinsi": vessel.vessel_type,
        "Boyu (m)": vessel.length_m,
        "Eni (m)": vessel.beam_m,
        "Yolcu Kapasitesi": vessel.passenger_capacity,
        "Kooperatif": vessel.cooperative_name,
        "Kooperatif Üyeliği": vessel.cooperative_status,
        "Dönüşüm Fazı": recommendation.conversion_phase,
        "Önerilen Tahrik": recommendation.recommended_propulsion,
        "Karar Durumu": recommendation.recommendation_status,
        "Hibe Yaklaşımı": recommendation.grant_status,
        "Karar Gerekçesi": recommendation.rationale,
    })

  return pd.DataFrame(rows)


def build_cooperative_fleet_table(analysis):
  rows = []

  for cooperative_name, summary in (
      analysis.cooperative_summary.items()
  ):
    rows.append({
        "Kooperatif": cooperative_name,
        "Toplam": summary["total"],
        "Faz 1": summary["phase_1"],
        "Faz 2": summary["phase_2"],
        "Yolcu Motoru": summary["passenger_motor"],
        "Gezinti / Tenezzüh": summary["excursion"],
    })

  if not rows:
    return pd.DataFrame(
        columns=[
            "Kooperatif",
            "Toplam",
            "Faz 1",
            "Faz 2",
            "Yolcu Motoru",
            "Gezinti / Tenezzüh",
        ]
    )

  return (
      pd.DataFrame(rows)
      .sort_values(
          by=["Toplam", "Kooperatif"],
          ascending=[False, True],
      )
      .reset_index(drop=True)
  )


def build_phase_one_cooperative_summary(analysis):
  phase_one = [
      recommendation
      for recommendation in analysis.recommendations
      if recommendation.conversion_phase == "Faz 1"
  ]

  counts = {}

  for recommendation in phase_one:
    status = recommendation.vessel.cooperative_status
    counts[status] = counts.get(status, 0) + 1

  return {
      "total": len(phase_one),
      "member": counts.get("Kooperatif üyesi", 0),
      "non_member": counts.get("Kooperatif dışı", 0),
      "unknown": counts.get("Bilinmiyor", 0),
  }


def inventory_financing_is_ready(allocation):
  if allocation is None:
    return False

  return (
      allocation.phase_one_total > 0
      and allocation.unknown_vessels == 0
      and allocation.activation_ready
  )


def calculate_inventory_financing(
    allocation,
    vessel_specs,
    grants_per_type,
    inputs,
):
  if not inventory_financing_is_ready(allocation):
    raise ValueError(
        "Faz 1 finansmanı hesaplanamaz: üyeliği bilinmeyen "
        "Faz 1 tekneleri bulunmaktadır."
    )

  counts = {
      key: int(allocation.target_counts[key])
      for key in (
          "v1",
          "v2",
          "v3",
          "v4_24",
          "v4_32",
      )
  }

  total_investment = sum(
      counts[key] * float(vessel_specs[key]["totalCost"])
      for key in counts
  )

  total_grant_need = sum(
      counts[key] * float(grants_per_type[key])
      for key in counts
  )

  total_owner_equity = (
      total_investment
      - total_grant_need
  )

  grant_program = calculate_first_year_grant_program(
      vessel_specs,
      counts,
      grants_per_type,
      ministry_budget_tl=inputs.grant_budget_ministry_tl,
      geka_budget_tl=inputs.grant_budget_geka_tl,
      yikob_budget_tl=inputs.grant_budget_yikob_tl,
      zero_waste_budget_tl=inputs.grant_budget_zero_waste_tl,
  )

  remaining_vessels = (
      sum(counts.values())
      - grant_program.funded_vessels
  )

  remaining_investment = (
      total_investment
      - grant_program.unlocked_investment_tl
  )

  return {
      "counts": counts,
      "total_investment_tl": total_investment,
      "total_grant_need_tl": total_grant_need,
      "total_owner_equity_tl": total_owner_equity,
      "grant_program": grant_program,
      "remaining_vessels": remaining_vessels,
      "remaining_investment_tl": remaining_investment,
  }


def _render_cooperative_fleet_breakdown(analysis):
  st.markdown(
      "**Kooperatif Bazlı Filo Dağılımı**"
  )

  cooperative_df = build_cooperative_fleet_table(
      analysis
  )

  if cooperative_df.empty:
    st.caption(
        "Envanterde kooperatif adı tanımlanmış tekne bulunmuyor."
    )
    return

  st.dataframe(
      cooperative_df,
      hide_index=True,
      use_container_width=True,
  )


def _render_phase_one_cooperative_status(analysis):
  summary = build_phase_one_cooperative_summary(
      analysis
  )

  if summary["unknown"] == 0:
    st.caption(
        "Üyelik verisi eksik: 0 · "
        "Faz 1 filosunun tamamında kooperatif statüsü tanımlı."
    )
  else:
    st.warning(
        f"Üyelik verisi eksik: {summary['unknown']} · "
        "Kooperatif statüsü bilinmeyen Faz 1 teknelerine "
        "otomatik finansman profili atanmaz."
    )

  return summary


def _render_target_allocation(allocation):
  st.markdown(
      "**Faz 1 Finansman Profil Dağılımı**"
  )

  st.caption(
      "Tip 1/2/3 ve Tip 4A/4B dağılımları mevcut senaryo "
      "paylarına göre oluşturulur. Bu dağılım optimum hedef filo "
      "olarak yorumlanmamalıdır."
  )

  if allocation is None:
    st.caption(
        "Faz 1 finansman profil dağılımı için geçerli "
        "envanter tahsisi bulunmuyor."
    )
    return

  rows = []

  for key in (
      "v1",
      "v2",
      "v3",
  ):
    rows.append({
        "Finansman Grubu": PROFILE_GROUPS[key],
        "Finansman Profili": PROFILE_LABELS[key],
        "Senaryo Payı": (
            f"%{allocation.member_target_shares[key] * 100:.0f}"
        ),
        "Tekne Adedi": allocation.target_counts[key],
    })

  for key in (
      "v4_24",
      "v4_32",
  ):
    rows.append({
        "Finansman Grubu": PROFILE_GROUPS[key],
        "Finansman Profili": PROFILE_LABELS[key],
        "Senaryo Payı": (
            f"%{allocation.non_member_target_shares[key] * 100:.0f}"
        ),
        "Tekne Adedi": allocation.target_counts[key],
    })

  st.dataframe(
      pd.DataFrame(rows),
      hide_index=True,
      use_container_width=True,
  )


def _render_financing(
    allocation,
    vessel_specs,
    inputs,
    fleet,
):
  st.markdown(
      "**Faz 1 Finansman İhtiyacı**"
  )

  st.caption(
      "Bu finansman özeti yalnız Faz 1 hedef filosunu kapsar. "
      "Faz 2 ve Faz 3 için kurulca kesinleştirilmiş tekne-başı "
      "yatırım ve finansman modeli bulunmadığından bu toplamların "
      "içine dahil edilmez."
  )

  if not inventory_financing_is_ready(allocation):
    unknown_vessels = (
        allocation.unknown_vessels
        if allocation is not None
        else 0
    )

    st.warning(
        "Envanter kaynaklı Faz 1 finansman hesabı üretilemedi. "
        "Kooperatif üyesi tekneler Tip 1/2/3, kooperatif dışı "
        "tekneler Tip 4A/4B profilleriyle hesaplanabilir; ancak "
        "üyeliği bilinmeyen Faz 1 teknesine finansman profili "
        "otomatik atanmaz."
    )

    if unknown_vessels:
      st.info(
          f"Üyeliği bilinmeyen Faz 1 tekne sayısı: "
          f"{unknown_vessels}. Kooperatif statüsü "
          "doğrulandığında finansman hesabı otomatik olarak "
          "kullanılabilir hale gelir."
      )

    return

  financing = calculate_inventory_financing(
      allocation,
      vessel_specs,
      fleet.grants_per_type,
      inputs,
  )

  grant_program = financing["grant_program"]

  investment_col, grant_col = st.columns(2)

  with investment_col:
    st.metric(
        "Toplam Yatırım",
        f"₺{format_integer_tr(financing['total_investment_tl'])}",
    )

  with grant_col:
    st.metric(
        "Toplam Hibe İhtiyacı",
        f"₺{format_integer_tr(financing['total_grant_need_tl'])}",
    )

  equity_col, funded_col = st.columns(2)

  with equity_col:
    st.metric(
        "Toplam Özkaynak İhtiyacı",
        f"₺{format_integer_tr(financing['total_owner_equity_tl'])}",
    )

  with funded_col:
    st.metric(
        "İlk Yıl Desteklenebilecek",
        f"{grant_program.funded_vessels} tekne",
    )

  allocated_col, unlocked_col = st.columns(2)

  with allocated_col:
    st.metric(
        "İlk Yıl Tahsis Edilebilen Hibe",
        f"₺{format_integer_tr(grant_program.allocated_grant_tl)}",
    )

  with unlocked_col:
    st.metric(
        "İlk Yıl Harekete Geçen Yatırım",
        f"₺{format_integer_tr(grant_program.unlocked_investment_tl)}",
    )

  st.metric(
      "İlk Yıl Sonrası Kalan Faz 1",
      f"{financing['remaining_vessels']} tekne",
      help=(
          "Birleşik ilk yıl hibe bütçesi ve mevcut program "
          "öncelikleri sonrasında henüz finanse edilemeyen "
          "Faz 1 tekne sayısı."
      ),
  )

  counts = financing["counts"]

  st.caption(
      "Kooperatif üyesi Faz 1 filosu Tip 1/2/3; "
      "kooperatif dışı Faz 1 filosu Tip 4A/4B finansman "
      "profilleriyle hesaplandı. "
      f"Profil toplamı: {sum(counts.values())} tekne."
  )


def render_fleet_inventory_dashboard(
    analysis,
    *,
    allocation,
    plan_active,
    vessel_specs,
    inputs,
    fleet,
):
  if analysis is None:
    return

  st.subheader(
      "📊 Envanter Dönüşüm Analizi"
  )

  total_inventory = len(
      analysis.recommendations
  )

  phase_counts = analysis.phase_counts

  phase_one_summary = (
      build_phase_one_cooperative_summary(
          analysis
      )
  )

  st.caption(
      f"Yüklenen envanterde {total_inventory} tekne analiz edildi. "
      "Aktif geliştirme ve finansman odağı Faz 1 yolcu motorlarıdır."
  )

  st.markdown(
      "**Faz 1 · Yolcu Motorları**"
  )

  phase_one_col, member_col, non_member_col = st.columns(3)

  with phase_one_col:
    st.metric(
        "Faz 1 Toplam",
        phase_one_summary["total"],
    )

  with member_col:
    st.metric(
        "Kooperatif Üyesi",
        phase_one_summary["member"],
    )

  with non_member_col:
    st.metric(
        "Kooperatif Dışı",
        phase_one_summary["non_member"],
    )

  _render_phase_one_cooperative_status(
      analysis
  )

  st.caption(
      f"Toplam Envanter: {total_inventory} · "
      f"Faz 2: {phase_counts.get('Faz 2', 0)} · "
      f"Faz 3: {phase_counts.get('Faz 3', 0)} · "
      f"Özel İnceleme: "
      f"{phase_counts.get('Özel İnceleme', 0)}"
  )

  if plan_active:
    st.success(
        "Envanter planı aktif senaryo olarak kullanılıyor. "
        "Ana teknik filo, enerji ve Faz 1 finansman hesapları "
        "aynı statü-duyarlı senaryo dağılımını esas alıyor."
    )

  else:
    st.info(
        "Envanter analiz edildi ancak aktif senaryo yapılmadı. "
        "Ana hesaplar manuel filo girdilerini kullanmaya devam ediyor."
    )

  _render_target_allocation(
      allocation
  )

  _render_financing(
      allocation,
      vessel_specs,
      inputs,
      fleet,
  )

  with st.expander(
      "Kooperatif bazlı filo ayrıntısı",
      expanded=False,
  ):
    _render_cooperative_fleet_breakdown(
        analysis
    )

  with st.expander(
      "Tekne bazlı dönüşüm kararları",
      expanded=False,
  ):
    decision_df = build_inventory_decision_table(
        analysis
    )

    filter_left, filter_right = st.columns(
        [0.35, 0.65]
    )

    with filter_left:
      phase_filter = st.selectbox(
          "Dönüşüm fazı",
          ["Tümü", *PHASE_ORDER],
          key="inventory_dashboard_phase_filter",
      )

    vessel_types = sorted(
        value
        for value in (
            decision_df["Tekne Cinsi"]
            .dropna()
            .unique()
        )
        if value
    )

    with filter_right:
      vessel_type_filter = st.multiselect(
          "Tekne cinsi",
          vessel_types,
          key="inventory_dashboard_type_filter",
      )

    filtered = decision_df

    if phase_filter != "Tümü":
      filtered = filtered[
          filtered["Dönüşüm Fazı"]
          == phase_filter
      ]

    if vessel_type_filter:
      filtered = filtered[
          filtered["Tekne Cinsi"].isin(
              vessel_type_filter
          )
      ]

    st.caption(
        f"{len(filtered)} / "
        f"{len(decision_df)} tekne gösteriliyor."
    )

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True,
        height=430,
        column_config={
            "Boyu (m)": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Eni (m)": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Yolcu Kapasitesi": st.column_config.NumberColumn(
                format="%d"
            ),
            "Karar Gerekçesi": st.column_config.TextColumn(
                width="large"
            ),
        },
    )

  st.divider()