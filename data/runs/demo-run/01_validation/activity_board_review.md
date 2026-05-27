# Activity Board Review

Total activities: 100
Primary activities: 49
Substitution activities: 51

## Modality Counts
- consultation: 30
- fitness: 30
- food: 20
- medication: 5
- therapy: 15

## QA Flags
- breakfast has 3 primary food activities; confirm meal-slot exclusivity and weekly denominator intent: Chef-prepared high-protein breakfast, Office-delivered breakfast, Hotel buffet or room-service breakfast (travel)
- dinner has 3 primary food activities; confirm meal-slot exclusivity and weekly denominator intent: Chef-prepared dinner at home, Structured restaurant dinner, Hotel or restaurant dinner (travel)
- lunch has 3 primary food activities; confirm meal-slot exclusivity and weekly denominator intent: Chef-prepped or delivered office lunch, Restaurant or hotel lunch (travel), Member-assembled lunch at home
- act_b01_lunch_home_no_prep looks like support/prep/protocol work but has no dependency link.
- act_b01_dinner_restaurant_no_prep looks like support/prep/protocol work but has no dependency link.
- act_b01_fasting_aware_meal_support_remote_check_sub looks like support/prep/protocol work but has no dependency link.
- act_b01_supplement_protocol_support_primary looks like support/prep/protocol work but has no dependency link.
- act_b01_supplement_protocol_support_travel_timing_sub looks like support/prep/protocol work but has no dependency link.
- act_b02_cardio_cgm_log_support_primary looks like support/prep/protocol work but has no dependency link.
- act_b02_cardio_hydration_protocol_support_primary looks like support/prep/protocol work but has no dependency link.
- act_b02_cardio_hydration_protocol_support_hotel_protocol_sub looks like support/prep/protocol work but has no dependency link.
- act_b03_strength_lower_load_strength_adjustment_remote looks like support/prep/protocol work but has no dependency link.
- act_b03_strength_provider_unavailable_strength_substitution_remote looks like support/prep/protocol work but has no dependency link.
- act_b04_recovery_load_adjustment_after_poor_sleep_primary looks like support/prep/protocol work but has no dependency link.
- act_b01_breakfast_travel_hotel_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b01_lunch_restaurant_travel_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b01_dinner_travel_hotel_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b01_supplement_protocol_support_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b02_cardio_cgm_log_support_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b02_cardio_hydration_protocol_support_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b03_strength_bodyweight_travel_substitution_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b03_strength_mobility_post_travel_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b03_strength_trainer_remote_substitution_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b03_strength_provider_unavailable_strength_substitution_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
- act_b04_recovery_evening_routine_travel_primary is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family.
