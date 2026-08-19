from copy import deepcopy

from calculations.assumptions_transparency import (
    CALCULATED_RESULT,
    CALIBRATED_ESTIMATE,
    COMMISSION_CRITERION,
    ENGINEERING_ASSUMPTION,
    FALLBACK_MARKET_DATA,
    LIVE_MARKET_DATA,
    USER_INPUT,
    build_assumptions_transparency,
)
from config.vessel_factory import build_vessel_specs
from models.inputs import SimulationInputs


def inputs():
  return SimulationInputs(
      count_v1=50,
      count_v2=50,
      count_v3=40,
      count_v4_24=30,
      count_v4_32=20,
      cost_eur_v1=108100,
      cost_eur_v2=144140,
      cost_eur_v3=180180,
      eur_rate=55.5,
      diesel_price=81.81,
      elec_price=3.5,
      operating_days=180,
      sun_hours=8.0,
      daily_miles=35.0,
      cruise_speed=6.0,
  )


def vessel_specs():
  return build_vessel_specs(108100, 144140, 180180, 55.5)


def rows_by_parameter(rows):
  return {row.parameter: row for row in rows}


def test_source_classification_contains_management_categories():
  rows = build_assumptions_transparency(inputs(), vessel_specs(), True, False)
  categories = {row.source_type for row in rows}

  assert USER_INPUT in categories
  assert LIVE_MARKET_DATA in categories
  assert FALLBACK_MARKET_DATA in categories
  assert COMMISSION_CRITERION in categories
  assert ENGINEERING_ASSUMPTION in categories
  assert CALIBRATED_ESTIMATE in categories
  assert CALCULATED_RESULT in categories


def test_live_and_fallback_market_labels_follow_current_flags():
  live = rows_by_parameter(
      build_assumptions_transparency(inputs(), vessel_specs(), True, True)
  )
  fallback = rows_by_parameter(
      build_assumptions_transparency(inputs(), vessel_specs(), False, False)
  )

  assert live["EUR/TRY kuru"].source_type == LIVE_MARKET_DATA
  assert live["Dizel fiyatı"].source_type == LIVE_MARKET_DATA
  assert fallback["EUR/TRY kuru"].source_type == FALLBACK_MARKET_DATA
  assert fallback["Dizel fiyatı"].source_type == FALLBACK_MARKET_DATA


def test_commission_criteria_are_not_mislabeled_as_assumptions():
  rows = rows_by_parameter(
      build_assumptions_transparency(inputs(), vessel_specs(), True, True)
  )

  for parameter in (
      "Komisyon asgari hızı",
      "Komisyon asgari menzili",
      "Komisyon motor verimi eşiği",
  ):
    assert rows[parameter].source_type == COMMISSION_CRITERION
    assert rows[parameter].source_type != ENGINEERING_ASSUMPTION


def test_engineering_values_and_wetted_surface_distinction_are_explicit():
  rows = rows_by_parameter(
      build_assumptions_transparency(inputs(), vessel_specs(), True, True)
  )

  for parameter in (
      "Form faktörü",
      "Artık direnç",
      "Eklenti direnci",
      "Sevk verimi",
      "Kullanılabilir batarya payı",
      "Operasyon rezervi",
      "Otel yükü",
      "Güneş paneli verimi",
      "Güneş sistemi derating faktörü",
      "Kullanılan ıslak yüzey alanı (v1)",
  ):
    assert rows[parameter].source_type == ENGINEERING_ASSUMPTION

  assumed = rows["Kullanılan ıslak yüzey alanı (v1)"]
  sanity = rows["Islak yüzey sanity tahmini (v1)"]
  assert assumed.current_value == "30 m²"
  assert "hidrostatik veri değildir" in assumed.description
  assert sanity.source_type == CALCULATED_RESULT
  assert sanity.current_value == "27,45 m²"
  assert "direnç hesabına girmez" in sanity.description


def test_building_transparency_does_not_mutate_inputs_or_specs():
  current_inputs = inputs()
  specs = vessel_specs()
  original_inputs = deepcopy(current_inputs)
  original_specs = deepcopy(specs)

  build_assumptions_transparency(current_inputs, specs, True, False)

  assert current_inputs == original_inputs
  assert specs == original_specs
