import pandas as pd
import streamlit as st

from calculations.fleet_inventory_analysis import (
    COOPERATIVE_MEMBER,
)
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


def inventory_financing_is_ready(analysis):
  phase_one = [
      recommendation
      for recommendation in analysis.recommendations
      if recommendation.conversion_phase == "Faz 1"
  ]

  if not phase_one:
    return False

  return all(
      recommendation.vessel.cooperative_status == COOPERATIVE_MEMBER
      for recommendation in phase_one
  )


def calculate_inventory_financing(
    analysis,
    vessel_specs,
    grants_per_type,
    inputs,
):
  if not inventory_financing_is_ready(analysis):
    raise ValueError(
        "Faz 1 finansmanı hesaplanamaz: tüm Faz 1 teknelerinin "
        "kooperatif üyeliği doğrulanmış olmalıdır."
    )

  target_counts = analysis.target_fleet.target_counts

  counts = {
      "v1": int(target_counts["v1"]),
      "v2": int(target_counts["v2"]),
      "v3": int(target_counts["v3"]),
      "v4_24": 0,
      "v4_32": 0,
  }

  total_investment = sum(
      counts[key] * float(vessel_specs[key]["totalCost"])
      for key in counts
  )

  total_grant_need = sum(
      counts[key] * float(grants_per_type[key])
      for key in counts
  )

  total_owner_equity = total_investment - total_grant_need

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


def _render_phase_one_cooperative_status(analysis):
  summary = build_phase_one_cooperative_summary(analysis)

  st.markdown("**Faz 1 Kooperatif Statüsü**")

  c1, c2, c3, c4 = st.columns(4)

  c1.metric(
      "Faz 1 Toplam",
      summary["total"],
  )
  c2.metric(
      "Kooperatif Üyesi",
      summary["member"],
  )
  c3.metric(
      "Kooperatif Dışı",
      summary["non_member"],
  )
  c4.metric(
      "Üyeliği Bilinmiyor",
      summary["unknown"],
  )

  return summary


def _render_financing(
    analysis,
    vessel_specs,
    inputs,
    fleet,
):
  st.markdown("**Faz 1 Finansman İhtiyacı**")

  st.caption(
      "Bu finansman özeti yalnız Faz 1 hedef filosunu kapsar. "
      "Faz 2 hibrit tekneler ile Faz 3 özel tekneler için henüz "
      "tekne-başı yatırım ve finansman modeli tanımlanmadığından "
      "bu toplamların içine dahil edilmez."
  )

  if not inventory_financing_is_ready(analysis):
    st.warning(
        "Envanter kaynaklı hibe hesabı henüz oluşturulmadı. "
        "Mevcut Tip 1/2/3 hibe modeli kooperatif üyesi tekneler "
        "için tanımlıdır. Faz 1 envanterinde kooperatif dışı veya "
        "üyeliği bilinmeyen tekne bulunduğunda bütün Faz 1 filosunu "
        "kooperatif üyesi kabul ederek hibe hesaplamak doğru değildir."
    )

    st.info(
        "Teknik hedef filo analizi kullanılabilir. Finansman hesabı "
        "ise tekne bazlı kooperatif statüsü ve yeni hibe tahsis "
        "yöntemi kesinleştirildikten sonra üretilecektir."
    )

    return

  financing = calculate_inventory_financing(
      analysis,
      vessel_specs,
      fleet.grants_per_type,
      inputs,
  )

  grant_program = financing["grant_program"]

  f1, f2, f3, f4 = st.columns(4)

  f1.metric(
      "Toplam Hedef Yatırım",
      f"₺{format_integer_tr(financing['total_investment_tl'])}",
  )

  f2.metric(
      "Toplam Hibe İhtiyacı",
      f"₺{format_integer_tr(financing['total_grant_need_tl'])}",
  )

  f3.metric(
      "Toplam Özkaynak İhtiyacı",
      f"₺{format_integer_tr(financing['total_owner_equity_tl'])}",
  )

  f4.metric(
      "İlk Yıl Desteklenebilecek",
      f"{grant_program.funded_vessels} tekne",
  )

  g1, g2, g3 = st.columns(3)

  g1.metric(
      "İlk Yıl Tahsis Edilebilen Hibe",
      f"₺{format_integer_tr(grant_program.allocated_grant_tl)}",
  )

  g2.metric(
      "İlk Yıl Harekete Geçen Yatırım",
      f"₺{format_integer_tr(grant_program.unlocked_investment_tl)}",
  )

  g3.metric(
      "İlk Yıl Sonrası Kalan Faz 1",
      f"{financing['remaining_vessels']} tekne",
      help=(
          "Birleşik ilk yıl hibe bütçesi ve mevcut program "
          "öncelikleri sonrasında henüz finanse edilemeyen "
          "Faz 1 tekne sayısı."
      ),
  )

  st.caption(
      "Bu hesap yalnız kooperatif üyeliği doğrulanmış Faz 1 "
      "envanteri için mevcut Tip 1/2/3 kooperatif hibe "
      "senaryosunu kullanır."
  )


def render_fleet_inventory_dashboard(
    analysis,
    *,
    plan_active,
    vessel_specs,
    inputs,
    fleet,
):
  if analysis is None:
    return

  st.subheader("📊 Envanter Dönüşüm Analizi")

  total_inventory = len(analysis.recommendations)
  phase_counts = analysis.phase_counts
  target_counts = analysis.target_fleet.target_counts

  st.caption(
      f"Yüklenen envanterde {total_inventory} tekne analiz edildi. "
      "Dönüşüm fazları mevcut tekne cinsine göre; Faz 1 hedef filo "
      "dağılımı ise belirlenen Tip 1/2/3 planlama oranlarına göre "
      "oluşturulur."
  )

  c1, c2, c3, c4, c5 = st.columns(5)

  c1.metric(
      "Toplam Envanter",
      total_inventory,
  )
  c2.metric(
      "Faz 1 · Tam Elektrik",
      phase_counts.get("Faz 1", 0),
  )
  c3.metric(
      "Faz 2 · Hibrit",
      phase_counts.get("Faz 2", 0),
  )
  c4.metric(
      "Faz 3 · Özel",
      phase_counts.get("Faz 3", 0),
  )
  c5.metric(
      "Özel İnceleme",
      phase_counts.get("Özel İnceleme", 0),
  )

  if plan_active:
    st.success(
        "Envanter planı aktif senaryo olarak kullanılıyor. "
        "Ana teknik filo ve enerji hesapları aşağıdaki Faz 1 "
        "hedef dağılımını esas alıyor. Envanter finansmanı ayrıca "
        "kooperatif statüsü doğrulamasına tabidir."
    )
  else:
    st.info(
        "Envanter analiz edildi ancak aktif senaryo yapılmadı. "
        "Ana hesaplar manuel filo hedeflerini kullanmaya devam ediyor."
    )

  st.markdown("**Faz 1 Hedef Filo Dağılımı**")

  target_df = pd.DataFrame([
      {
          "Hedef Tekne Tipi": PROFILE_LABELS[key],
          "Hedef Pay": (
              f"%{analysis.target_fleet.target_shares[key] * 100:.0f}"
          ),
          "Tekne Adedi": target_counts[key],
      }
      for key in ("v1", "v2", "v3")
  ])

  st.dataframe(
      target_df,
      hide_index=True,
      use_container_width=True,
  )

  _render_phase_one_cooperative_status(analysis)

  _render_financing(
      analysis,
      vessel_specs,
      inputs,
      fleet,
  )

  st.markdown("**Tekne Bazlı Dönüşüm Kararları**")

  decision_df = build_inventory_decision_table(analysis)

  filter_left, filter_right = st.columns([0.35, 0.65])

  with filter_left:
    phase_filter = st.selectbox(
        "Dönüşüm fazı",
        ["Tümü", *PHASE_ORDER],
        key="inventory_dashboard_phase_filter",
    )

  vessel_types = sorted(
      value
      for value in decision_df["Tekne Cinsi"].dropna().unique()
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
        filtered["Dönüşüm Fazı"] == phase_filter
    ]

  if vessel_type_filter:
    filtered = filtered[
        filtered["Tekne Cinsi"].isin(vessel_type_filter)
    ]

  st.caption(
      f"{len(filtered)} / {len(decision_df)} tekne gösteriliyor."
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
