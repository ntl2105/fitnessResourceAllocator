# Assembled Prompt: Stage 06 Activity Board Review

Send this prompt to OpenAI.

---

## System Role

# System Role

You are generating synthetic demo data for an Elyx HealthSpan Resource Allocator prototype.

Your job is to produce realistic, internally consistent, schema-valid data for a scheduling and resource-allocation system. The data should help demonstrate how a simple allocator adapts a member's health plan around availability, travel, equipment, providers, food prep, and other constraints.

This is synthetic demo data only. It is not medical advice. Do not claim clinical validity. Do not diagnose the member. Do not invent medical facts beyond plausible scheduling-demo context.

## Output Discipline

- Output only the requested artifact.
- If the requested artifact is JSON, output valid JSON only.
- Do not include Markdown, comments, prose, or explanations outside the JSON unless the stage explicitly asks for Markdown.
- Use stable IDs that are easy to reference later.
- Preserve IDs from previous-stage inputs exactly.
- Do not invent provider, equipment, location, or travel IDs after the resource-universe stage.
- Make constraints realistic enough to produce meaningful scheduler traces.
- Do not make every activity perfectly schedulable.
- Some substitutions, reschedules, and unscheduled tasks should be expected.
- Prefer coherent care logic over superficial variety.

## Synthetic Data Boundary

The generated data should be plausible for a healthspan concierge scheduling demo, but it should not be clinically authoritative. Use language such as "physician review," "approved protocol," "synthetic marker," and "care-team follow-up" rather than definitive medical claims.

---

## Stage Instructions

# Stage 06: Activity Board Final Review

You are reviewing the complete generated activity board after all activity families have been generated, flattened, and structurally validated.

The goal is to assess whether the activity board is a coherent synthetic health journey, not merely a collection of valid rows.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`
- `known_frictions.json`
- `activity_families.json`
- flattened `action_plan.json`
- deterministic validation summary

## Output

Return Markdown for:

```text
data/runs/<run_id>/01_validation/activity_board_review.md
```

## Review sections

Include:

1. `Status`
2. `Board-level summary`
3. `Priority review`
4. `Goal coverage review`
5. `Journey phase review`
6. `Dependency review`
7. `Substitution review`
8. `Food and meal review`
9. `Known friction coverage`
10. `Care handoff review`
11. `Warnings`
12. `Repair recommendations`

## Review criteria

Check:

- priorities are internally consistent across goals and modalities
- high-priority activities map to the member's stated primary goals
- support activities do not outrank core goal activities without a clear reason
- member goals include weekly and 3-month target definitions that make calendar coverage explainable
- member profile includes `goal_actions` that define concrete weekly and 3-month denominators
- every high-priority goal action is covered by enough primary or substitution activity families
- every family that claims goal coverage references valid `goal_action_id` values
- activity goal tags and `goal_contributions` are specific enough to explain week-level progress
- low-complexity daily habits, supplements, and reminders do not inflate weekly goal coverage
- prep, planning, reminders, logs, handoffs, protocol checks, and ordering precommitments are not counted as core weekly target completion
- goal actions are neither obviously under-supplied nor over-supplied by generated core activity frequency
- if a goal action is over target, extra work is justified as optional, support, or phase-specific rather than counted as required progress
- substitutions are counted as weekly goal coverage only when they preserve the same goal intent
- substitutions include `substitution_for_activity_id`,
  `substitution_reason_codes`, and `substitution_notes`
- travel-adapted activities are substitutions or alternate delivery modes for
  underlying meal, cardio, strength, recovery, consultation, measurement, or
  adherence actions, not their own core goal denominator
- any goal action with travel in the ID or label is `support_only: true`
  unless the member profile provides a specific independent travel training
  goal
- travel-context substitutions count toward the underlying goal action
  they preserve, not toward a separate travel action
- every week should have an inspectable target denominator: scheduled, unscheduled, substituted, and at-risk counts must map back to generated activities
- goal progression is plausible across the 3-month journey
- baseline, travel, pain escalation, and consolidation phase activities fit their phases
- dependencies form a coherent graph
- food prep, lab prerequisites, medication-with-food, and consultation-after-lab requirements are coherent
- food coverage includes real breakfast, lunch, and dinner activities where nutrition is part of the journey
- supplement protocols do not masquerade as meal coverage
- meal timing responds to fasting labs, chef availability, member-prep preferences, travel state, and no-prep fallback conditions
- food support activities such as prep, planning, fiber checks, protein confirmations, and restaurant precommitments do not masquerade as breakfast, lunch, or dinner completion
- substitutions preserve primary activity intent
- substitutions reduce at least one scheduling constraint
- substitution titles read like member-facing activities, while fallback/substitution rationale lives in metadata
- substitutions do not create harder dependencies than the primary unless justified
- lower-load, post-travel, fatigue-sensitive, or pain-sensitive variants are
  substitutions when they replace a normal training session; they should be
  primary activities only when they are independent recovery work
- load distribution supports recovery and avoids unrealistic clustering
- known frictions are represented in activities or scheduling constraints
- travel over 3 hours creates visible lower-load, recovery, or reduced-capacity logic on the arrival day or next day
- the board does not require exact commute/transport-time modeling for this version
- care handoff metadata is present when provider coordination is needed
- there are no obvious duplicated, contradictory, or clinically implausible prescriptions

## Output discipline

Be specific and actionable.

If the board is acceptable, say so and list accepted limitations.

If repair is needed, provide targeted repair recommendations rather than rewriting the whole board.

---

## member_profile.json

```json
{
  "age_range": "46-50",
  "baseline_metrics": {
    "body_composition": {
      "estimated_body_fat_percent": 23,
      "height_cm": 172,
      "waist_cm": 90,
      "weight_kg": 74
    },
    "fitness": {
      "cardio_pattern": "intermittent, drops during heavy travel",
      "estimated_vo2max_category": "below_average",
      "resting_heart_rate_bpm": 65,
      "strength_level": "intermediate"
    },
    "metabolic": {
      "risk_level": "mildly elevated",
      "synthetic_markers": [
        {
          "name": "fasting_glucose",
          "value": "slightly elevated (synthetic)"
        },
        {
          "name": "LDL-C",
          "value": "borderline (synthetic)"
        }
      ]
    },
    "sleep": {
      "average_bedtime": "23:40",
      "average_sleep_duration_hours": 6.1,
      "main_issue": "work-travel rhythm, investor calls, and late client dinners",
      "wake_time": "06:15"
    },
    "subjective": {
      "afternoon_energy_average": 7.1,
      "morning_energy_average": 6.5,
      "travel_week_energy_average": 5.6
    }
  },
  "constraints": {
    "behavioral": [
      "adherence drops if routines are overly complex or require daily meal prep/logging",
      "low friction is essential for routines to persist during travel",
      "opposes wellness interventions without clear, quantified rationale"
    ],
    "medical_safety": [
      "synthetic demo profile only",
      "abnormal or trend-worsening labs route to physician review",
      "high-intensity or high-load activity avoided after fatigue, travel, or pain"
    ],
    "physical": [
      {
        "constraint_id": "constraint_knee_001",
        "description": "Mild irritation post running or high flexion, aggravated if volume increases abruptly.",
        "implications": [
          "avoid running volume spikes",
          "prefer knee-safe lower body strength",
          "use cycling, rowing, or swimming during flare-ups"
        ],
        "name": "Mild right-knee irritation",
        "severity": "mild"
      },
      {
        "constraint_id": "constraint_back_001",
        "description": "Back tightness emerges often after flights exceeding 3 hours or long conference days.",
        "implications": [
          "schedule mobility or recovery post-travel",
          "avoid heavy deadlifts or loaded movements immediately after flights"
        ],
        "name": "Lower-back tightness after >3h flight or long sitting",
        "severity": "mild"
      }
    ],
    "schedule": [
      "monthly planned travel (2-6 days duration)",
      "occasional last-minute trips to Jakarta or Bangkok (short notice)",
      "morning and evening cross-timezone calls 2-3x/week",
      "client dinners up to 3x per month",
      "inconsistent sleep on travel weeks"
    ]
  },
  "dietary_access_plan": {
    "chef_capacity_per_week": 2,
    "dining_out_allowance_per_week": 3,
    "explicit_meal_scheduling": [
      "breakfast",
      "lunch",
      "dinner"
    ],
    "food_source_labels": [
      "chef_prepped",
      "office_delivery",
      "packed_meal",
      "member_assembled",
      "restaurant",
      "hotel_buffet",
      "room_service"
    ],
    "home_chef_access": true,
    "member_assembly_limit_per_week": 2,
    "normal_week_strategy": {
      "breakfast": "home chef-prepped or low-prep high-protein breakfast",
      "dinner": "home chef-prepped meal, with limited structured restaurant dinners when work or social context requires",
      "lunch": "structured office lunch from chef-prepped packed meal or office delivery"
    },
    "notes": "Chef/provider work should appear as food-source context unless Marcus actively participates. Office lunch should be schedulable while Marcus is at the office.",
    "office_meal_access": "chef-prepped packed lunch or office delivery during work blocks",
    "travel_meal_strategy": {
      "last_minute_low_resource_travel": "restaurant or room-service meals, fewer assumptions about ideal structure, remote dietitian support if adherence risk rises",
      "planned_high_resource_travel": "hotel buffet or room-service breakfast; restaurant or hotel lunch and dinner with dietitian guidance when needed"
    }
  },
  "goal_actions": [
    {
      "activity_types": [
        "food"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_structured_meals_weekly",
      "goal_id": "goal_metabolic_health",
      "label": "Complete structured metabolic meals",
      "notes": "Chef-prepped, member-assembled (<2x per week), or travel-compatible meals count as structured. Supplement protocols or meal planning do not count.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "meals",
        "units": 14
      }
    },
    {
      "activity_types": [
        "fitness"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_aerobic_conditioning_weekly",
      "goal_id": "goal_metabolic_health",
      "label": "Complete aerobic conditioning",
      "notes": "Zone 2 \u2018true cardio\u2019, swimming, cycling, or suitable travel/hotel-gym equivalents count directly.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      }
    },
    {
      "activity_types": [
        "fitness"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_strength_sessions_weekly",
      "goal_id": "goal_strength_and_mobility",
      "label": "Complete knee-modified strength sessions",
      "notes": "Trainer-led, hotel-gym, or bodyweight alternatives count if following knee-safe plan. Mobility substituted only post-travel or pain.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      }
    },
    {
      "activity_types": [
        "therapy",
        "fitness",
        "food"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_sleep_recovery_weekly",
      "goal_id": "goal_sleep_recovery",
      "label": "Complete sleep and fatigue recovery actions",
      "notes": "Evening mobility, recovery, post-flight stretching, and travel sleep protection actions count. Logging or reminders do not.",
      "role": "recovery",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "actions",
        "units": 4
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_clinical_review_3month",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete preventive lab or provider review (when due)",
      "notes": "Only counts on scheduled lab, physician, or dietitian review weeks. Remote or in-person review is valid.",
      "role": "measurement",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "3_month",
        "unit_label": "reviews",
        "units": 4
      }
    },
    {
      "activity_types": [
        "medication",
        "food",
        "consultation"
      ],
      "counts_substitutions": false,
      "goal_action_id": "ga_adherence_support_weekly",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete support adherence or supplement protocol",
      "notes": "Daily supplements, check-in logging, and checklist review support adherence but do not count as core outcome progress.",
      "role": "support",
      "substitutions_allowed": false,
      "support_only": true,
      "target": {
        "period": "weekly",
        "unit_label": "protocol checks",
        "units": 7
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_care_team_followthrough_3month",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete care-team review and decision follow-through",
      "notes": "Counts physician, dietitian, physio, remote care-team handoff, plan-adjustment review, and lab-result follow-up touchpoints. Passive logs and reminders do not count.",
      "role": "care_team",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "3_month",
        "unit_label": "touchpoints",
        "units": 6
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_behavior_coaching_weekly",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete behavior coaching and friction-resolution touchpoints",
      "notes": "Counts member-facing coaching, adherence barrier review, travel friction planning, post-missed-session coaching, and meal-prep failure resolution. Daily supplement-taking does not count.",
      "role": "coaching",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "touchpoints",
        "units": 1
      }
    }
  ],
  "goals": [
    {
      "description": "Reduce metabolic risk with structured meals, aerobic conditioning, measured protein, and regular physician and lab review.",
      "goal_id": "goal_metabolic_health",
      "goal_targets": [
        {
          "counts_activity_types": [
            "food",
            "fitness",
            "consultation"
          ],
          "goal_action_ids": [
            "ga_structured_meals_weekly",
            "ga_aerobic_conditioning_weekly"
          ],
          "minimum": 12,
          "notes": "Breakfast, lunch, and dinner structure and aerobic conditioning each count directly; supplement, meal planning, and chef prep are support-only.",
          "period": "weekly",
          "preferred": 14,
          "support_activity_types": [
            "medication"
          ],
          "unit": "support_context"
        }
      ],
      "name": "Improve metabolic health",
      "priority": 1,
      "success_indicators": [
        "14 structured meals completed per week",
        "2+ aerobic sessions/week",
        "improved fasting glucose at review"
      ]
    },
    {
      "description": "Build strength, especially lower-body and core, without aggravating right-knee or lower-back issues.",
      "goal_id": "goal_strength_and_mobility",
      "goal_targets": [
        {
          "counts_activity_types": [
            "fitness"
          ],
          "goal_action_ids": [
            "ga_strength_sessions_weekly"
          ],
          "minimum": 2,
          "notes": "Knee-modified strength or trainer-led sessions count. Mobility or assessment are support-only unless they replace strength after travel or pain.",
          "period": "weekly",
          "preferred": 3,
          "support_activity_types": [
            "therapy",
            "consultation"
          ],
          "unit": "core_activity"
        }
      ],
      "name": "Build and maintain safe, lean strength",
      "priority": 2,
      "success_indicators": [
        "2-3 knee-modified strength sessions",
        "trainer or physio assessment after travel",
        "no pain escalation post-strength work"
      ]
    },
    {
      "description": "Protect sleep duration and quality, especially on high-stress travel or late-call weeks, by targeting recovery, adjusting activity, and using provider support.",
      "goal_id": "goal_sleep_recovery",
      "goal_targets": [
        {
          "counts_activity_types": [
            "therapy",
            "fitness",
            "food"
          ],
          "goal_action_ids": [
            "ga_sleep_recovery_weekly"
          ],
          "minimum": 3,
          "notes": "Stretching, mobility, tailored post-travel routines, and sleep hygiene actions count. Logging or reminders are support-only.",
          "period": "weekly",
          "preferred": 4,
          "support_activity_types": [
            "consultation"
          ],
          "unit": "core_or_recovery_activity"
        }
      ],
      "name": "Preserve energy and consistent sleep, especially around travel",
      "priority": 3,
      "success_indicators": [
        "Sleep average at least 6h/night",
        "Less dropoff in sleep on travel",
        "At least 3 travel/fatigue recovery actions"
      ]
    },
    {
      "description": "Reduce fall-off during heavy travel weeks, ensure timely labs, and improve care-team coordination without increasing friction.",
      "goal_id": "goal_adherence_and_careteam",
      "goal_targets": [
        {
          "counts_activity_types": [
            "consultation"
          ],
          "goal_action_ids": [
            "ga_clinical_review_3month",
            "ga_adherence_support_weekly"
          ],
          "minimum": 1,
          "notes": "Labs and provider review count in due weeks only; adherence tasks and supplement protocols are tracked but don't inflate core coverage.",
          "period": "weekly",
          "preferred": 2,
          "support_activity_types": [
            "medication",
            "food"
          ],
          "unit": "measurement_or_support_activity"
        },
        {
          "goal_action_ids": [
            "ga_clinical_review_3month"
          ],
          "minimum": 1,
          "notes": "Full-horizon target used for 3-month goal attainment review.",
          "period": "3_month",
          "preferred": 4,
          "unit": "completed_actions"
        }
      ],
      "name": "Improve adherence and enable reliable preventive care",
      "priority": 4,
      "success_indicators": [
        "Follow up on scheduled labs and reviews",
        "Adherence logs above 80%",
        "Physician and dietitian reviews completed after screenings"
      ]
    },
    {
      "description": "Adapt core meal, movement, and provider routines while traveling. Accept substitutions as needed, prioritize continuity and quick recovery post-travel.",
      "goal_id": "goal_travel_resilience",
      "goal_targets": [
        {
          "counts_activity_types": [
            "fitness",
            "food"
          ],
          "goal_action_ids": [
            "ga_structured_meals_weekly",
            "ga_aerobic_conditioning_weekly",
            "ga_strength_sessions_weekly",
            "ga_sleep_recovery_weekly",
            "ga_behavior_coaching_weekly"
          ],
          "minimum": 2,
          "notes": "Travel is tracked as adaptation context. Travel meals, training, recovery, and remote care count toward their underlying weekly actions; this goal watches continuity and substitution quality without adding a separate core denominator.",
          "period": "weekly",
          "preferred": 3,
          "support_activity_types": [
            "therapy",
            "consultation"
          ],
          "unit": "core_activity"
        },
        {
          "goal_action_ids": [
            "ga_care_team_followthrough_3month",
            "ga_behavior_coaching_weekly"
          ],
          "minimum": 3,
          "notes": "Full-horizon target used for 3-month goal attainment review.",
          "period": "3_month",
          "preferred": 3,
          "unit": "completed_actions"
        }
      ],
      "name": "Maintain healthspan routines during heavy travel",
      "priority": 5,
      "success_indicators": [
        "1+ physical activity session completed during each travel window",
        "Structured meal adherence 80%+ during travel weeks",
        "At least 2 recovery/mobility sessions per multi-day trip"
      ]
    }
  ],
  "journey_phases": [
    {
      "end_date": "2026-06-18",
      "phase_id": "phase_marcus_001",
      "phase_type": "baseline",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "prioritize baseline labs and movement review",
        "avoid sudden increases in lower-body load",
        "use in-person chef and trainer when possible"
      ],
      "start_date": "2026-06-01",
      "trigger": "Start of new HealthSpan plan. Initial labs, chef briefing, and movement review."
    },
    {
      "end_date": "2026-06-25",
      "phase_id": "phase_marcus_002",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_sleep_recovery",
        "goal_metabolic_health"
      ],
      "scheduling_biases": [
        "prioritize aerobic and basic resistance training using hotel equipment",
        "use quick meal check-ins, chef-prepped or no-prep options",
        "avoid lab scheduling; all reviews remote"
      ],
      "start_date": "2026-06-19",
      "trigger": "Planned board meetings in Hong Kong. Use hotel gym and remote consults."
    },
    {
      "end_date": "2026-07-21",
      "phase_id": "phase_marcus_003",
      "phase_type": "consolidation",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "reaffirm morning sessions, check-in with dietitian",
        "progress strength work gradually",
        "confirm post-travel sleep/adherence"
      ],
      "start_date": "2026-06-26",
      "trigger": "Return from travel, stabilize routines and monitor metrics."
    },
    {
      "end_date": "2026-07-29",
      "phase_id": "phase_marcus_004",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_sleep_recovery",
        "goal_strength_and_mobility"
      ],
      "scheduling_biases": [
        "accept hotel gym or bodyweight subs",
        "use remote coach/dietitian as needed",
        "schedule mobility after arrival"
      ],
      "start_date": "2026-07-22",
      "trigger": "Planned Tokyo board and investor travel; full week out of Singapore, limited gym."
    },
    {
      "end_date": "2026-08-07",
      "phase_id": "phase_marcus_005",
      "phase_type": "pain_escalation",
      "primary_goals": [
        "goal_strength_and_mobility",
        "goal_sleep_recovery"
      ],
      "scheduling_biases": [
        "substitute strength with mobility; schedule physio consult",
        "minimize high load lower-body training",
        "coordinate handoff for trainer and physiotherapist"
      ],
      "start_date": "2026-08-01",
      "trigger": "Synthetic mild knee and back flare after post-travel overload."
    },
    {
      "end_date": "2026-08-16",
      "phase_id": "phase_marcus_006",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "focus on travel-compatible exercises",
        "structured eating mostly by restaurant with check-ins",
        "log fatigue post-travel"
      ],
      "start_date": "2026-08-13",
      "trigger": "Last-minute Jakarta escalation: low-resource, high stress, remote-only support."
    },
    {
      "end_date": "2026-08-31",
      "phase_id": "phase_marcus_007",
      "phase_type": "consolidation",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_sleep_recovery"
      ],
      "scheduling_biases": [
        "complete provider reviews/labs as due",
        "plan travel mitigation for next cycle",
        "avoid last-minute overload"
      ],
      "start_date": "2026-08-17",
      "trigger": "End-of-quarter check, final progress review, and next cycle planning."
    }
  ],
  "location_rhythm": {
    "home_location_id": "marcus_home",
    "office_location_id": "marcus_office",
    "ordinary_weekday_pattern": [
      {
        "likely_location": "marcus_home",
        "notes": "Preferred for home training, remote fitness or nutrition consultation, or chef breakfast.",
        "time_window": "06:00-08:15"
      },
      {
        "likely_location": "marcus_office",
        "notes": "Work focus; only short, low-complexity tasks feasible.",
        "time_window": "08:30-18:30"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Backup evening training window. Sometimes gym or travel-screen.",
        "time_window": "18:45-20:00"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Recovery, low-load habits, and wind down. Avoid strenuous sessions.",
        "time_window": "20:30-22:30"
      }
    ],
    "weekend_pattern": [
      {
        "likely_location": "marcus_gym_or_home",
        "notes": "Longer training with trainer or physiotherapist, or chef prep.",
        "time_window": "08:00-11:00"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Family, meal planning, chef prep, and light movement.",
        "time_window": "12:00-18:00"
      }
    ]
  },
  "member_id": "member_elyx_marcus_001",
  "name": "Marcus Tan",
  "occupation": "Founder-Operator & Regional CEO, Logistics Technology",
  "preferences": {
    "communication_preferences": {
      "detail_level": "medium",
      "preferred_channels": [
        "app",
        "weekly summary"
      ],
      "style": "concise, rational, and progress-focused"
    },
    "consultation_preferences": [
      "prefers concise, actionable summaries",
      "accepts remote consultations (especially travel weeks)",
      "prefers in-person physio and movement review when available"
    ],
    "exercise_timing": {
      "acceptable": [
        "18:45-20:00"
      ],
      "avoid": [
        "after_20:30",
        "during_12:00-14:00"
      ],
      "preferred": [
        "06:30-08:00"
      ]
    },
    "nutrition_preferences": [
      "prefers high-protein, low-effort breakfasts",
      "values practical meal solutions over restrictive tracking",
      "enjoys Singaporean, Japanese, Mediterranean, Indian, and Vietnamese cuisine",
      "willing to cook/assemble at home up to 2x per week; prefers chef or no-prep otherwise",
      "does not want strict calorie counting"
    ],
    "session_length": {
      "weekday_max_minutes": 60,
      "weekend_max_minutes": 90
    },
    "training_preferences": [
      "prefers trainer-led and data-driven strength progressions",
      "needs knee-safe modifications for certain exercises",
      "accepts remote or app-based coaching during travel",
      "dislikes purely treadmill or monotonous cardio"
    ]
  },
  "profile_summary": "Marcus Tan is a driven, analytical Singapore-based CEO, managing technology and logistics teams across multiple Asia-Pacific hubs. With frequent travel and complex coordination demands, he values data-driven, low-friction routines designed to improve metabolic health, maintain functional strength, and optimize energy and sleep on the road\u2014with minimal decision fatigue.",
  "scheduling_rules": {
    "avoid_heavy_lower_body_after_flight_hours": 24,
    "avoid_high_intensity_after_poor_sleep": true,
    "compact_recurring_low_complexity_tasks_in_calendar": true,
    "default_time_granularity_minutes": 15,
    "max_high_load_activities_per_day": 1,
    "max_medium_or_high_load_activities_per_day": 2,
    "min_gap_between_fitness_sessions_hours": 6,
    "planning_months": 3,
    "planning_start_date": "2026-06-01",
    "poor_sleep_threshold_hours": 5.2,
    "prefer_morning_exercise": true,
    "weekday_session_limit_minutes": 60,
    "weekend_session_limit_minutes": 90
  },
  "timezone": "Asia/Singapore",
  "travel_windows": [
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Hong Kong",
      "end": "2026-06-25T20:00:00+08:00",
      "expected_facilities": [
        "hotel_gym",
        "hotel_pool",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no in-person trusted physio or lab",
        "restaurant meals dominant (2+ client dinners)",
        "some jetlag from travel over 3 hours"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Planned high-resource travel. Hotel gym and pool available; care coordination shifts mostly remote except chef-prepped meals.",
      "purpose": "Board and investor meetings",
      "start": "2026-06-19T10:00:00+08:00",
      "travel_id": "travel_hk_2026_06",
      "travel_type": "planned",
      "travel_window_id": "travel_hk_2026_06",
      "type": "planned"
    },
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Tokyo",
      "end": "2026-07-29T21:15:00+09:00",
      "expected_facilities": [
        "basic_hotel_gym",
        "walking_routes",
        "remote_consultation_supported"
      ],
      "limitations": [
        "hotel gym limited equipment",
        "unpredictable meal structure (several client events)",
        "remote-only provider support"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Moderate-resource travel. Meals partly chef-prepped, most fitness sessions require adaptation.",
      "purpose": "Extended board and client visit",
      "start": "2026-07-22T07:15:00+08:00",
      "travel_id": "travel_tokyo_2026_07",
      "travel_type": "planned",
      "travel_window_id": "travel_tokyo_2026_07",
      "type": "planned"
    },
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Jakarta",
      "end": "2026-08-16T21:00:00+07:00",
      "expected_facilities": [
        "hotel_room",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no usable hotel gym",
        "no chef or trusted local providers",
        "most meals restaurant-based",
        "increased work stress and energy drop"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Low-resource travel, mainly supports travel-compatible movement and remote check-ins. Designed to force substitutions and unscheduled support tasks.",
      "purpose": "Urgent client escalation",
      "start": "2026-08-13T06:00:00+08:00",
      "travel_id": "travel_jakarta_2026_08",
      "travel_type": "last_minute",
      "travel_window_id": "travel_jakarta_2026_08",
      "type": "last_minute"
    }
  ],
  "typical_work_hours": {
    "monday_to_friday": {
      "end": "18:30",
      "notes": "In-office core hours; occasional late investor or cross-region calls until 21:00.",
      "start": "08:30"
    },
    "saturday": {
      "end": "12:00",
      "notes": "Catch-up strategy, light work, or personal training/recovery.",
      "start": "09:30"
    },
    "sunday": {
      "end": null,
      "notes": "Reserved for family, meal planning, chef prep, and recovery.",
      "start": null
    }
  }
}
```

---

## resource_universe.json

```json
{
  "equipment": [
    {
      "availability_required": true,
      "display_name": "Home Dumbbells (5-15kg pairs)",
      "equipment_id": "eq_dumbbells_home",
      "equipment_type": "dumbbells_fixed",
      "location_ids": [
        "home"
      ],
      "notes": "Enables modified strength routines at home.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Mini Resistance Bands (portable)",
      "equipment_id": "eq_mini_band",
      "equipment_type": "mini_band_portable",
      "location_ids": [
        "gym",
        "home",
        "office",
        "travel_hotel"
      ],
      "notes": "For hotel/office mobility and knee-safe strength work. Often brought during travel.",
      "travel_compatible": true
    },
    {
      "availability_required": false,
      "display_name": "Yoga/Exercise Mat",
      "equipment_id": "eq_yoga_mat",
      "equipment_type": "mat_portable",
      "location_ids": [
        "gym",
        "home",
        "travel_hotel"
      ],
      "notes": "Facilitates stretching and recovery, including post-travel.",
      "travel_compatible": true
    },
    {
      "availability_required": false,
      "display_name": "Concept2 Rower (Gym)",
      "equipment_id": "eq_rower_gym",
      "equipment_type": "rower_fixed",
      "location_ids": [
        "gym"
      ],
      "notes": "Cardio conditioning option for knee-safe aerobic.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Selectorized Strength Machines",
      "equipment_id": "eq_strength_machines_gym",
      "equipment_type": "strength_machine_fixed",
      "location_ids": [
        "gym"
      ],
      "notes": "Supports safe, knee-modified resistance sessions.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Hotel Pool (Hong Kong)",
      "equipment_id": "eq_pool_hotel_hk",
      "equipment_type": "pool_fixed",
      "location_ids": [
        "travel_hotel"
      ],
      "notes": "Low-impact aerobic and recovery option during HK trip.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Basic Hotel Gym Equipment (Tokyo)",
      "equipment_id": "eq_basic_gym_hotel_tokyo",
      "equipment_type": "basic_gym_fixed",
      "location_ids": [
        "travel_hotel"
      ],
      "notes": "Limited hotel gym: free weights up to 10kg, treadmill, and mat.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Bodyweight/No Equipment",
      "equipment_id": "eq_bodyweight",
      "equipment_type": "bodyweight",
      "location_ids": [
        "gym",
        "home",
        "office",
        "travel_hotel"
      ],
      "notes": "Always available as fallback. Used for travel-adapted and flare-up recovery routines.",
      "travel_compatible": true
    },
    {
      "availability_required": true,
      "display_name": "Lab Collection Kit (Clinic/Lab)",
      "equipment_id": "eq_lab_kits",
      "equipment_type": "lab_kit_fixed",
      "location_ids": [
        "clinic",
        "lab"
      ],
      "notes": "Synthetic: used for all on-site lab draws.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Home Kitchen Prep Area",
      "equipment_id": "eq_kitchen_home",
      "equipment_type": "kitchen_fixed",
      "location_ids": [
        "home"
      ],
      "notes": "Chef and Marcus use for structured meal prep twice per week.",
      "travel_compatible": false
    }
  ],
  "locations": [
    {
      "available_equipment_ids": [
        "eq_lab_kits"
      ],
      "display_name": "Elyx Partner Clinic (Singapore)",
      "location_id": "clinic",
      "location_type": "clinic",
      "notes": "Clinic consults, in-person physician review, and lab draws.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_rower_gym",
        "eq_strength_machines_gym",
        "eq_yoga_mat"
      ],
      "display_name": "Preferred Gym (Singapore)",
      "location_id": "gym",
      "location_type": "gym",
      "notes": "Strength, aerobic, and trainer- or physio-led sessions. Most equipment available.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_dumbbells_home",
        "eq_kitchen_home",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "display_name": "Marcus's Home (Singapore)",
      "location_id": "home",
      "location_type": "home",
      "notes": "Primary training, chef prep, and recovery. Physio visits and remote consults available.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_lab_kits"
      ],
      "display_name": "Core Clinical Lab (Singapore)",
      "location_id": "lab",
      "location_type": "lab",
      "notes": "Primary location for baseline and periodic labs.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "display_name": "Marcus's Office (Singapore)",
      "location_id": "office",
      "location_type": "office",
      "notes": "Daytime work hours; short, low-complexity movement or remote consult only.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [],
      "display_name": "Structured Restaurant Meal",
      "location_id": "restaurant",
      "location_type": "restaurant",
      "notes": "Used for structured restaurant meals during normal Singapore weeks when chef-prepped or office delivery meals are unavailable.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [],
      "display_name": "Remote/Virtual",
      "location_id": "remote",
      "location_type": "remote",
      "notes": "Used for remote consults, telemedicine, or non-specific travel fallback.",
      "timezone": null,
      "travel_compatible": true
    },
    {
      "available_equipment_ids": [
        "eq_basic_gym_hotel_tokyo",
        "eq_bodyweight",
        "eq_mini_band",
        "eq_pool_hotel_hk",
        "eq_yoga_mat"
      ],
      "display_name": "Hotel (Hong Kong)",
      "location_id": "travel_hotel",
      "location_type": "travel_hotel",
      "notes": "High-resource travel: hotel gym and pool. Trainer, dietitian, and remote coach available by remote.; Moderate-resource travel: limited gym, mainly bodyweight and portable gear. Provider pool remote-only.; Low-resource travel: no gym, minimal equipment, remote only.",
      "timezone": "Asia/Hong_Kong",
      "travel_compatible": true
    }
  ],
  "providers": [
    {
      "care_context_supported": [
        "strength",
        "mobility",
        "aerobic",
        "travel_fitness",
        "post_travel_adaptation"
      ],
      "care_team_role": "performance_trainer",
      "continuity_scope": "Owns strength progression, aerobic training adaptations, and trainer-to-physio handoffs.",
      "credentials": [
        "CSCS",
        "corrective_exercise_specialist"
      ],
      "display_name": "Kai Tan",
      "handoff_partner_provider_ids": [
        "provider_physio_01",
        "provider_physician_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "gym",
        "home",
        "office",
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "in_person",
        "remote",
        "travel_adapted"
      ],
      "notes": "Specializes in data-driven strength and lower-body modified routines. Supports remote coaching and travel adaptation.",
      "provider_id": "provider_trainer_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "strength_and_conditioning",
        "knee_safe_training",
        "travel_fitness_adaptation"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "strength",
        "mobility",
        "knee_safe_training",
        "provider_unavailable_substitution"
      ],
      "care_team_role": "strength_coach",
      "continuity_scope": "Delivers gym-based strength sessions when the primary performance trainer is unavailable; follows Kai's progression plan.",
      "credentials": [
        "CSCS",
        "strength_and_power_coach"
      ],
      "display_name": "Amelia Wong",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "gym",
        "home",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Secondary strength coach for gym and home sessions; useful when Kai is unavailable or when extra strength coverage is needed.",
      "provider_id": "provider_strength_coach_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "gym_strength_progression",
        "resistance_training_technique",
        "knee_safe_loading"
      ],
      "team_group": "allied_health",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "travel_fitness",
        "hotel_gym_substitution",
        "bodyweight_conditioning",
        "equipment_unavailable_substitution"
      ],
      "care_team_role": "travel_trainer",
      "continuity_scope": "Delivers remote and hotel-gym substitutions during travel windows; keeps strength/cardio intent intact when facilities change.",
      "credentials": [
        "NASM-CPT",
        "travel_fitness_specialist"
      ],
      "display_name": "Ravi Patel",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "remote",
        "travel_adapted"
      ],
      "notes": "Travel trainer for hotel-gym and remote sessions when Marcus is away from Singapore or normal facilities are unavailable.",
      "provider_id": "provider_travel_trainer_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "hotel_gym_training",
        "bodyweight_conditioning",
        "remote_travel_adaptation"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "mobility",
        "pain_review",
        "post_travel_recovery"
      ],
      "care_team_role": "physiotherapist",
      "continuity_scope": "Owns pain escalation review, movement restrictions, and rehab-to-training progression.",
      "credentials": [
        "MSc Physiotherapy",
        "sports_rehabilitation"
      ],
      "display_name": "Daniel Koh",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physician_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "gym",
        "home",
        "office",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Knee and lower-back rehab focus. Coordinates handoff with trainer after pain or travel events.",
      "provider_id": "provider_physio_01",
      "provider_type": "physiotherapist",
      "remote_supported": true,
      "specialties": [
        "knee_pain_rehabilitation",
        "lower_back_resilience",
        "post_travel_mobility"
      ],
      "team_group": "allied_health",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "nutrition_review",
        "structured_meals",
        "travel_meal_adaptation"
      ],
      "care_team_role": "registered_dietitian",
      "continuity_scope": "Owns structured meal targets, restaurant/travel food strategy, and nutrition interpretation after labs or CGM review.",
      "credentials": [
        "registered_dietitian",
        "sports_nutrition_certificate"
      ],
      "display_name": "Priya Shah",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_chef_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "home",
        "office",
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Provides concise nutrition summaries and meal adaptation, especially for travel and restaurant-heavy weeks.",
      "provider_id": "provider_dietitian_01",
      "provider_type": "dietitian",
      "remote_supported": true,
      "specialties": [
        "metabolic_nutrition",
        "CGM_informed_meal_planning",
        "travel_restaurant_strategy"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "periodic_review",
        "lab_followup",
        "protocol_modification"
      ],
      "care_team_role": "lead_physician",
      "continuity_scope": "Owns clinical interpretation, preventive screening decisions, and escalation guidance for the Allied Health team.",
      "credentials": [
        "MBBS",
        "MRCGP",
        "preventive_medicine"
      ],
      "display_name": "Dr. Aisha Menon",
      "handoff_partner_provider_ids": [
        "provider_dietitian_01",
        "provider_physio_01",
        "provider_trainer_01",
        "provider_lab_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "office",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Concise review and preventive oversight for metabolic and fitness trending. Remote available during travel windows.",
      "provider_id": "provider_physician_01",
      "provider_type": "physician",
      "remote_supported": true,
      "specialties": [
        "preventive_cardiometabolic_medicine",
        "metabolic_risk_review",
        "clinical_protocol_governance"
      ],
      "team_group": "specialist_clinical",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "lab_draw",
        "preventive_screening"
      ],
      "care_team_role": "clinical_lab_partner",
      "continuity_scope": "Owns sample collection logistics and passes lab status to physician and dietitian.",
      "credentials": [
        "MOH_registered_lab_partner"
      ],
      "display_name": "Elyx Partner Lab - Singapore",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_dietitian_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "lab"
      ],
      "modalities_supported": [
        "on_site_lab"
      ],
      "notes": "Handles all synthetic baseline labs and periodic screening. Not available during travel or abroad.",
      "provider_id": "provider_lab_01",
      "provider_type": "phlebotomist",
      "remote_supported": false,
      "specialties": [
        "fasted_blood_draw",
        "preventive_biomarker_panel",
        "sample_coordination"
      ],
      "team_group": "clinical_operations",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "meal_prep",
        "nutrition_briefing"
      ],
      "care_team_role": "private_chef",
      "continuity_scope": "Executes dietitian meal briefs during non-travel periods; does not provide clinical advice.",
      "credentials": [
        "private_chef",
        "metabolic_meal_prep"
      ],
      "display_name": "Chef Liyang (Home/Local Meals)",
      "handoff_partner_provider_ids": [
        "provider_dietitian_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "home",
        "office"
      ],
      "modalities_supported": [
        "in_person",
        "prepped_dropoff"
      ],
      "notes": "Prepares metabolic-structured meals, up to 2 home-prepped sessions weekly; non-travel periods only.",
      "provider_id": "provider_chef_01",
      "provider_type": "chef",
      "remote_supported": false,
      "specialties": [
        "high_protein_meal_prep",
        "office_meal_delivery",
        "dietitian_brief_execution"
      ],
      "team_group": "lifestyle_support",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "adherence_support",
        "recovery_checkin",
        "routine_travel_fallback"
      ],
      "care_team_role": "health_coach",
      "continuity_scope": "Owns weekly behavior coaching, friction resolution, missed-session follow-up, and care-team coordination prompts.",
      "credentials": [
        "NBC-HWC",
        "behavior_change_coaching"
      ],
      "display_name": "Maya Rao",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_dietitian_01",
        "provider_physio_01",
        "provider_trainer_01"
      ],
      "location_ids": [
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "remote"
      ],
      "notes": "Remote pool supports check-ins, fatigue/mobility logs, travel substitutions, and care-team continuity.",
      "provider_id": "provider_remote_coach_01",
      "provider_type": "remote_coach_pool",
      "remote_supported": true,
      "specialties": [
        "behavior_coaching",
        "adherence_barrier_resolution",
        "travel_friction_planning"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    }
  ],
  "travel_time_rules": [
    {
      "from_location_id": "home",
      "minutes": 25,
      "to_location_id": "restaurant"
    },
    {
      "from_location_id": "restaurant",
      "minutes": 25,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 25,
      "to_location_id": "gym"
    },
    {
      "from_location_id": "gym",
      "minutes": 25,
      "to_location_id": "home"
    },
    {
      "from_location_id": "office",
      "minutes": 40,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 40,
      "to_location_id": "office"
    },
    {
      "from_location_id": "office",
      "minutes": 15,
      "to_location_id": "gym"
    },
    {
      "from_location_id": "gym",
      "minutes": 15,
      "to_location_id": "office"
    },
    {
      "from_location_id": "clinic",
      "minutes": 30,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 30,
      "to_location_id": "clinic"
    },
    {
      "from_location_id": "lab",
      "minutes": 30,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 30,
      "to_location_id": "lab"
    }
  ],
  "travel_windows": [
    {
      "arrival_fatigue_risk": "moderate",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Hong Kong)",
      "end": "2026-06-25T20:00:00+08:00",
      "estimated_travel_duration_hours": 4,
      "member_location_override": "travel_hotel",
      "notes": "Planned high-resource travel. Hotel gym and pool available; care coordination shifts mostly remote except chef-prepped meals.",
      "origin_location_id": "home",
      "start": "2026-06-19T10:00:00+08:00",
      "travel_type": "planned",
      "travel_window_id": "travel_hk_2026_06"
    },
    {
      "arrival_fatigue_risk": "moderate",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Tokyo)",
      "end": "2026-07-29T21:15:00+09:00",
      "estimated_travel_duration_hours": 6.5,
      "member_location_override": "travel_hotel",
      "notes": "Moderate-resource travel. Meals partly chef-prepped, most fitness sessions require adaptation.",
      "origin_location_id": "home",
      "start": "2026-07-22T07:15:00+08:00",
      "travel_type": "planned",
      "travel_window_id": "travel_tokyo_2026_07"
    },
    {
      "arrival_fatigue_risk": "high",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Jakarta)",
      "end": "2026-08-16T21:00:00+07:00",
      "estimated_travel_duration_hours": 2,
      "member_location_override": "travel_hotel",
      "notes": "Low-resource travel, mainly supports travel-compatible movement and remote check-ins. Designed to force substitutions and unscheduled support tasks.",
      "origin_location_id": "home",
      "start": "2026-08-13T06:00:00+08:00",
      "travel_type": "last_minute",
      "travel_window_id": "travel_jakarta_2026_08"
    }
  ]
}
```

---

## known_frictions.json

```json
{
  "frictions": [
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06"
      ],
      "date_range": {
        "end": "2026-06-25T20:00:00+08:00",
        "start": "2026-06-19T10:00:00+08:00"
      },
      "description": "During the planned Hong Kong travel window, Marcus has access to a well-equipped hotel gym and pool, enabling most fitness routines. However, there is no in-person trusted physio or lab access, and most provider support is remote. Restaurant meals dominate, with only limited chef-prepped options.",
      "friction_id": "friction_planned_travel_better_facilities_001",
      "name": "Planned Travel with Enhanced Facilities",
      "scheduler_expectation": "Scheduler should prioritize hotel gym/pool for fitness, adapt meal planning to restaurant-heavy context, and route all provider consults to remote. In-person labs and physio sessions should not be scheduled during this window."
    },
    {
      "affected_travel_window_ids": [
        "travel_jakarta_2026_08"
      ],
      "date_range": {
        "end": "2026-08-16T21:00:00+07:00",
        "start": "2026-08-13T06:00:00+08:00"
      },
      "description": "During the urgent Jakarta trip, Marcus only has access to his hotel room and remote support. There is no usable hotel gym, no chef or trusted local providers, and most meals are restaurant-based. Increased work stress and energy drop are expected.",
      "friction_id": "friction_last_minute_travel_limited_facilities_001",
      "name": "Last-Minute Travel with Limited Facilities",
      "scheduler_expectation": "Scheduler should substitute all fitness with bodyweight or portable-band routines, rely on remote coach/dietitian, and expect some activities to be unscheduled or substituted. Structured meal adherence may drop; chef-prepped meals are unavailable."
    },
    {
      "date_range": null,
      "description": "Marcus prefers early morning or early evening sessions for fitness and consultations. However, the Elyx Performance Trainer and Physiotherapist have limited early morning slots, and the Dietitian and Physician are only available during office hours. This causes conflicts with Marcus's preferred exercise and review times.",
      "friction_id": "friction_provider_availability_mismatch_001",
      "linked_resource_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_dietitian_01",
        "provider_physician_01"
      ],
      "name": "Provider Availability Mismatch with Member Preferences",
      "scheduler_expectation": "Scheduler may need to schedule some sessions outside Marcus's preferred windows or delay/reschedule certain provider-led activities. Expect some member-preferred slots to be unavailable."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Lab draws and in-person physician reviews are only possible at the Singapore clinic or lab. During all travel windows, these services are unavailable. Remote consults are possible, but labs must be rescheduled.",
      "friction_id": "friction_lab_consult_disruption_travel_001",
      "linked_resource_ids": [
        "provider_lab_01",
        "provider_physician_01",
        "clinic",
        "lab"
      ],
      "name": "Lab or Consultation Disruption During Travel",
      "scheduler_expectation": "Scheduler should avoid scheduling lab draws or in-person physician reviews during travel. If due, these should be rescheduled before or after travel, or substituted with remote consults where possible."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Structured metabolic meals require either chef-prep at home/office or Marcus to assemble meals himself (up to 2x per week). During travel, chef-prepped meals are unavailable, and Marcus is unwilling to do meal prep in hotel settings.",
      "friction_id": "friction_food_prep_dependency_001",
      "linked_resource_ids": [
        "provider_chef_01",
        "eq_kitchen_home",
        "home",
        "office"
      ],
      "name": "Food Prep Dependency on Chef or Member",
      "scheduler_expectation": "Scheduler should only schedule chef-prepped or member-assembled structured meals at home/office, and use restaurant or travel-compatible meal options during travel. Some structured meal targets may be missed during travel."
    },
    {
      "affected_travel_window_ids": [
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Certain equipment (e.g., strength machines, rower) and facilities (e.g., gym, pool) are only available at home or gym locations. During the Tokyo trip, the hotel gym has only basic equipment. During Jakarta travel, there is no usable gym at all.",
      "friction_id": "friction_equipment_facility_unavailability_001",
      "linked_resource_ids": [
        "eq_strength_machines_gym",
        "eq_rower_gym",
        "eq_basic_gym_hotel_tokyo",
        "eq_pool_hotel_hk",
        "gym",
        "travel_hotel"
      ],
      "name": "Equipment or Facility Unavailability",
      "scheduler_expectation": "Scheduler should substitute unavailable equipment with bodyweight or portable-band routines during travel, and avoid scheduling equipment-dependent activities in locations where the equipment is not present."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07"
      ],
      "date_range": null,
      "description": "After travel windows involving flights over 3 hours (e.g., Singapore to Hong Kong or Tokyo), Marcus experiences moderate fatigue and lower-back tightness. High-load or lower-body training should be avoided for 24 hours post-arrival.",
      "friction_id": "friction_post_travel_fatigue_001",
      "name": "Post-Travel Fatigue After Location Change Over 3 Hours",
      "scheduler_expectation": "Scheduler should avoid scheduling high-load or heavy lower-body activities for 24 hours after arrival, and instead prioritize mobility, stretching, or recovery sessions."
    },
    {
      "date_range": null,
      "description": "If Marcus skips or substitutes a high-load strength or aerobic session (especially after travel or during pain escalation), the plan should automatically schedule a recovery or mobility session and flag for care-team follow-up.",
      "friction_id": "friction_skipped_high_load_recovery_adjustment_001",
      "linked_resource_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "name": "Skipped or Substituted High-Load Activity Requiring Recovery Adjustment",
      "scheduler_expectation": "Scheduler should detect skipped or substituted high-load activities and insert appropriate recovery/mobility sessions, possibly triggering a remote coach or physio check-in."
    }
  ]
}
```

---

## activity_families.json

```json
{
  "activity_families": [
    {
      "activity_family_id": "b01_nutrition_breakfast_chef_home",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 5,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Covers core structured breakfast at home with chef prep or low-prep fallback.",
        "Substitution counts toward weekly meal target if chef prep is unavailable.",
        "If a fasting lab draw is scheduled before breakfast, replace breakfast with act_b01_breakfast_skip_for_fasting_lab and record the skip reason."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "metabolic_health"
      ],
      "intent": "breakfast",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_breakfast_chef_home",
        "activity_id": "act_b01_breakfast_chef_home_primary",
        "activity_type": "food",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "current dietary preference",
          "protein target"
        ],
        "dependencies": [],
        "details": "Breakfast at home, chef-prepped or prepped in advance. High-protein, low-effort, tailored to metabolic goals. Chef Liyang prepares up to 2x/week; other days use prepped or low-prep options.",
        "dining_source": "home",
        "duration_minutes": 20,
        "facilitator_type": "chef",
        "fasting_lab_scheduling_constraint": {
          "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
          "calendar_skip_reason_required": true,
          "do_not_schedule_before_fasting_lab_same_day": true,
          "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "skip_reason_code": "fasting_lab_same_morning"
        },
        "food_provider_id": "provider_chef_01",
        "frequency": {
          "count": 5,
          "preferred_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday"
          ],
          "preferred_time_windows": [
            "06:30-08:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Directly supports weekly structured meal goal as home chef-prepped breakfast.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "structured_meal",
          "breakfast",
          "metabolic_health"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "home",
          "facilitator_type": "chef",
          "meal_slot": "breakfast",
          "prep_source": "chef_prepped"
        },
        "meal_slot": "breakfast",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings",
          "post_meal_energy"
        ],
        "prep_required": false,
        "prep_source": "chef_prepped",
        "priority": 10,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_kitchen_home"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": {
          "allowed_for_fasting_lab": true,
          "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
          "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
        },
        "substitution_activity_ids": [
          "act_b01_breakfast_home_lowprep",
          "act_b01_breakfast_skip_for_fasting_lab"
        ],
        "title": "Chef-prepared high-protein breakfast",
        "weekly_primary_cap": 4
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_breakfast_chef_home",
          "activity_id": "act_b01_breakfast_home_lowprep",
          "activity_type": "food",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "protein target"
          ],
          "dependencies": [],
          "details": "Member assembles a high-protein breakfast (e.g., Greek yogurt, eggs, fruit, nuts) when chef prep is unavailable or time is limited.",
          "dining_source": "home",
          "duration_minutes": 10,
          "facilitator_type": "member",
          "fasting_lab_scheduling_constraint": {
            "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
            "calendar_skip_reason_required": true,
            "do_not_schedule_before_fasting_lab_same_day": true,
            "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
            "skip_reason_code": "fasting_lab_same_morning"
          },
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "06:30-08:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts as structured meal if chef unavailable; preserves high-protein, low-effort intent.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "structured_meal",
            "breakfast",
            "metabolic_health"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "home",
            "facilitator_type": "member",
            "meal_slot": "breakfast",
            "prep_source": "member_assembled"
          },
          "meal_slot": "breakfast",
          "metrics_to_collect": [
            "meal_completion",
            "protein_servings"
          ],
          "prep_required": false,
          "prep_source": "member_assembled",
          "priority": 20,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_kitchen_home"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_for_fasting_lab": true,
            "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
            "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_breakfast_chef_home_primary",
          "substitution_notes": "Preserves structured, high-protein breakfast intent when chef prep is unavailable or time is limited.",
          "substitution_reason_codes": [
            "prep_unavailable",
            "time_conflict"
          ],
          "title": "Low-prep high-protein breakfast at home",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_breakfast_home_lowprep",
          "reason": "Allows structured breakfast completion when chef prep is not feasible or time is constrained.",
          "when": "chef unavailable or member has early meeting"
        },
        {
          "prefer_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "reason": "Breakfast would break the 8-hour fasting requirement for same-morning metabolic labs.",
          "when": "fasting lab draw is scheduled before breakfast on the same day"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_office_delivery",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Backup for breakfast when at office early or home prep unavailable.",
        "Does not count toward core meal target unless explicitly scheduled as a structured meal.",
        "If a fasting lab draw is scheduled before breakfast, replace breakfast with act_b01_breakfast_skip_for_fasting_lab and record the skip reason.",
        "On WFH dates, do not schedule office-location meals; use home fallback or reject with wfh_no_office_location_activity."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "office",
        "support"
      ],
      "intent": "breakfast",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_breakfast_office_delivery",
        "activity_id": "act_b01_breakfast_office_delivery_primary",
        "activity_type": "food",
        "allowed_locations": [
          "office"
        ],
        "care_context_required": [
          "office schedule"
        ],
        "delivery_source": "office_delivery",
        "dependencies": [],
        "details": "Breakfast delivered to office for early workdays or when home prep is not possible. Chef-prepped or office delivery, high-protein and low-effort.",
        "dining_source": "office",
        "duration_minutes": 10,
        "facilitator_type": "chef",
        "fasting_lab_scheduling_constraint": {
          "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
          "calendar_skip_reason_required": true,
          "do_not_schedule_before_fasting_lab_same_day": true,
          "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "skip_reason_code": "fasting_lab_same_morning"
        },
        "food_provider_id": "provider_chef_01",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "08:30-09:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Support-only; does not count unless explicitly scheduled as structured meal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "breakfast",
          "office",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "office",
          "facilitator_type": "chef",
          "meal_slot": "breakfast",
          "prep_source": "chef_prepped"
        },
        "meal_slot": "breakfast",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings"
        ],
        "prep_required": false,
        "prep_source": "chef_prepped",
        "priority": 40,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": {
          "allowed_for_fasting_lab": true,
          "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
          "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
        },
        "substitution_activity_ids": [
          "act_b01_breakfast_office_member_assembled",
          "act_b01_breakfast_skip_for_fasting_lab",
          "act_b01_breakfast_home_lowprep"
        ],
        "title": "Office-delivered breakfast",
        "wfh_scheduling_constraint": {
          "calendar_rejection_reason_required_if_no_substitution": true,
          "on_member_location_home_day": "do_not_schedule_office_location",
          "preferred_substitution_activity_id": "act_b01_breakfast_home_lowprep",
          "rejection_reason_code": "wfh_no_office_location_activity"
        }
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_breakfast_office_delivery",
          "activity_id": "act_b01_breakfast_office_member_assembled",
          "activity_type": "food",
          "allowed_locations": [
            "office"
          ],
          "care_context_required": [
            "office schedule"
          ],
          "delivery_source": "none",
          "dependencies": [],
          "details": "Member assembles a simple high-protein breakfast at office (e.g., protein shake, nuts, fruit) if delivery is unavailable.",
          "dining_source": "office",
          "duration_minutes": 10,
          "facilitator_type": "member",
          "fasting_lab_scheduling_constraint": {
            "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
            "calendar_skip_reason_required": true,
            "do_not_schedule_before_fasting_lab_same_day": true,
            "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
            "skip_reason_code": "fasting_lab_same_morning"
          },
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "08:30-09:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Support-only; member-assembled office breakfast if delivery fails.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "breakfast",
            "office",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "office",
            "facilitator_type": "member",
            "meal_slot": "breakfast",
            "prep_source": "member_assembled",
            "structured_meal": true
          },
          "meal_slot": "breakfast",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "member_assembled",
          "priority": 50,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_for_fasting_lab": true,
            "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
            "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_breakfast_office_delivery_primary",
          "substitution_notes": "Preserves breakfast intent at office when delivery is unavailable or time is limited.",
          "substitution_reason_codes": [
            "prep_unavailable",
            "time_conflict"
          ],
          "title": "Simple high-protein breakfast at office"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_breakfast_office_member_assembled",
          "reason": "Allows member to still complete a breakfast at office when delivery fails or is delayed.",
          "when": "office delivery unavailable or member arrives before delivery window"
        },
        {
          "prefer_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "reason": "Breakfast would break the 8-hour fasting requirement for same-morning metabolic labs.",
          "when": "fasting lab draw is scheduled before breakfast on the same day"
        },
        {
          "prefer_activity_id": "act_b01_breakfast_home_lowprep",
          "reason": "WFH day makes office-location meal invalid; use home meal fallback instead.",
          "when": "member_location override is home or WFH day is active"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Travel hotel breakfast (buffet or room service) as substitution for structured home breakfast.",
        "Does not add to normal-week denominator; supports travel continuity.",
        "If a fasting lab draw is scheduled before breakfast, replace breakfast with act_b01_breakfast_skip_for_fasting_lab and record the skip reason."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "travel",
        "support"
      ],
      "intent": "breakfast",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
        "activity_id": "act_b01_breakfast_travel_hotel_primary",
        "activity_type": "food",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "dietitian guidance"
        ],
        "dependencies": [],
        "details": "Breakfast at hotel buffet or via room service during travel. Focus on protein and fiber; chef prep unavailable.",
        "dining_source": "hotel_buffet",
        "duration_minutes": 15,
        "facilitator_type": "member",
        "fasting_lab_scheduling_constraint": {
          "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
          "calendar_skip_reason_required": true,
          "do_not_schedule_before_fasting_lab_same_day": true,
          "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "skip_reason_code": "fasting_lab_same_morning"
        },
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "07:00-09:00"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Travel hotel breakfast as substitution for structured home breakfast; does not count toward normal-week denominator.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "breakfast",
          "travel",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "hotel_buffet",
          "facilitator_type": "member",
          "meal_slot": "breakfast",
          "prep_source": "none"
        },
        "meal_slot": "breakfast",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings"
        ],
        "prep_required": false,
        "prep_source": "none",
        "priority": 60,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": {
          "allowed_for_fasting_lab": true,
          "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
          "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
        },
        "substitution_activity_ids": [
          "act_b01_breakfast_travel_hotel_restaurant",
          "act_b01_breakfast_skip_for_fasting_lab"
        ],
        "title": "Hotel buffet or room-service breakfast (travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
          "activity_id": "act_b01_breakfast_travel_hotel_restaurant",
          "activity_type": "food",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window"
          ],
          "dependencies": [],
          "details": "Breakfast at a local restaurant when hotel buffet or room service is unavailable during travel.",
          "dining_source": "restaurant",
          "duration_minutes": 15,
          "facilitator_type": "member",
          "fasting_lab_scheduling_constraint": {
            "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
            "calendar_skip_reason_required": true,
            "do_not_schedule_before_fasting_lab_same_day": true,
            "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
            "skip_reason_code": "fasting_lab_same_morning"
          },
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "07:00-09:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Restaurant breakfast during travel; does not count toward normal-week denominator.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "breakfast",
            "travel",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "restaurant",
            "facilitator_type": "member",
            "meal_slot": "breakfast",
            "prep_source": "none"
          },
          "meal_slot": "breakfast",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 70,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_for_fasting_lab": true,
            "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
            "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_breakfast_travel_hotel_primary",
          "substitution_notes": "Preserves travel breakfast intent when hotel buffet or room service is unavailable.",
          "substitution_reason_codes": [
            "travel_window",
            "prep_unavailable"
          ],
          "title": "Restaurant breakfast (travel)",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_breakfast_travel_hotel_restaurant",
          "reason": "Allows Marcus to complete breakfast during travel when hotel options are not available.",
          "when": "hotel buffet or room service unavailable during travel"
        },
        {
          "prefer_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "reason": "Breakfast would break the 8-hour fasting requirement for same-morning metabolic labs.",
          "when": "fasting lab draw is scheduled before breakfast on the same day"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_lunch_office_delivery",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 5,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Covers core structured lunch via office delivery or chef-prepped packed meal.",
        "Substitution counts toward weekly meal target if chef or delivery is unavailable.",
        "On WFH dates, do not schedule office-location meals; use home fallback or reject with wfh_no_office_location_activity."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "office",
        "metabolic_health"
      ],
      "intent": "lunch",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_lunch_office_delivery",
        "activity_id": "act_b01_lunch_office_delivery_primary",
        "activity_type": "food",
        "allowed_locations": [
          "office"
        ],
        "care_context_required": [
          "office schedule",
          "protein target"
        ],
        "delivery_source": "office_delivery",
        "dependencies": [],
        "details": "Lunch at office, delivered or packed by chef. High-protein, balanced, and easy to eat during work blocks.",
        "dining_source": "office",
        "duration_minutes": 25,
        "facilitator_type": "chef",
        "food_provider_id": "provider_chef_01",
        "frequency": {
          "count": 5,
          "preferred_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday"
          ],
          "preferred_time_windows": [
            "12:00-13:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Directly supports structured meal goal as office lunch.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "structured_meal",
          "lunch",
          "office",
          "metabolic_health"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "office",
          "facilitator_type": "chef",
          "meal_slot": "lunch",
          "prep_source": "chef_prepped"
        },
        "meal_slot": "lunch",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings",
          "fiber_servings"
        ],
        "prep_required": false,
        "prep_source": "chef_prepped",
        "priority": 15,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_lunch_office_member_assembled",
          "act_b01_lunch_member_assembled_home_primary"
        ],
        "title": "Chef-prepped or delivered office lunch",
        "weekly_primary_cap": 4,
        "wfh_scheduling_constraint": {
          "calendar_rejection_reason_required_if_no_substitution": true,
          "on_member_location_home_day": "do_not_schedule_office_location",
          "preferred_substitution_activity_id": "act_b01_lunch_member_assembled_home_primary",
          "rejection_reason_code": "wfh_no_office_location_activity"
        }
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_lunch_office_delivery",
          "activity_id": "act_b01_lunch_office_member_assembled",
          "activity_type": "food",
          "allowed_locations": [
            "office"
          ],
          "care_context_required": [
            "office schedule"
          ],
          "delivery_source": "none",
          "dependencies": [],
          "details": "Member assembles a high-protein, balanced lunch at office (e.g., protein bowl, salad, pre-packed meal) if chef or delivery is unavailable.",
          "dining_source": "office",
          "duration_minutes": 15,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "12:00-13:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts as structured meal if chef or delivery is unavailable and member assembles lunch at office.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "structured_meal",
            "lunch",
            "office",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "office",
            "facilitator_type": "member",
            "meal_slot": "lunch",
            "prep_source": "member_assembled",
            "structured_meal": true
          },
          "meal_slot": "lunch",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "member_assembled",
          "priority": 25,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_lunch_office_delivery_primary",
          "substitution_notes": "Preserves structured lunch intent at office when chef or delivery is unavailable.",
          "substitution_reason_codes": [
            "prep_unavailable",
            "time_conflict"
          ],
          "title": "Balanced office lunch bowl",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_lunch_office_member_assembled",
          "reason": "Allows Marcus to complete a structured lunch at office when chef or delivery is unavailable.",
          "when": "chef or office delivery unavailable or time-constrained"
        },
        {
          "prefer_activity_id": "act_b01_lunch_member_assembled_home_primary",
          "reason": "WFH day makes office-location meal invalid; use home meal fallback instead.",
          "when": "member_location override is home or WFH day is active"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Travel lunch via restaurant or hotel meal as substitution for structured office lunch.",
        "Does not count toward normal-week denominator; supports travel continuity."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "travel",
        "support"
      ],
      "intent": "lunch",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
        "activity_id": "act_b01_lunch_restaurant_travel_primary",
        "activity_type": "food",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "dietitian guidance"
        ],
        "dependencies": [],
        "details": "Lunch at restaurant or hotel during travel. Focus on protein and fiber; chef prep and office delivery unavailable.",
        "dining_source": "restaurant",
        "duration_minutes": 30,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "12:00-13:30"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Travel lunch as substitution for structured office lunch; does not count toward normal-week denominator.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "lunch",
          "travel",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "restaurant",
          "facilitator_type": "member",
          "meal_slot": "lunch",
          "prep_source": "none"
        },
        "meal_slot": "lunch",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings"
        ],
        "prep_required": false,
        "prep_source": "none",
        "priority": 65,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_lunch_travel_room_service"
        ],
        "title": "Restaurant or hotel lunch (travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
          "activity_id": "act_b01_lunch_travel_room_service",
          "activity_type": "food",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window"
          ],
          "dependencies": [],
          "details": "Lunch via hotel room service when restaurant is not feasible during travel.",
          "dining_source": "room_service",
          "duration_minutes": 25,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "12:00-13:30"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Room-service lunch during travel; does not count toward normal-week denominator.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "lunch",
            "travel",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "room_service",
            "facilitator_type": "member",
            "meal_slot": "lunch",
            "prep_source": "none"
          },
          "meal_slot": "lunch",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 75,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_lunch_restaurant_travel_primary",
          "substitution_notes": "Preserves travel lunch intent when restaurant is not feasible.",
          "substitution_reason_codes": [
            "travel_window",
            "prep_unavailable"
          ],
          "title": "Room-service lunch (travel)",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_lunch_travel_room_service",
          "reason": "Allows Marcus to complete lunch during travel when restaurant is not an option.",
          "when": "restaurant lunch not feasible during travel (e.g., time or location constraint)"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Member-assembled lunch at home as fallback if chef or delivery unavailable.",
        "Does not count unless explicitly scheduled as structured meal."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "home",
        "support"
      ],
      "intent": "lunch",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
        "activity_id": "act_b01_lunch_member_assembled_home_primary",
        "activity_type": "food",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "home schedule"
        ],
        "dependencies": [],
        "details": "Member assembles a high-protein, balanced lunch at home (e.g., salad, grain bowl, leftovers) if chef prep or office delivery is unavailable.",
        "dining_source": "home",
        "duration_minutes": 15,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "12:00-13:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Member-assembled lunch at home as fallback; does not count unless explicitly scheduled as structured meal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "lunch",
          "home",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "home",
          "facilitator_type": "member",
          "meal_slot": "lunch",
          "prep_source": "member_assembled",
          "structured_meal": true
        },
        "meal_slot": "lunch",
        "metrics_to_collect": [
          "meal_completion"
        ],
        "prep_required": false,
        "prep_source": "member_assembled",
        "priority": 55,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_kitchen_home"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_lunch_home_no_prep"
        ],
        "title": "Simple high-protein lunch at home"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
          "activity_id": "act_b01_lunch_home_no_prep",
          "activity_type": "food",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "home schedule"
          ],
          "dependencies": [],
          "details": "Quick, no-prep lunch at home (e.g., protein shake, pre-packed meal) if member assembly is not feasible.",
          "dining_source": "home",
          "duration_minutes": 5,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "12:00-13:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "No-prep lunch at home (e.g., protein shake, pre-packed meal) if member assembly is not feasible.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "lunch",
            "home",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "home",
            "facilitator_type": "member",
            "meal_slot": "lunch",
            "prep_source": "none",
            "structured_meal": true
          },
          "meal_slot": "lunch",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 65,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_lunch_member_assembled_home_primary",
          "substitution_notes": "Preserves lunch intent at home when member assembly is not feasible.",
          "substitution_reason_codes": [
            "prep_unavailable"
          ],
          "title": "Quick protein lunch at home"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_lunch_home_no_prep",
          "reason": "Allows Marcus to complete lunch at home when member assembly is not feasible.",
          "when": "member unable to assemble lunch at home (e.g., time constraint)"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_dinner_chef_home",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 4,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Covers core structured dinner at home with chef prep.",
        "Substitution counts toward weekly meal target if chef unavailable."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "home",
        "metabolic_health"
      ],
      "intent": "dinner",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_dinner_chef_home",
        "activity_id": "act_b01_dinner_chef_home_primary",
        "activity_type": "food",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "current dietary preference",
          "protein target"
        ],
        "dependencies": [],
        "details": "Dinner at home, chef-prepped. Balanced, high-protein, and tailored to metabolic goals. Chef Liyang prepares up to 2x/week; other days use prepped or low-prep options.",
        "dining_source": "home",
        "duration_minutes": 40,
        "facilitator_type": "chef",
        "food_provider_id": "provider_chef_01",
        "frequency": {
          "count": 4,
          "preferred_days": [
            "monday",
            "tuesday",
            "wednesday",
            "sunday"
          ],
          "preferred_time_windows": [
            "19:00-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Directly supports structured meal goal as home chef-prepped dinner.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "structured_meal",
          "dinner",
          "home",
          "metabolic_health"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "home",
          "facilitator_type": "chef",
          "meal_slot": "dinner",
          "prep_source": "chef_prepped"
        },
        "meal_slot": "dinner",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings",
          "fiber_servings"
        ],
        "prep_required": false,
        "prep_source": "chef_prepped",
        "priority": 20,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_kitchen_home"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_dinner_home_restaurant"
        ],
        "title": "Chef-prepared dinner at home",
        "weekly_primary_cap": 3
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_dinner_chef_home",
          "activity_id": "act_b01_dinner_home_restaurant",
          "activity_type": "food",
          "allowed_locations": [
            "restaurant"
          ],
          "care_context_required": [
            "dining out context"
          ],
          "dependencies": [],
          "details": "Dinner at a structured restaurant when chef prep is unavailable or client dinner is required. Focus on protein, fiber, and metabolic balance.",
          "dining_source": "restaurant",
          "duration_minutes": 60,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "19:00-20:30"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts as structured meal if chef prep is unavailable and Marcus dines at a structured restaurant.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "structured_meal",
            "dinner",
            "home",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "restaurant",
            "facilitator_type": "member",
            "meal_slot": "dinner",
            "prep_source": "none",
            "structured_meal": true
          },
          "meal_slot": "dinner",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 30,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_dinner_chef_home_primary",
          "substitution_notes": "Preserves structured dinner intent when chef prep is unavailable or client dinner is required.",
          "substitution_reason_codes": [
            "prep_unavailable",
            "time_conflict"
          ],
          "title": "Balanced restaurant dinner",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_dinner_home_restaurant",
          "reason": "Allows Marcus to complete a structured dinner when chef prep is not feasible.",
          "when": "chef unavailable or client dinner required"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_dinner_restaurant",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Structured restaurant dinner as fallback if chef prep unavailable or client dinner required.",
        "Does not count unless explicitly scheduled as structured meal."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "restaurant",
        "support"
      ],
      "intent": "dinner",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_dinner_restaurant",
        "activity_id": "act_b01_dinner_restaurant_primary",
        "activity_type": "food",
        "allowed_locations": [
          "restaurant"
        ],
        "care_context_required": [
          "dining out context"
        ],
        "dependencies": [],
        "details": "Dinner at a structured restaurant when chef prep is unavailable or client dinner is required. Focus on protein, fiber, and metabolic balance.",
        "dining_source": "restaurant",
        "duration_minutes": 60,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "19:00-20:30"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Structured restaurant dinner as fallback; does not count unless explicitly scheduled as structured meal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "dinner",
          "restaurant",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "restaurant",
          "facilitator_type": "member",
          "meal_slot": "dinner",
          "prep_source": "none",
          "structured_meal": true
        },
        "meal_slot": "dinner",
        "metrics_to_collect": [
          "meal_completion"
        ],
        "prep_required": false,
        "prep_source": "none",
        "priority": 45,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_dinner_restaurant_no_prep"
        ],
        "title": "Balanced restaurant dinner"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_dinner_restaurant",
          "activity_id": "act_b01_dinner_restaurant_no_prep",
          "activity_type": "food",
          "allowed_locations": [
            "restaurant"
          ],
          "care_context_required": [
            "dining out context"
          ],
          "dependencies": [],
          "details": "Quick, no-prep dinner at restaurant (e.g., set menu or pre-ordered) if time is limited.",
          "dining_source": "restaurant",
          "duration_minutes": 45,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "19:00-20:30"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "No-prep dinner at restaurant (e.g., set menu or pre-ordered) if time is limited.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "dinner",
            "restaurant",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "restaurant",
            "facilitator_type": "member",
            "meal_slot": "dinner",
            "prep_source": "none",
            "structured_meal": true
          },
          "meal_slot": "dinner",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 55,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_dinner_restaurant_primary",
          "substitution_notes": "Preserves dinner intent at restaurant when time is limited.",
          "substitution_reason_codes": [
            "prep_unavailable",
            "time_conflict"
          ],
          "title": "Quick restaurant dinner"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_dinner_restaurant_no_prep",
          "reason": "Allows Marcus to complete dinner at restaurant when time is limited.",
          "when": "time is limited or set menu is required at restaurant"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_dinner_travel_hotel",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Travel dinner via restaurant or hotel meal as substitution for structured home dinner.",
        "Does not count toward normal-week denominator; supports travel continuity."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "travel",
        "support"
      ],
      "intent": "dinner",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_dinner_travel_hotel",
        "activity_id": "act_b01_dinner_travel_hotel_primary",
        "activity_type": "food",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "dietitian guidance"
        ],
        "dependencies": [],
        "details": "Dinner at hotel restaurant or via room service during travel. Focus on protein and metabolic balance; chef prep unavailable.",
        "dining_source": "restaurant",
        "duration_minutes": 45,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "19:00-20:30"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Travel dinner as substitution for structured home dinner; does not count toward normal-week denominator.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "structured_meal",
          "dinner",
          "travel",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": "restaurant",
          "facilitator_type": "member",
          "meal_slot": "dinner",
          "prep_source": "none"
        },
        "meal_slot": "dinner",
        "metrics_to_collect": [
          "meal_completion",
          "protein_servings"
        ],
        "prep_required": false,
        "prep_source": "none",
        "priority": 70,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_dinner_travel_room_service"
        ],
        "title": "Hotel or restaurant dinner (travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_dinner_travel_hotel",
          "activity_id": "act_b01_dinner_travel_room_service",
          "activity_type": "food",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window"
          ],
          "dependencies": [],
          "details": "Dinner via hotel room service when restaurant is not feasible during travel.",
          "dining_source": "room_service",
          "duration_minutes": 40,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "19:00-20:30"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Room-service dinner during travel; does not count toward normal-week denominator.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "structured_meal",
            "dinner",
            "travel",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": "room_service",
            "facilitator_type": "member",
            "meal_slot": "dinner",
            "prep_source": "none"
          },
          "meal_slot": "dinner",
          "metrics_to_collect": [
            "meal_completion"
          ],
          "prep_required": false,
          "prep_source": "none",
          "priority": 80,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_dinner_travel_hotel_primary",
          "substitution_notes": "Preserves travel dinner intent when restaurant is not feasible.",
          "substitution_reason_codes": [
            "travel_window",
            "prep_unavailable"
          ],
          "title": "Room-service dinner (travel)",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_dinner_travel_room_service",
          "reason": "Allows Marcus to complete dinner during travel when restaurant is not an option.",
          "when": "restaurant dinner not feasible during travel (e.g., late arrival, location constraint)"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_structured_meals_weekly",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "meals"
      },
      "family_validation_notes": [
        "Supports meal timing and structure around fasting labs.",
        "Does not count as a meal; only supports meal scheduling logic.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Fasting lab days must produce an explicit breakfast skip row with skip_reason_code=fasting_lab_same_morning when breakfast would otherwise occur before labs."
      ],
      "goal_action_ids": [
        "ga_structured_meals_weekly"
      ],
      "goal_tags": [
        "fasting",
        "meal_timing",
        "support"
      ],
      "intent": "fasting_aware_meal",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
        "activity_id": "act_b01_fasting_aware_meal_support_primary",
        "activity_type": "food",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "lab schedule"
        ],
        "dependencies": [],
        "details": "Supports meal scheduling logic around fasting labs. Member receives reminder and meal plan adjustment for fasting requirement.",
        "duration_minutes": 0,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "06:00-10:00"
          ],
          "type": "due_week"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Supports meal timing and structure around fasting labs; does not count as a meal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "fasting",
          "meal_timing",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "meal_metadata": {
          "dining_source": null,
          "facilitator_type": "member",
          "meal_slot": null,
          "prep_source": null
        },
        "metrics_to_collect": [
          "meal_timing_adherence"
        ],
        "prep_required": false,
        "priority": 85,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_fasting_aware_meal_support_remote_check_sub",
          "act_b01_breakfast_skip_for_fasting_lab"
        ],
        "title": "Fasting-aware meal timing support"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
          "activity_id": "act_b01_fasting_aware_meal_support_remote_check_sub",
          "activity_type": "food",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "lab schedule"
          ],
          "dependencies": [],
          "details": "Remote review of fasting timing, hydration, and first-meal plan when lab timing changes or travel creates uncertainty.",
          "duration_minutes": 10,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "06:00-10:00"
            ],
            "type": "due_week"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "fasting",
            "meal_timing",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_metadata": {
            "dining_source": null,
            "facilitator_type": "member",
            "meal_slot": null,
            "prep_source": null
          },
          "metrics_to_collect": [
            "meal_timing_adherence"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "lab schedule"
            ]
          },
          "prep_required": true,
          "priority": 88,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_fasting_aware_meal_support_primary",
          "substitution_notes": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
          "substitution_reason_codes": [
            "remote_delivery_needed",
            "time_conflict"
          ],
          "title": "Remote fasting meal timing check",
          "variety_role": "planned_variety",
          "weekly_variety_min": 1
        },
        {
          "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
          "activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "activity_type": "food",
          "allowed_locations": [
            "home",
            "clinic",
            "remote"
          ],
          "care_context_required": [
            "lab schedule",
            "fasting start time"
          ],
          "dependencies": [
            {
              "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
              "must_happen": "after",
              "notes": "Use only on a day with a scheduled fasting lab draw before the normal breakfast window closes.",
              "type": "same_day_activity_context"
            }
          ],
          "details": "Explicit skipped breakfast row for a fasting metabolic lab draw. Water only until the lab draw is complete; first caloric meal should be scheduled after labs.",
          "duration_minutes": 0,
          "facilitator_type": "member",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "06:30-10:00"
            ],
            "type": "constraint_scoped"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_structured_meals_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Skipped breakfast does not count as a structured meal; it preserves fasting validity for metabolic lab draw.",
              "role": "skip",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "fasting",
            "breakfast",
            "skip",
            "metabolic_review"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "meal_slot": "breakfast",
          "metrics_to_collect": [
            "skip_reason_recorded",
            "fasting_confirmed"
          ],
          "prep_metadata": {
            "calendar_skip_reason_required": true,
            "due_before_minutes": 720,
            "missing_data_policy": "do_not_schedule_skip_without_lab_draw",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "fasting_lab_breakfast_skip",
            "required_inputs": [
              "lab schedule",
              "fasting start time"
            ],
            "skip_reason_code": "fasting_lab_same_morning"
          },
          "prep_required": true,
          "priority": 10,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian",
            "physician"
          ],
          "skip_adjustment": {
            "is_skip": true,
            "reschedule_first_meal_after_activity": true,
            "skip_reason_code": "fasting_lab_same_morning",
            "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting.",
            "valid_only_before_activity_id": "act_b05_clinical_lab_draw_due_week_primary"
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_breakfast_chef_home_primary",
          "substitution_notes": "Use instead of breakfast when a fasting lab draw is scheduled before breakfast.",
          "substitution_reason_codes": [
            "fasting_lab_same_morning"
          ],
          "title": "Skip breakfast for fasting lab draw"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_fasting_aware_meal_support_remote_check_sub",
          "reason": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
          "when": "remote_delivery_needed or time_conflict"
        },
        {
          "prefer_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
          "reason": "Preserves 8-hour fasting validity for metabolic lab draw and creates an explicit skipped-breakfast calendar row.",
          "when": "fasting lab draw is scheduled before breakfast or before first caloric meal"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_supplement_protocol_support",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_adherence_support_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": true,
        "target_units": 7,
        "unit_label": "protocol checks"
      },
      "family_validation_notes": [
        "Daily supplement protocol supports adherence but does not count as a core meal.",
        "Must not inflate meal or fitness goal math.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_adherence_support_weekly"
      ],
      "goal_tags": [
        "supplement",
        "adherence",
        "support"
      ],
      "intent": "supplement_protocol",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_supplement_protocol_support",
        "activity_id": "act_b01_supplement_protocol_support_primary",
        "activity_type": "medication",
        "allowed_locations": [
          "home",
          "office",
          "travel_hotel"
        ],
        "care_context_required": [
          "current supplement protocol"
        ],
        "dependencies": [],
        "details": "Member takes prescribed supplements with breakfast or dinner. Protocol is reviewed weekly by dietitian.",
        "duration_minutes": 5,
        "facilitator_type": "member",
        "food_timing": "with_breakfast_or_dinner",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "07:00-08:30",
            "19:00-20:30"
          ],
          "type": "daily"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_adherence_support_weekly",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Daily supplement protocol supports adherence but does not count as a core meal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "supplement",
          "adherence",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_002",
          "phase_marcus_003",
          "phase_marcus_004",
          "phase_marcus_005",
          "phase_marcus_006",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "protocol_completion",
          "miss_reason"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "context_review",
          "required_inputs": [
            "current supplement protocol"
          ]
        },
        "prep_required": true,
        "priority": 90,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_supplement_protocol_support_travel_timing_sub"
        ],
        "title": "Daily supplement protocol with breakfast or dinner"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_supplement_protocol_support",
          "activity_id": "act_b01_supplement_protocol_support_travel_timing_sub",
          "activity_type": "medication",
          "allowed_locations": [
            "remote",
            "travel_hotel"
          ],
          "care_context_required": [
            "current supplement protocol"
          ],
          "dependencies": [],
          "details": "Travel-compatible supplement timing review tied to the available breakfast or dinner window, without replacing a meal.",
          "duration_minutes": 10,
          "facilitator_type": "member",
          "food_timing": "with_breakfast_or_dinner",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "07:00-08:30",
              "19:00-20:30"
            ],
            "type": "daily"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_adherence_support_weekly",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Preserves supplement adherence support when travel disrupts the usual meal window.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "supplement",
            "adherence",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_002",
            "phase_marcus_003",
            "phase_marcus_004",
            "phase_marcus_005",
            "phase_marcus_006",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "protocol_completion",
            "miss_reason"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "current supplement protocol"
            ]
          },
          "prep_required": true,
          "priority": 93,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_supplement_protocol_support_primary",
          "substitution_notes": "Preserves supplement adherence support when travel disrupts the usual meal window.",
          "substitution_reason_codes": [
            "travel_window",
            "remote_delivery_needed"
          ],
          "title": "Travel supplement timing review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_supplement_protocol_support_travel_timing_sub",
          "reason": "Preserves supplement adherence support when travel disrupts the usual meal window.",
          "when": "travel_window or remote_delivery_needed"
        }
      ]
    },
    {
      "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
      "care_domain": "metabolic_nutrition",
      "family_target": {
        "goal_action_id": "ga_behavior_coaching_weekly",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": true,
        "target_units": 3,
        "unit_label": "travel continuity reviews"
      },
      "family_validation_notes": [
        "Remote coach/dietitian check-in for meal adherence during travel.",
        "Support-only; does not count as a meal.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "travel",
        "meal_adherence",
        "support"
      ],
      "intent": "travel_support",
      "primary_activity": {
        "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
        "activity_id": "act_b01_travel_meal_adherence_check_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "travel window",
          "recent meal log"
        ],
        "dependencies": [],
        "details": "Remote check-in with dietitian or health coach to review meal adherence and troubleshoot barriers during travel.",
        "duration_minutes": 15,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "19:00-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "value": 1
          }
        ],
        "goal_tags": [
          "travel",
          "meal_adherence",
          "support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "adherence_score",
          "barrier_notes"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "context_review",
          "required_inputs": [
            "travel window",
            "recent meal log"
          ]
        },
        "prep_required": true,
        "priority": 95,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_dietitian_01",
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian",
          "remote_coach_pool"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b01_travel_meal_adherence_check_photo_review_sub"
        ],
        "title": "Remote meal adherence check-in (travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
          "activity_id": "act_b01_travel_meal_adherence_check_photo_review_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "travel window",
            "recent meal log"
          ],
          "dependencies": [],
          "details": "Asynchronous dietitian or coach review of travel meal photos and notes to keep structured eating aligned with metabolic goals.",
          "duration_minutes": 10,
          "facilitator_type": "dietitian",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "19:00-20:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_behavior_coaching_weekly",
              "value": 1
            }
          ],
          "goal_tags": [
            "travel",
            "meal_adherence",
            "support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "adherence_score",
            "barrier_notes"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "travel window",
              "recent meal log"
            ]
          },
          "prep_required": true,
          "priority": 98,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_dietitian_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian",
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b01_travel_meal_adherence_check_primary",
          "substitution_notes": "Preserves travel meal adherence support when a live check-in cannot be scheduled.",
          "substitution_reason_codes": [
            "travel_window",
            "time_conflict"
          ],
          "title": "Async travel meal photo review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b01_travel_meal_adherence_check_photo_review_sub",
          "reason": "Preserves travel meal adherence support when a live check-in cannot be scheduled.",
          "when": "travel_window or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_zone2_gym",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Primary gym-based aerobic session with realistic home and time-based substitutions.",
        "Substitutions count toward the same weekly aerobic conditioning target.",
        "Core aerobic plan target is 2 sessions/week across gym + home aerobic families."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "metabolic_health"
      ],
      "intent": "zone2",
      "primary_activity": {
        "activity_family_id": "b02_cardio_zone2_gym",
        "activity_id": "act_b02_cardio_zone2_gym_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "gym"
        ],
        "care_context_required": [
          "current aerobic goal",
          "recent knee/back status"
        ],
        "dependencies": [],
        "details": "Structured aerobic session using rower or stationary bike at preferred gym. Prioritizes Zone 2 heart rate. Trainer available for guidance if scheduled.",
        "duration_minutes": 45,
        "facilitator_type": "trainer",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "saturday"
          ],
          "preferred_time_windows": [
            "08:00-10:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Directly satisfies weekly aerobic conditioning target.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "zone2",
          "metabolic_health"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "average_heart_rate",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 101,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_rower_gym"
        ],
        "required_provider_ids": [
          "provider_trainer_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": false,
          "notes": "If post-travel or equipment unavailable, use substitution."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_zone2_gym_home_sub",
          "act_b02_cardio_zone2_gym_time_sub"
        ],
        "title": "Zone 2 aerobic session at gym (rower or bike)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_zone2_gym",
          "activity_id": "act_b02_cardio_zone2_gym_home_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Home-based aerobic session using stationary bike, brisk walking, or bodyweight circuit. Used if gym or equipment is unavailable.",
          "duration_minutes": 40,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "saturday"
            ],
            "preferred_time_windows": [
              "08:00-10:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts as aerobic conditioning if gym unavailable.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "zone2",
            "metabolic_health"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 102,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Lower-load option if needed."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_zone2_gym_primary",
          "substitution_notes": "Preserves aerobic intent when gym or rower is unavailable.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "equipment_unavailable"
          ],
          "title": "Zone 2 aerobic session at home (bodyweight or cycling)"
        },
        {
          "activity_family_id": "b02_cardio_zone2_gym",
          "activity_id": "act_b02_cardio_zone2_gym_time_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "gym"
          ],
          "care_context_required": [
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Condensed aerobic session at gym (rower or bike) for days with limited time. Used when full session cannot fit after work or due to travel buffer.",
          "duration_minutes": 30,
          "facilitator_type": "trainer",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "saturday"
            ],
            "preferred_time_windows": [
              "10:15-11:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts if gym session cannot be scheduled due to time conflict.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "zone2",
            "metabolic_health"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 103,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_rower_gym"
          ],
          "required_provider_ids": [
            "provider_trainer_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Shorter session if needed."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_zone2_gym_primary",
          "substitution_notes": "Preserves aerobic intent when only a shorter gym window is available.",
          "substitution_reason_codes": [
            "time_conflict"
          ],
          "title": "Shorter aerobic session at gym (reduced duration)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_zone2_gym_home_sub",
          "reason": "Preserves aerobic conditioning using home-based equipment or bodyweight.",
          "when": "Gym or rower unavailable (maintenance, travel, or access issue)"
        },
        {
          "prefer_activity_id": "act_b02_cardio_zone2_gym_time_sub",
          "reason": "Enables a shorter session to maintain aerobic intent.",
          "when": "Time conflict prevents full session (e.g., after office hours with travel buffer)"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b02_cardio_zone2_home",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Primary home-based aerobic session with travel-compatible substitution.",
        "Substitution counts toward weekly aerobic conditioning target.",
        "Core aerobic plan target is 2 sessions/week across gym + home aerobic families."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "home_fitness"
      ],
      "intent": "zone2",
      "primary_activity": {
        "activity_family_id": "b02_cardio_zone2_home",
        "activity_id": "act_b02_cardio_zone2_home_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "current aerobic goal"
        ],
        "dependencies": [],
        "details": "Home-based aerobic session using stationary bike, brisk walking, or bodyweight circuit. Self-led, knee-safe.",
        "does_not_count_toward_goal_action_ids": [
          "ga_strength_sessions_weekly"
        ],
        "duration_minutes": 40,
        "facilitator_type": "self",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "thursday"
          ],
          "preferred_time_windows": [
            "06:30-08:00",
            "07:15-08:00",
            "19:50-20:30",
            "18:45-20:00",
            "18:00-18:45"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Directly satisfies weekly aerobic conditioning target.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "zone2",
          "home_fitness"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 104,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Can be replaced by travel variant if home unavailable."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_zone2_home_travel_sub"
        ],
        "title": "Zone 2 aerobic session at home (cycling or brisk walk)",
        "walking_activity_metadata": {
          "counts_as_full_aerobic_session": true,
          "counts_as_strength": false,
          "walk_only_week_reason_field": "calendar_week_validation_reason",
          "walk_only_week_requires_reason": true
        }
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_zone2_home",
          "activity_id": "act_b02_cardio_zone2_home_travel_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Travel-compatible aerobic session using bodyweight and mini bands in hotel room. Used if home is unavailable due to travel.",
          "duration_minutes": 35,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "thursday"
            ],
            "preferred_time_windows": [
              "06:30-08:00",
              "07:15-08:00",
              "19:50-20:30",
              "18:45-20:00",
              "18:00-18:45"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Counts if home session is blocked by travel.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "zone2",
            "travel_adapted"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 105,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Travel-compatible."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_zone2_home_primary",
          "substitution_notes": "Preserves aerobic intent when home is unavailable due to travel.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable"
          ],
          "title": "Zone 2 aerobic session in hotel room (bodyweight/band circuit)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_zone2_home_travel_sub",
          "reason": "Preserves aerobic conditioning using travel-compatible bodyweight/band circuit.",
          "when": "Home unavailable due to travel or facility issue"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Travel hotel gym aerobic session with pool-based substitution.",
        "Both support travel continuity but do not add to normal-week denominator."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "travel_adapted",
        "hotel_gym"
      ],
      "intent": "travel_cardio_substitution",
      "primary_activity": {
        "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
        "activity_id": "act_b02_cardio_zone2_travel_hotel_gym_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "current aerobic goal"
        ],
        "dependencies": [],
        "details": "Aerobic session using hotel gym bike or treadmill during travel. Used when normal gym/home sessions are not possible.",
        "duration_minutes": 35,
        "facilitator_type": "self",
        "frequency": {
          "count": 1,
          "preferred_days": [],
          "preferred_time_windows": [
            "07:00-08:00"
          ],
          "type": "travel-window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Travel hotel gym aerobic session counts toward weekly aerobic conditioning.",
            "role": "core",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "goal_id": "goal_travel_resilience",
            "notes": "Supports travel continuity.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "zone2",
          "travel_adapted",
          "hotel_gym"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 106,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_basic_gym_hotel_tokyo"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Travel adaptation."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_zone2_travel_hotel_gym_pool_sub"
        ],
        "title": "Aerobic session in hotel gym (bike or treadmill)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
          "activity_id": "act_b02_cardio_zone2_travel_hotel_gym_pool_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window",
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Aerobic swim session in hotel pool during travel. Used if hotel gym equipment is unavailable or pool is preferred.",
          "duration_minutes": 30,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_days": [],
            "preferred_time_windows": [
              "07:00-08:00"
            ],
            "type": "travel-window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "zone2",
            "travel_adapted",
            "hotel_pool"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 107,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_pool_hotel_hk"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Travel adaptation."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_zone2_travel_hotel_gym_primary",
          "substitution_notes": "Preserves aerobic intent using hotel pool when gym equipment is unavailable.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "equipment_unavailable"
          ],
          "title": "Aerobic swim session in hotel pool"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_zone2_travel_hotel_gym_pool_sub",
          "reason": "Preserves aerobic conditioning using hotel pool.",
          "when": "Hotel gym equipment unavailable or pool preferred"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Travel bodyweight aerobic session with walking fallback for lowest-resource hotel scenario.",
        "Both support travel continuity but do not add to normal-week denominator."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "travel_adapted",
        "bodyweight"
      ],
      "intent": "travel_cardio_substitution",
      "primary_activity": {
        "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
        "activity_id": "act_b02_cardio_zone2_travel_bodyweight_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "current aerobic goal"
        ],
        "dependencies": [],
        "details": "Aerobic session using bodyweight and mini bands in hotel room during low-resource travel. Used when no gym or pool is available.",
        "duration_minutes": 25,
        "facilitator_type": "self",
        "frequency": {
          "count": 1,
          "preferred_days": [],
          "preferred_time_windows": [
            "06:30-07:15"
          ],
          "type": "travel-window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Hotel pool aerobic session counts toward weekly aerobic conditioning.",
            "role": "core",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "goal_id": "goal_travel_resilience",
            "notes": "Supports travel continuity.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "travel_adapted",
          "bodyweight"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 108,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Travel adaptation for low-resource hotel."
        },
        "substitution_activity_ids": [],
        "title": "Bodyweight aerobic session in hotel room"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
          "activity_id": "act_b02_cardio_zone2_travel_bodyweight_walk_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window",
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Brisk walking session outside or in hotel corridors during travel when no equipment is available.",
          "does_not_count_toward_goal_action_ids": [
            "ga_strength_sessions_weekly"
          ],
          "duration_minutes": 30,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_days": [],
            "preferred_time_windows": [
              "07:00-07:45"
            ],
            "type": "travel-window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "travel_adapted",
            "walking"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_006"
          ],
          "last_resort_substitution_metadata": {
            "avoid_week_with_only_walks_unless_impossible": true,
            "calendar_reason_required_if_scheduled": true,
            "last_resort": true,
            "prefer_non_walk_aerobic_before_walk": true,
            "reason_code_examples": [
              "facility_unavailable",
              "equipment_unavailable",
              "travel_window",
              "time_conflict",
              "pain_or_fatigue"
            ]
          },
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 109,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_bodyweight"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Travel adaptation for lowest-resource scenario."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_zone2_travel_bodyweight_primary",
          "substitution_notes": "Preserves aerobic intent using walking when even bodyweight circuit is not feasible.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "equipment_unavailable"
          ],
          "title": "Brisk walking session near hotel",
          "walking_activity_metadata": {
            "counts_as_full_aerobic_session": true,
            "counts_as_strength": false,
            "walk_only_week_reason_field": "calendar_week_validation_reason",
            "walk_only_week_requires_reason": true
          }
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_zone2_travel_bodyweight_walk_sub",
          "reason": "Preserves aerobic intent with brisk walking when all other options are blocked.",
          "when": "No equipment or space for bodyweight circuit in hotel room"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Travel pool-based aerobic session with bodyweight fallback.",
        "Both support travel continuity but do not add to normal-week denominator."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "swimming",
        "travel_adapted",
        "hotel_pool"
      ],
      "intent": "swim",
      "primary_activity": {
        "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
        "activity_id": "act_b02_cardio_swim_pool_hotel_hk_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel window",
          "current aerobic goal"
        ],
        "dependencies": [],
        "details": "Aerobic swim session in hotel pool during Hong Kong travel. Used as a travel-specific aerobic alternative.",
        "duration_minutes": 30,
        "facilitator_type": "self",
        "frequency": {
          "count": 1,
          "preferred_days": [],
          "preferred_time_windows": [
            "07:00-08:00"
          ],
          "type": "travel-window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Hotel pool aerobic session counts toward weekly aerobic conditioning.",
            "role": "core",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "goal_id": "goal_travel_resilience",
            "notes": "Supports travel continuity.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "swimming",
          "travel_adapted",
          "hotel_pool"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 110,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_pool_hotel_hk"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Travel adaptation."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_swim_pool_hotel_hk_bodyweight_sub"
        ],
        "title": "Swimming aerobic session in hotel pool (Hong Kong)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
          "activity_id": "act_b02_cardio_swim_pool_hotel_hk_bodyweight_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window",
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Bodyweight/band aerobic session in hotel room if pool is unavailable or access is restricted.",
          "duration_minutes": 25,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_days": [],
            "preferred_time_windows": [
              "07:00-07:45"
            ],
            "type": "travel-window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "travel_adapted",
            "bodyweight"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 111,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Travel adaptation."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_swim_pool_hotel_hk_primary",
          "substitution_notes": "Preserves aerobic intent when pool is unavailable.",
          "substitution_reason_codes": [
            "facility_unavailable"
          ],
          "title": "Bodyweight aerobic session in hotel room (if pool unavailable)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_swim_pool_hotel_hk_bodyweight_sub",
          "reason": "Preserves aerobic intent with bodyweight circuit if pool is not accessible.",
          "when": "Hotel pool unavailable or access restricted"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_walking_office",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Office walking breaks are support-only and do not count toward aerobic session denominator.",
        "Walking breaks never count toward strength sessions.",
        "On WFH dates, office walking breaks must be converted to home walking breaks or rejected/unscheduled with a reason."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "walking",
        "office_support"
      ],
      "intent": "walk",
      "primary_activity": {
        "activity_family_id": "b02_cardio_walking_office",
        "activity_id": "act_b02_cardio_walking_office_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "office"
        ],
        "care_context_required": [
          "current aerobic goal"
        ],
        "dependencies": [],
        "details": "Short walking or movement break during office hours to support aerobic activity when full session is not possible.",
        "does_not_count_toward_goal_action_ids": [
          "ga_strength_sessions_weekly"
        ],
        "duration_minutes": 10,
        "facilitator_type": "self",
        "frequency": {
          "count": 3,
          "preferred_days": [
            "monday",
            "wednesday",
            "friday"
          ],
          "preferred_time_windows": [
            "10:30-11:00",
            "15:00-15:30"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "walking",
          "office_support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "last_resort_substitution_metadata": {
          "avoid_week_with_only_walks_unless_impossible": true,
          "calendar_reason_required_if_scheduled": true,
          "last_resort": true,
          "prefer_non_walk_aerobic_before_walk": true,
          "reason_code_examples": [
            "facility_unavailable",
            "equipment_unavailable",
            "travel_window",
            "time_conflict",
            "pain_or_fatigue"
          ]
        },
        "load_level": "low",
        "metrics_to_collect": [
          "completion"
        ],
        "prep_required": false,
        "priority": 112,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": true,
        "share_with_provider_types": [
          "trainer",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Support-only."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_walking_office_remote_sub"
        ],
        "title": "Short walking or movement break at office",
        "walking_activity_metadata": {
          "counts_as_full_aerobic_session": false,
          "counts_as_strength": false,
          "walk_only_week_reason_field": "calendar_week_validation_reason",
          "walk_only_week_requires_reason": true
        },
        "wfh_scheduling_constraint": {
          "calendar_rejection_reason_required": true,
          "if_substitution_unavailable": "reject_or_unschedule",
          "on_member_location_home_day": "do_not_schedule_office_location",
          "preferred_substitution_activity_id": "act_b02_cardio_walking_office_remote_sub",
          "rejection_reason_code": "wfh_no_office_location_activity"
        }
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_walking_office",
          "activity_id": "act_b02_cardio_walking_office_remote_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "current aerobic goal"
          ],
          "dependencies": [],
          "details": "Short walking or movement break at home during WFH days to support movement without scheduling an office-location activity.",
          "does_not_count_toward_goal_action_ids": [
            "ga_strength_sessions_weekly"
          ],
          "duration_minutes": 10,
          "facilitator_type": "self",
          "frequency": {
            "count": 3,
            "preferred_days": [
              "monday",
              "wednesday",
              "friday"
            ],
            "preferred_time_windows": [
              "10:30-11:00",
              "15:00-15:30"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "walking",
            "home_support",
            "wfh"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "last_resort_substitution_metadata": {
            "avoid_week_with_only_walks_unless_impossible": true,
            "calendar_reason_required_if_scheduled": true,
            "last_resort": true,
            "prefer_non_walk_aerobic_before_walk": true,
            "reason_code_examples": [
              "facility_unavailable",
              "equipment_unavailable",
              "travel_window",
              "time_conflict",
              "pain_or_fatigue"
            ]
          },
          "load_level": "low",
          "metrics_to_collect": [
            "completion"
          ],
          "prep_required": false,
          "priority": 113,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_bodyweight"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": true,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Support-only."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_walking_office_primary",
          "substitution_notes": "Preserves movement-break intent on WFH days without using office location.",
          "substitution_reason_codes": [
            "wfh_location_override",
            "facility_unavailable",
            "time_conflict"
          ],
          "title": "Short walking break at home during WFH",
          "walking_activity_metadata": {
            "counts_as_full_aerobic_session": false,
            "counts_as_strength": false,
            "walk_only_week_reason_field": "calendar_week_validation_reason",
            "walk_only_week_requires_reason": true
          },
          "wfh_scheduling_constraint": {
            "calendar_substitution_reason_required": true,
            "replaces_office_location_activity": true,
            "substitution_reason_code": "wfh_location_override",
            "valid_on_member_location_home_day": true
          }
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_walking_office_remote_sub",
          "reason": "WFH day means office-location activities are invalid; use home walking break instead.",
          "when": "member_location override is home or WFH day is active"
        },
        {
          "prefer_activity_id": "act_b02_cardio_walking_office_remote_sub",
          "reason": "Preserves aerobic support intent with home walking breaks.",
          "when": "Office unavailable or working remotely"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b02_cardio_remote_coach_progression_review",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Remote coach review is support-only and does not count toward aerobic session denominator.",
        "Review requires recent aerobic session data; do not schedule if no aerobic session log exists in the lookback window.",
        "Asynchronous log review is the fallback when live review cannot be scheduled."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "remote_coach",
        "progression_review"
      ],
      "intent": "remote_handoff",
      "primary_activity": {
        "activity_family_id": "b02_cardio_remote_coach_progression_review",
        "activity_id": "act_b02_cardio_remote_coach_progression_review_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent aerobic session data",
          "session duration",
          "RPE",
          "average heart rate if available",
          "barriers or missed-session notes"
        ],
        "dependencies": [
          {
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "lookback_days": 14,
            "minimum_sessions": 1,
            "must_exist": true,
            "notes": "Coach progression review requires at least one recent aerobic session log in the prior 14 days.",
            "type": "recent_session_data"
          }
        ],
        "details": "Remote check-in with Elyx health coach to review aerobic session adherence, barriers, and plan adjustments.",
        "duration_minutes": 20,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "monday"
          ],
          "preferred_time_windows": [
            "09:00-09:30",
            "19:00-20:00"
          ],
          "preferred_week": "second",
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Remote coach review supports adherence but does not count as a session.",
            "role": "support",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "remote_coach",
          "progression_review"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "coach_notes",
          "next_action"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "lookback_days": 14,
          "minimum_recent_sessions": 1,
          "missing_data_policy": "defer_review_until_recent_aerobic_session_data_exists",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "aerobic_progression_data_review",
          "required_inputs": [
            "recent aerobic session data",
            "session duration",
            "RPE",
            "average heart rate if available",
            "barriers or missed-session notes"
          ],
          "required_recent_activity_goal_action_id": "ga_aerobic_conditioning_weekly",
          "requires_recent_activity_data": true
        },
        "prep_required": true,
        "priority": 114,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Support-only."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_remote_coach_progression_review_async_log_sub"
        ],
        "title": "Remote coach review of aerobic progression"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_remote_coach_progression_review",
          "activity_id": "act_b02_cardio_remote_coach_progression_review_async_log_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent aerobic session data",
            "session duration",
            "RPE",
            "average heart rate if available",
            "barriers or missed-session notes"
          ],
          "dependencies": [
            {
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "lookback_days": 14,
              "minimum_sessions": 1,
              "must_exist": true,
              "notes": "Coach progression review requires at least one recent aerobic session log in the prior 14 days.",
              "type": "recent_session_data"
            }
          ],
          "details": "Coach reviews wearable or session notes asynchronously and adjusts the next aerobic target when schedules prevent a live review.",
          "duration_minutes": 10,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "monday"
            ],
            "preferred_time_windows": [
              "09:00-09:30",
              "19:00-20:00"
            ],
            "preferred_week": "second",
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Preserves aerobic progression support when live coach availability is blocked.",
              "role": "support",
              "unit": "activity",
              "value": 0
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "remote_coach",
            "progression_review"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "coach_notes",
            "next_action"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "lookback_days": 14,
            "minimum_recent_sessions": 1,
            "missing_data_policy": "defer_review_until_recent_aerobic_session_data_exists",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "aerobic_progression_data_review",
            "required_inputs": [
              "recent aerobic session data",
              "session duration",
              "RPE",
              "average heart rate if available",
              "barriers or missed-session notes"
            ],
            "required_recent_activity_goal_action_id": "ga_aerobic_conditioning_weekly",
            "requires_recent_activity_data": true
          },
          "prep_required": true,
          "priority": 117,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_remote_coach_progression_review_primary",
          "substitution_notes": "Preserves aerobic progression support when live coach availability is blocked.",
          "substitution_reason_codes": [
            "time_conflict",
            "remote_delivery_needed"
          ],
          "title": "Async aerobic log review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_remote_coach_progression_review_async_log_sub",
          "reason": "Preserves aerobic progression support when live coach availability is blocked.",
          "when": "time_conflict or remote_delivery_needed"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_cgm_log_support",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": true,
        "target_units": 0,
        "unit_label": "protocol checks"
      },
      "family_validation_notes": [
        "CGM log is support-only and does not count toward aerobic or meal session denominator.",
        "No substitutions needed."
      ],
      "goal_action_ids": [
        "ga_adherence_support_weekly"
      ],
      "goal_tags": [
        "cgm",
        "adherence_support",
        "metabolic_tracking"
      ],
      "intent": "cgm_log",
      "primary_activity": {
        "activity_family_id": "b02_cardio_cgm_log_support",
        "activity_id": "act_b02_cardio_cgm_log_support_primary",
        "activity_type": "medication",
        "allowed_locations": [
          "home",
          "office",
          "travel_hotel"
        ],
        "care_context_required": [
          "recent aerobic or meal session"
        ],
        "dependencies": [],
        "details": "Continuous glucose monitor (CGM) check and log to support metabolic tracking. Performed as needed after aerobic or meal sessions.",
        "duration_minutes": 5,
        "facilitator_type": "self",
        "frequency": {
          "count": 0,
          "preferred_time_windows": [
            "07:00-08:00",
            "19:00-20:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_adherence_support_weekly",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "CGM log supports adherence but does not count as a core outcome.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "cgm",
          "adherence_support",
          "metabolic_tracking"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "glucose_value",
          "log_time"
        ],
        "prep_required": false,
        "priority": 115,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": true,
        "share_with_provider_types": [
          "dietitian",
          "physician"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Support-only."
        },
        "substitution_activity_ids": [],
        "title": "CGM check and log (as needed)"
      },
      "substitution_activities": [],
      "substitution_rules": []
    },
    {
      "activity_family_id": "b02_cardio_hydration_protocol_support",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_adherence_support_weekly",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": true,
        "target_units": 0,
        "unit_label": "protocol checks"
      },
      "family_validation_notes": [
        "Hydration protocol is support-only and does not count toward aerobic or meal session denominator.",
        "No substitutions needed.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_adherence_support_weekly"
      ],
      "goal_tags": [
        "hydration",
        "adherence_support",
        "travel_support"
      ],
      "intent": "hydration",
      "primary_activity": {
        "activity_family_id": "b02_cardio_hydration_protocol_support",
        "activity_id": "act_b02_cardio_hydration_protocol_support_primary",
        "activity_type": "medication",
        "allowed_locations": [
          "home",
          "travel_hotel",
          "office"
        ],
        "care_context_required": [
          "travel window",
          "recent aerobic session"
        ],
        "dependencies": [],
        "details": "Hydration and electrolyte protocol to support energy and recovery, especially during travel or after aerobic sessions.",
        "duration_minutes": 5,
        "facilitator_type": "self",
        "frequency": {
          "count": 0,
          "preferred_time_windows": [
            "07:00-08:00",
            "18:00-19:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_adherence_support_weekly",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Hydration protocol supports adherence but does not count as a core outcome.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "hydration",
          "adherence_support",
          "travel_support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "hydration_amount"
        ],
        "prep_required": false,
        "priority": 116,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": true,
        "share_with_provider_types": [
          "dietitian",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Support-only."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_hydration_protocol_support_hotel_protocol_sub"
        ],
        "title": "Hydration and electrolyte protocol (especially during travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_hydration_protocol_support",
          "activity_id": "act_b02_cardio_hydration_protocol_support_hotel_protocol_sub",
          "activity_type": "medication",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel window",
            "recent aerobic session"
          ],
          "dependencies": [],
          "details": "Travel-compatible hydration and electrolyte check using hotel-room supplies before or after aerobic work.",
          "duration_minutes": 5,
          "facilitator_type": "self",
          "frequency": {
            "count": 0,
            "preferred_time_windows": [
              "07:00-08:00",
              "18:00-19:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_adherence_support_weekly",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Preserves hydration support when the member is travelling or away from the usual setup.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "hydration",
            "adherence_support",
            "travel_support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "hydration_amount"
          ],
          "prep_required": false,
          "priority": 119,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": true,
          "share_with_provider_types": [
            "dietitian",
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_hydration_protocol_support_primary",
          "substitution_notes": "Preserves hydration support when the member is travelling or away from the usual setup.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable"
          ],
          "title": "Hotel-room hydration protocol"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_hydration_protocol_support_hotel_protocol_sub",
          "reason": "Preserves hydration support when the member is travelling or away from the usual setup.",
          "when": "travel_window or facility_unavailable"
        }
      ]
    },
    {
      "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
      "care_domain": "cardiorespiratory_fitness",
      "family_target": {
        "goal_action_id": "ga_aerobic_conditioning_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Facility-unavailable aerobic session with walking fallback.",
        "Both count toward aerobic conditioning denominator if primary is blocked.",
        "Fallback family must not create extra aerobic demand; use only when a core aerobic session is blocked."
      ],
      "goal_action_ids": [
        "ga_aerobic_conditioning_weekly"
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "facility_unavailable",
        "travel_adapted"
      ],
      "intent": "facility_unavailable_cardio_substitution",
      "primary_activity": {
        "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
        "activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home",
          "travel_hotel",
          "office"
        ],
        "care_context_required": [
          "facility/equipment status"
        ],
        "dependencies": [],
        "details": "Aerobic session using bodyweight and mini bands when gym or equipment is unavailable due to travel, maintenance, or time conflict.",
        "duration_minutes": 35,
        "facilitator_type": "self",
        "frequency": {
          "count": 0,
          "preferred_days": [
            "thursday",
            "sunday"
          ],
          "preferred_time_windows": [
            "18:45-20:00",
            "08:00-10:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_aerobic_conditioning_weekly",
            "goal_id": "goal_metabolic_health",
            "notes": "Counts as aerobic conditioning if gym or equipment is unavailable.",
            "role": "core",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "aerobic_conditioning",
          "facility_unavailable",
          "travel_adapted"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_005"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "RPE",
          "session_duration"
        ],
        "prep_required": false,
        "priority": 117,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed_after_poor_sleep": true,
          "allowed_after_travel": true,
          "notes": "Travel/facility adaptation."
        },
        "substitution_activity_ids": [
          "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub"
        ],
        "title": "Aerobic session using bodyweight/bands (facility unavailable)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
          "activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "home",
            "travel_hotel",
            "office"
          ],
          "care_context_required": [
            "facility/equipment status"
          ],
          "dependencies": [],
          "details": "Brisk walking session outdoors or in hotel corridors when all other aerobic options are blocked.",
          "does_not_count_toward_goal_action_ids": [
            "ga_strength_sessions_weekly"
          ],
          "duration_minutes": 30,
          "facilitator_type": "self",
          "frequency": {
            "count": 0,
            "preferred_days": [
              "thursday",
              "sunday"
            ],
            "preferred_time_windows": [
              "18:45-20:00",
              "08:00-10:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_aerobic_conditioning_weekly",
              "goal_id": "goal_metabolic_health",
              "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
              "role": "core",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "aerobic_conditioning",
            "facility_unavailable",
            "walking"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_005"
          ],
          "last_resort_substitution_metadata": {
            "avoid_week_with_only_walks_unless_impossible": true,
            "calendar_reason_required_if_scheduled": true,
            "last_resort": true,
            "prefer_non_walk_aerobic_before_walk": true,
            "reason_code_examples": [
              "facility_unavailable",
              "equipment_unavailable",
              "travel_window",
              "time_conflict",
              "pain_or_fatigue"
            ]
          },
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "RPE",
            "session_duration"
          ],
          "prep_required": false,
          "priority": 118,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Travel/facility adaptation."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_primary",
          "substitution_notes": "Preserves aerobic intent with brisk walking when all other options are blocked.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "equipment_unavailable",
            "time_conflict"
          ],
          "title": "Brisk walking session (facility/equipment unavailable)",
          "walking_activity_metadata": {
            "counts_as_full_aerobic_session": true,
            "counts_as_strength": false,
            "walk_only_week_reason_field": "calendar_week_validation_reason",
            "walk_only_week_requires_reason": true
          }
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub",
          "reason": "Preserves aerobic intent with brisk walking when all other options are blocked.",
          "when": "All equipment and facilities unavailable (travel, maintenance, or time conflict)"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b03_strength_trainer_gym",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Primary gym-based trainer session is core for weekly strength goal.",
        "Remote substitution is valid for provider/facility/time constraints.",
        "Mobility or lower-load adjustment required if pain/fatigue emerges.",
        "Core strength plan target is 2 sessions/week across trainer-led + home strength families."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led",
        "mobility_support"
      ],
      "intent": "trainer_strength",
      "primary_activity": {
        "activity_family_id": "b03_strength_trainer_gym",
        "activity_id": "act_b03_strength_trainer_gym_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "gym"
        ],
        "care_context_required": [
          "current knee/back status",
          "recent physio notes",
          "strength progression log"
        ],
        "dependencies": [],
        "details": "Full-body strength session with knee-safe modifications, led by Elyx Performance Trainer. Focus on progressive overload and safe lower-body work.",
        "duration_minutes": 60,
        "facilitator_type": "trainer",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "sunday"
          ],
          "preferred_time_windows": [
            "06:30-08:00",
            "19:30-20:30",
            "18:45-20:00",
            "11:00-12:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Trainer-led gym strength session directly counts toward weekly strength goal.",
            "role": "core",
            "unit": "session",
            "value": 1
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "trainer_led"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "high",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 181,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_strength_machines_gym",
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [
          "provider_strength_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": {
          "adjustment": "Schedule lower-load or mobility session and flag for care-team review.",
          "trigger": "pain_or_fatigue"
        },
        "substitution_activity_ids": [
          "act_b03_strength_trainer_gym_remote"
        ],
        "title": "Trainer-led knee-safe strength session at gym"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_trainer_gym",
          "activity_id": "act_b03_strength_trainer_gym_remote",
          "activity_type": "fitness",
          "allowed_locations": [
            "home",
            "remote",
            "travel_hotel"
          ],
          "care_context_required": [
            "current knee/back status",
            "recent physio notes",
            "strength progression log"
          ],
          "dependencies": [],
          "details": "Live remote session with Elyx Performance Trainer using available home or travel equipment. Focus on knee-safe movements and maintaining progression.",
          "duration_minutes": 50,
          "facilitator_type": "trainer",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "sunday"
            ],
            "preferred_time_windows": [
              "06:30-08:00",
              "19:30-20:30",
              "18:45-20:00",
              "11:00-12:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Remote trainer-led session counts toward weekly strength goal if in-person is unavailable.",
              "role": "core",
              "unit": "session",
              "value": 1
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "trainer_led",
            "remote"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_required": false,
          "priority": 182,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [
            "provider_strength_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "adjustment": "Schedule lower-load or mobility session and flag for care-team review.",
            "trigger": "pain_or_fatigue"
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_trainer_gym_primary",
          "substitution_notes": "Preserves trainer-led strength intent when in-person or gym is unavailable.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "facility_unavailable",
            "time_conflict"
          ],
          "title": "Remote trainer-led strength session"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_trainer_gym_remote",
          "reason": "Remote trainer-led session preserves core strength intent using available equipment.",
          "when": "Trainer or gym facility is unavailable, or time conflict prevents in-person session."
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b03_strength_home_strength",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Home-based session is core for weekly strength goal.",
        "Travel-adapted substitution is valid for facility/equipment/time constraints.",
        "Mobility or lower-load adjustment required if pain/fatigue emerges.",
        "Core strength plan target is 2 sessions/week across trainer-led + home strength families."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "home_based",
        "mobility_support"
      ],
      "intent": "home_strength",
      "primary_activity": {
        "activity_family_id": "b03_strength_home_strength",
        "activity_id": "act_b03_strength_home_strength_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "current knee/back status",
          "strength progression log"
        ],
        "dependencies": [],
        "details": "Strength session using dumbbells, bands, and bodyweight at home. Focus on knee-safe lower-body and core movements.",
        "duration_minutes": 45,
        "facilitator_type": "member",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "tuesday",
            "sunday"
          ],
          "preferred_time_windows": [
            "06:30-08:00",
            "19:45-20:30",
            "18:45-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Home-based strength session directly counts toward weekly strength goal.",
            "role": "core",
            "unit": "session",
            "value": 1
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "home_based"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 183,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_dumbbells_home",
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": {
          "adjustment": "Schedule mobility or lower-load session and flag for care-team review.",
          "trigger": "pain_or_fatigue"
        },
        "substitution_activity_ids": [
          "act_b03_strength_hotel_gym_strength_primary",
          "act_b03_strength_home_strength_travel"
        ],
        "title": "Home-based knee-safe strength session"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_home_strength",
          "activity_id": "act_b03_strength_home_strength_travel",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel",
            "remote"
          ],
          "care_context_required": [
            "current knee/back status",
            "strength progression log"
          ],
          "dependencies": [],
          "details": "Strength session using portable bands and bodyweight in hotel or remote setting. Focus on maintaining movement quality and knee safety.",
          "duration_minutes": 35,
          "facilitator_type": "member",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "tuesday",
              "sunday",
              "wednesday"
            ],
            "preferred_time_windows": [
              "06:30-08:00",
              "07:15-08:00",
              "19:50-20:30",
              "18:45-20:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Travel-adapted session counts toward weekly strength goal if home is unavailable.",
              "role": "core",
              "unit": "session",
              "value": 1
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "travel_adapted"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_required": false,
          "priority": 184,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "adjustment": "Schedule mobility session and flag for care-team review.",
            "trigger": "pain_or_fatigue"
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
          "substitution_notes": "Preserves home-based strength intent using travel-compatible equipment.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "equipment_unavailable",
            "time_conflict"
          ],
          "title": "Travel-adapted strength session (bands/bodyweight)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_hotel_gym_strength_primary",
          "reason": "Tokyo travel has hotel gym equipment, so use the hotel gym strength option before the in-room bands/bodyweight fallback.",
          "when": "Member is traveling and hotel gym equipment is available."
        },
        {
          "prefer_activity_id": "act_b03_strength_home_strength_travel",
          "reason": "Travel-adapted session preserves strength intent using portable equipment.",
          "when": "Home or equipment is unavailable, or time conflict prevents home session."
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      }
    },
    {
      "activity_family_id": "b03_strength_hotel_gym_strength",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Hotel gym session supports travel continuity, not normal-week denominator.",
        "Bodyweight/band substitution is valid for equipment/facility constraints."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "hotel_gym",
        "travel_continuity"
      ],
      "intent": "hotel_gym_strength",
      "primary_activity": {
        "activity_family_id": "b03_strength_home_strength",
        "activity_id": "act_b03_strength_hotel_gym_strength_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "current knee/back status"
        ],
        "dependencies": [],
        "details": "Strength session using available hotel gym equipment. Focus on maintaining strength and mobility during travel.",
        "duration_minutes": 40,
        "facilitator_type": "member",
        "frequency": {
          "count": 2,
          "preferred_days": [
            "tuesday",
            "sunday",
            "wednesday"
          ],
          "preferred_time_windows": [
            "06:30-08:00",
            "07:15-08:00",
            "19:50-20:30",
            "18:45-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Hotel gym strength session counts toward weekly strength goal when travel prevents home strength.",
            "role": "core",
            "unit": "session",
            "value": 1
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "hotel_gym",
          "travel_continuity"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 183,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_basic_gym_hotel_tokyo",
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": {
          "adjustment": "Schedule bodyweight/band session.",
          "trigger": "equipment_unavailable"
        },
        "substitution_activity_ids": [
          "act_b03_strength_hotel_gym_strength_bodyweight"
        ],
        "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
        "substitution_notes": "Use hotel gym equipment during Tokyo-style travel before falling back to in-room bands/bodyweight.",
        "substitution_reason_codes": [
          "travel_window",
          "facility_available",
          "equipment_available"
        ],
        "title": "Hotel gym strength session (travel window)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_home_strength",
          "activity_id": "act_b03_strength_hotel_gym_strength_bodyweight",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "current knee/back status"
          ],
          "dependencies": [],
          "details": "Strength session using only bodyweight and portable bands in hotel room. Focus on movement quality and knee safety.",
          "duration_minutes": 30,
          "facilitator_type": "member",
          "frequency": {
            "count": 2,
            "preferred_days": [
              "tuesday",
              "sunday",
              "wednesday"
            ],
            "preferred_time_windows": [
              "06:30-08:00",
              "07:15-08:00",
              "19:50-20:30",
              "18:45-20:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "In-room bodyweight/band session counts toward weekly strength goal only when hotel gym equipment is unavailable.",
              "role": "core",
              "unit": "session",
              "value": 1
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "bodyweight",
            "travel_continuity"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_required": false,
          "priority": 186,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "adjustment": "Schedule mobility session and flag for care-team review.",
            "trigger": "pain_or_fatigue"
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
          "substitution_notes": "Preserves travel strength intent when hotel gym equipment is unavailable.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable",
            "equipment_unavailable"
          ],
          "title": "Bodyweight/band strength session in hotel room"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_hotel_gym_strength_bodyweight",
          "reason": "Bodyweight/band session maintains travel continuity when gym equipment is not available.",
          "when": "Hotel gym equipment is unavailable or member prefers in-room session."
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_bodyweight_travel_substitution",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Bodyweight/band session is support-only for travel continuity.",
        "Remote coach substitution is valid for member needing extra guidance."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "bodyweight",
        "travel_low_resource"
      ],
      "intent": "lower_load_strength_substitution",
      "primary_activity": {
        "activity_family_id": "b03_strength_bodyweight_travel_substitution",
        "activity_id": "act_b03_strength_bodyweight_travel_substitution_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "current knee/back status"
        ],
        "dependencies": [],
        "details": "Travel-adapted strength session coached by Ravi using bodyweight and portable bands in the hotel room. Focus on movement quality and knee safety.",
        "duration_minutes": 25,
        "facilitator_type": "travel_trainer",
        "frequency": {
          "count": 1,
          "preferred_days": [],
          "preferred_time_windows": [
            "18:45-20:00",
            "07:00-08:30"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Ravi-led bodyweight/band session counts toward weekly strength only for low-resource travel when no hotel gym is available.",
            "role": "core",
            "unit": "session",
            "value": 1
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "bodyweight",
          "travel_low_resource"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 187,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [
          "provider_travel_trainer_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": {
          "adjustment": "Schedule mobility session and flag for care-team review.",
          "trigger": "pain_or_fatigue"
        },
        "substitution_activity_ids": [
          "act_b03_strength_bodyweight_travel_substitution_remote"
        ],
        "title": "Bodyweight/band strength session (low-resource travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_bodyweight_travel_substitution",
          "activity_id": "act_b03_strength_bodyweight_travel_substitution_remote",
          "activity_type": "fitness",
          "allowed_locations": [
            "travel_hotel",
            "remote"
          ],
          "care_context_required": [
            "current knee/back status"
          ],
          "dependencies": [],
          "details": "Remote coach provides live or asynchronous guidance for bodyweight/band strength session in hotel room.",
          "duration_minutes": 20,
          "facilitator_type": "travel_trainer",
          "frequency": {
            "count": 1,
            "preferred_days": [],
            "preferred_time_windows": [
              "18:45-20:00",
              "07:00-08:30"
            ],
            "type": "travel_window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Remote coach check-in supports travel continuity when member needs guidance.",
              "role": "support",
              "unit": "session",
              "value": 0
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "remote_coach",
            "travel_low_resource"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_required": false,
          "priority": 188,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [
            "provider_travel_trainer_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "adjustment": "Schedule mobility session and flag for care-team review.",
            "trigger": "pain_or_fatigue"
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_bodyweight_travel_substitution_primary",
          "substitution_notes": "Preserves travel strength intent with remote coach support when member needs guidance.",
          "substitution_reason_codes": [
            "travel_window",
            "equipment_unavailable",
            "lower_load_needed"
          ],
          "title": "Remote coach-guided strength session (travel)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_bodyweight_travel_substitution_remote",
          "reason": "Remote coach guidance preserves travel strength intent when member needs support.",
          "when": "Member requests remote coach support or needs extra guidance during low-resource travel."
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_mobility_post_travel",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Post-travel mobility session supports recovery and pain prevention.",
        "Member-led substitution is valid for provider unavailability."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly",
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "mobility",
        "recovery",
        "post_travel",
        "pain_prevention"
      ],
      "intent": "post_travel_recovery",
      "primary_activity": {
        "activity_family_id": "b03_strength_mobility_post_travel",
        "activity_id": "act_b03_strength_mobility_post_travel_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent travel details",
          "current pain/tightness status"
        ],
        "dependencies": [],
        "details": "Guided mobility and stretching session at home to address fatigue and lower-back tightness after travel.",
        "duration_minutes": 30,
        "facilitator_type": "physiotherapist",
        "frequency": {
          "count": 1,
          "preferred_days": [],
          "preferred_time_windows": [
            "18:45-20:00",
            "20:00-21:30"
          ],
          "type": "post_travel"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Post-travel mobility session supports recovery but does not count as strength unless explicitly substituted.",
            "role": "recovery",
            "unit": "action",
            "value": 0
          }
        ],
        "goal_tags": [
          "mobility",
          "recovery",
          "post_travel"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "mobility_score",
          "pain_level"
        ],
        "prep_required": false,
        "priority": 189,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_yoga_mat",
          "eq_mini_band"
        ],
        "required_provider_ids": [
          "provider_physio_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physiotherapist",
          "trainer"
        ],
        "skip_adjustment": {
          "adjustment": "Member-led mobility session.",
          "trigger": "provider_unavailable"
        },
        "substitution_activity_ids": [
          "act_b03_strength_mobility_post_travel_member"
        ],
        "title": "Mobility and recovery session after travel"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_mobility_post_travel",
          "activity_id": "act_b03_strength_mobility_post_travel_member",
          "activity_type": "fitness",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "recent travel details",
            "current pain/tightness status"
          ],
          "dependencies": [],
          "details": "Self-guided mobility and stretching routine at home using mat and bands to address post-travel fatigue.",
          "duration_minutes": 25,
          "facilitator_type": "member",
          "frequency": {
            "count": 1,
            "preferred_days": [],
            "preferred_time_windows": [
              "18:45-20:00",
              "06:30-08:00",
              "07:15-08:00",
              "19:50-20:30"
            ],
            "type": "post_travel"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Member-led session supports recovery if physio is unavailable.",
              "role": "recovery",
              "unit": "action",
              "value": 0
            }
          ],
          "goal_tags": [
            "mobility",
            "recovery",
            "post_travel",
            "member_led"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "mobility_score",
            "pain_level"
          ],
          "prep_required": false,
          "priority": 190,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_yoga_mat",
            "eq_mini_band"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physiotherapist",
            "trainer"
          ],
          "skip_adjustment": null,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_mobility_post_travel_primary",
          "substitution_notes": "Preserves post-travel recovery intent when provider is unavailable.",
          "substitution_reason_codes": [
            "travel_window",
            "pain_or_fatigue"
          ],
          "title": "Member-led mobility and stretching after travel"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_mobility_post_travel_member",
          "reason": "Member-led session preserves recovery intent when provider is unavailable.",
          "when": "Physiotherapist is unavailable or session must be done independently."
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_physio_assessment_due",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Physio assessment counts toward 3-month review goal when due.",
        "Remote substitution is valid for provider unavailability.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "physio_assessment",
        "pain_review",
        "measurement"
      ],
      "intent": "physio_assessment",
      "primary_activity": {
        "activity_family_id": "b03_strength_physio_assessment_due",
        "activity_id": "act_b03_strength_physio_assessment_due_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "home",
          "gym",
          "clinic"
        ],
        "care_context_required": [
          "recent pain escalation details",
          "current movement plan",
          "recent training load notes",
          "mobility limitation summary"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent pain escalation details",
              "current movement plan",
              "recent training load notes",
              "mobility limitation summary"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "In-person physiotherapist assessment to review knee/back status and update movement plan after travel or when clinically indicated.",
        "duration_minutes": 30,
        "facilitator_type": "physiotherapist",
        "frequency": {
          "preferred_time_windows": [
            "08:00-09:00",
            "18:45-20:00",
            "19:00-20:00"
          ],
          "type": "once",
          "window_days": 7
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Physio assessment counts toward 3-month clinical review goal when due.",
            "role": "measurement",
            "unit": "review",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "physio_assessment",
          "pain_review",
          "measurement"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_005"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "pain_level",
          "mobility_score",
          "provider_notes"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent pain escalation details",
            "current movement plan",
            "recent training load notes",
            "mobility limitation summary"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_yoga_mat",
          "eq_mini_band"
        ],
        "required_provider_ids": [
          "provider_physio_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": null,
        "substitution_activity_ids": [
          "act_b03_strength_physio_assessment_due_remote"
        ],
        "title": "Initial physiotherapist assessment"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_physio_assessment_due",
          "activity_id": "act_b03_strength_physio_assessment_due_remote",
          "activity_type": "consultation",
          "allowed_locations": [
            "home",
            "remote"
          ],
          "care_context_required": [
            "recent pain escalation details",
            "current movement plan",
            "recent training load notes",
            "mobility limitation summary"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent pain escalation details",
                "current movement plan",
                "recent training load notes",
                "mobility limitation summary"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Remote video assessment with physiotherapist to review pain and update movement plan after escalation or travel.",
          "duration_minutes": 30,
          "facilitator_type": "physiotherapist",
          "frequency": {
            "preferred_time_windows": [
              "08:00-09:00",
              "18:45-20:00",
              "19:00-20:00"
            ],
            "type": "once",
            "window_days": 7
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Remote physio assessment counts toward 3-month review goal if in-person is unavailable.",
              "role": "measurement",
              "unit": "review",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "physio_assessment",
            "pain_review",
            "remote"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_005"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "pain_level",
            "mobility_score",
            "provider_notes"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent pain escalation details",
              "current movement plan",
              "recent training load notes",
              "mobility limitation summary"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_physio_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": null,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_physio_assessment_due_primary",
          "substitution_notes": "Preserves assessment intent when in-person provider is unavailable.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "title": "Remote physiotherapist assessment"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_physio_assessment_due_remote",
          "reason": "Remote assessment preserves measurement intent when in-person is not possible.",
          "when": "In-person physiotherapist is unavailable or remote delivery is required."
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_trainer_remote_substitution",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Remote trainer-led session is support-only unless scheduled as core.",
        "Used when in-person session is not possible.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led",
        "remote"
      ],
      "intent": "trainer_strength",
      "primary_activity": {
        "activity_family_id": "b03_strength_trainer_remote_substitution",
        "activity_id": "act_b03_strength_trainer_remote_substitution_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home",
          "remote",
          "travel_hotel"
        ],
        "care_context_required": [
          "current knee/back status",
          "recent physio notes",
          "strength progression log"
        ],
        "dependencies": [],
        "details": "Live remote session with Elyx Performance Trainer using available equipment. Used when in-person session is not possible.",
        "duration_minutes": 45,
        "facilitator_type": "trainer",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "08:00-09:00",
            "18:45-20:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Remote trainer-led session is support-only unless explicitly scheduled as core.",
            "role": "support",
            "unit": "session",
            "value": 0
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "trainer_led",
          "remote"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 193,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [
          "provider_trainer_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": null,
        "substitution_activity_ids": [
          "act_b03_strength_trainer_remote_substitution_async_plan_sub"
        ],
        "title": "Remote trainer-led strength session (as-needed)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_trainer_remote_substitution",
          "activity_id": "act_b03_strength_trainer_remote_substitution_async_plan_sub",
          "activity_type": "fitness",
          "allowed_locations": [
            "remote",
            "home",
            "travel_hotel"
          ],
          "care_context_required": [
            "current knee/back status",
            "recent physio notes",
            "strength progression log"
          ],
          "dependencies": [],
          "details": "Trainer sends a knee-safe strength plan for self-guided completion when a live remote session cannot be scheduled.",
          "duration_minutes": 15,
          "facilitator_type": "trainer",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "08:00-09:00",
              "18:45-20:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
              "role": "support",
              "unit": "session",
              "value": 0
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "trainer_led",
            "remote"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_required": false,
          "priority": 196,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_trainer_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_trainer_remote_substitution_primary",
          "substitution_notes": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "time_conflict"
          ],
          "title": "Async trainer strength plan"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_trainer_remote_substitution_async_plan_sub",
          "reason": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
          "when": "provider_unavailable or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_lower_load_strength_adjustment",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Lower-load session is support-only unless scheduled as core after pain/fatigue.",
        "Remote coach substitution is valid for member needing extra guidance."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "lower_load",
        "pain_fatigue"
      ],
      "intent": "lower_load_strength_substitution",
      "primary_activity": {
        "activity_family_id": "b03_strength_lower_load_strength_adjustment",
        "activity_id": "act_b03_strength_lower_load_strength_adjustment_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent pain/fatigue details"
        ],
        "dependencies": [],
        "details": "Reduced-load strength session at home with focus on safe movement and pain avoidance. Used after pain escalation or fatigue.",
        "duration_minutes": 30,
        "facilitator_type": "member",
        "frequency": {
          "count": 0,
          "preferred_days": [],
          "preferred_time_windows": [
            "06:30-08:00",
            "07:15-08:00",
            "18:45-20:00"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Lower-load session is support-only unless explicitly scheduled as core after pain/fatigue.",
            "role": "support",
            "unit": "session",
            "value": 0
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "lower_load",
          "pain_fatigue"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_005"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "pain_level"
        ],
        "prep_required": false,
        "priority": 194,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": null,
        "substitution_activity_ids": [],
        "title": "Lower-load strength session after pain or fatigue"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_lower_load_strength_adjustment",
          "activity_id": "act_b03_strength_lower_load_strength_adjustment_remote",
          "activity_type": "fitness",
          "allowed_locations": [
            "home",
            "remote"
          ],
          "care_context_required": [
            "recent pain/fatigue details"
          ],
          "dependencies": [],
          "details": "Remote coach provides guidance for lower-load strength session after pain or fatigue.",
          "duration_minutes": 20,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 0,
            "preferred_days": [],
            "preferred_time_windows": [
              "06:30-08:00",
              "07:15-08:00",
              "18:45-20:00"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Remote coach check-in supports lower-load session if member needs guidance.",
              "role": "support",
              "unit": "session",
              "value": 0
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "lower_load",
            "remote"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_005"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "pain_level"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "recent pain/fatigue details"
            ]
          },
          "prep_required": true,
          "priority": 195,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": null,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_lower_load_strength_adjustment_primary",
          "substitution_notes": "Preserves lower-load strength intent with remote coach support after pain/fatigue.",
          "substitution_reason_codes": [
            "lower_load_needed",
            "pain_or_fatigue"
          ],
          "title": "Remote coach check-in for lower-load strength"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_lower_load_strength_adjustment_remote",
          "reason": "Remote coach guidance preserves lower-load strength intent after pain/fatigue.",
          "when": "Member requests remote coach support for lower-load session after pain/fatigue."
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": false,
        "support_counts": true,
        "target_units": 0,
        "unit_label": "travel continuity reviews"
      },
      "family_validation_notes": [
        "Remote check-in is support-only for travel continuity and pain/mobility review.",
        "No substitutions needed; activity is inherently remote and as-needed.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_care_team_followthrough_3month"
      ],
      "goal_tags": [
        "mobility",
        "pain_review",
        "travel_recovery",
        "remote_checkin"
      ],
      "intent": "remote_handoff",
      "primary_activity": {
        "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
        "activity_id": "act_b03_strength_mobility_pain_recovery_checkin_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote",
          "travel_hotel"
        ],
        "care_context_required": [
          "recent travel or skipped session details",
          "current pain/mobility status"
        ],
        "dependencies": [],
        "details": "Physiotherapist check-in to review pain, mobility, and recovery after travel or missed high-load session.",
        "duration_minutes": 15,
        "facilitator_type": "physiotherapist",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "friday"
          ],
          "preferred_time_windows": [
            "16:00-18:00",
            "19:00-20:00"
          ],
          "preferred_week": "third",
          "preferred_weeks": [
            "third",
            "fourth",
            "third"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "goal_id": "goal_travel_resilience",
            "notes": "Remote check-in supports travel continuity and pain/mobility review.",
            "role": "support",
            "unit": "review",
            "value": 1
          }
        ],
        "goal_tags": [
          "mobility",
          "pain_review",
          "travel_recovery",
          "remote_checkin"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_005",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "pain_level",
          "mobility_score",
          "next_actions"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "context_review",
          "required_inputs": [
            "recent travel or skipped session details",
            "current pain/mobility status"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_physio_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physiotherapist",
          "trainer"
        ],
        "skip_adjustment": null,
        "substitution_activity_ids": [
          "act_b03_strength_mobility_pain_recovery_checkin_pain_note_sub"
        ],
        "title": "Physiotherapist recovery check-in after travel or skipped session"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
          "activity_id": "act_b03_strength_mobility_pain_recovery_checkin_pain_note_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent travel or skipped session details",
            "current pain/mobility status"
          ],
          "dependencies": [],
          "details": "Coach or physio reviews pain, fatigue, and travel notes asynchronously and recommends the safest next session option.",
          "duration_minutes": 10,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 0,
            "preferred_time_windows": [
              "20:00-21:30",
              "19:00-20:00"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "goal_id": "goal_travel_resilience",
              "notes": "Preserves pain-aware recovery support when a live check-in cannot fit.",
              "role": "support",
              "unit": "review",
              "value": 1
            }
          ],
          "goal_tags": [
            "mobility",
            "pain_review",
            "travel_recovery",
            "remote_checkin"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_005",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "pain_level",
            "mobility_score",
            "next_actions"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "recent travel or skipped session details",
              "current pain/mobility status"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_physio_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physiotherapist",
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_mobility_pain_recovery_checkin_primary",
          "substitution_notes": "Preserves pain-aware recovery support when a live check-in cannot fit.",
          "substitution_reason_codes": [
            "pain_or_fatigue",
            "remote_delivery_needed"
          ],
          "title": "Async pain recovery note review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_mobility_pain_recovery_checkin_pain_note_sub",
          "reason": "Preserves pain-aware recovery support when a live check-in cannot fit.",
          "when": "pain_or_fatigue or remote_delivery_needed"
        }
      ]
    },
    {
      "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
      "care_domain": "strength_mobility_pain",
      "family_target": {
        "goal_action_id": "ga_strength_sessions_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "sessions"
      },
      "family_validation_notes": [
        "Trainer-unavailable strength alternative is support-only unless scheduled as core.",
        "Remote coach substitution is valid for provider unavailability.",
        "Fallback family must not create extra strength demand; use only when a core strength session is blocked."
      ],
      "goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "provider_unavailable",
        "remote"
      ],
      "intent": "provider_unavailable_strength_substitution",
      "primary_activity": {
        "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
        "activity_id": "act_b03_strength_provider_unavailable_strength_substitution_primary",
        "activity_type": "fitness",
        "allowed_locations": [
          "home",
          "remote",
          "travel_hotel"
        ],
        "care_context_required": [
          "current knee/back status",
          "approved protocol"
        ],
        "dependencies": [],
        "details": "Member-led or remote-guided knee-safe strength session when trainer is unavailable. Follows approved protocol.",
        "duration_minutes": 40,
        "facilitator_type": "member",
        "frequency": {
          "applies_when": [
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "count": 0,
          "preferred_time_windows": [
            "06:30-08:00",
            "07:15-08:00",
            "18:45-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_strength_sessions_weekly",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Trainer-unavailable strength alternative is support-only unless scheduled as core.",
            "role": "support",
            "unit": "session",
            "value": 0
          }
        ],
        "goal_tags": [
          "strength",
          "knee_safe",
          "provider_unavailable",
          "remote"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_005"
        ],
        "load_level": "medium",
        "metrics_to_collect": [
          "completion",
          "sets_reps",
          "RPE",
          "knee_discomfort"
        ],
        "prep_required": false,
        "priority": 197,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": null,
        "substitution_activity_ids": [
          "act_b03_strength_provider_unavailable_strength_substitution_remote"
        ],
        "title": "Knee-safe strength session when trainer unavailable"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
          "activity_id": "act_b03_strength_provider_unavailable_strength_substitution_remote",
          "activity_type": "fitness",
          "allowed_locations": [
            "home",
            "remote",
            "travel_hotel"
          ],
          "care_context_required": [
            "current knee/back status",
            "approved protocol"
          ],
          "dependencies": [],
          "details": "Remote coach provides protocol check and guidance for knee-safe strength session when trainer is unavailable.",
          "duration_minutes": 20,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "applies_when": [
              "provider_unavailable",
              "remote_delivery_needed"
            ],
            "count": 0,
            "preferred_time_windows": [
              "06:30-08:00",
              "07:15-08:00",
              "18:45-20:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_strength_sessions_weekly",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Remote coach check-in supports member-led session if trainer is unavailable.",
              "role": "support",
              "unit": "session",
              "value": 0
            }
          ],
          "goal_tags": [
            "strength",
            "knee_safe",
            "provider_unavailable",
            "remote"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_005"
          ],
          "load_level": "medium",
          "metrics_to_collect": [
            "completion",
            "sets_reps",
            "RPE",
            "knee_discomfort"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "current knee/back status",
              "approved protocol"
            ]
          },
          "prep_required": true,
          "priority": 198,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": null,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b03_strength_provider_unavailable_strength_substitution_primary",
          "substitution_notes": "Preserves knee-safe strength intent with remote coach support when trainer is unavailable.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "remote_delivery_needed",
            "time_conflict"
          ],
          "title": "Remote coach check-in for trainer-unavailable strength"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b03_strength_provider_unavailable_strength_substitution_remote",
          "reason": "Remote coach guidance preserves knee-safe strength intent when trainer is unavailable.",
          "when": "Trainer is unavailable or remote delivery is required."
        }
      ]
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_home",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 2,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a home-based evening mobility/recovery session for sleep support.",
        "Substitution is a remote-guided, shorter session for time or provider constraints.",
        "Both count toward the weekly recovery/sleep goal.",
        "Core recovery target is 4 actions/week across evening mobility + sleep wind-down families."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly"
      ],
      "goal_tags": [
        "sleep_quality",
        "mobility",
        "recovery",
        "evening_routine"
      ],
      "intent": "evening_recovery",
      "primary_activity": {
        "activity_family_id": "b04_recovery_evening_mobility_home",
        "activity_id": "act_b04_recovery_evening_mobility_home_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent sleep duration",
          "mobility limitation summary"
        ],
        "dependencies": [],
        "details": "Guided mobility, stretching, or foam rolling at home to support sleep quality and recovery. Can be member-led or with remote coach input.",
        "duration_minutes": 30,
        "facilitator_type": "self_or_remote_coach",
        "frequency": {
          "count": 2,
          "preferred_days": [
            "monday",
            "thursday"
          ],
          "preferred_time_windows": [
            "20:00-21:30"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Directly supports weekly recovery/sleep goal.",
            "role": "recovery",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "sleep_quality",
          "mobility",
          "recovery"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sleep_quality_next_morning",
          "mobility_score"
        ],
        "prep_required": false,
        "priority": 261,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_yoga_mat",
          "eq_bodyweight"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member is traveling or has late work obligations, use travel/remote variant."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_evening_mobility_home_sub_time_conflict"
        ],
        "title": "Evening home-based mobility and recovery session"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_evening_mobility_home",
          "activity_id": "act_b04_recovery_evening_mobility_home_sub_time_conflict",
          "activity_type": "therapy",
          "allowed_locations": [
            "home",
            "remote"
          ],
          "care_context_required": [
            "recent sleep duration"
          ],
          "dependencies": [],
          "details": "Shorter, remote-guided mobility or stretching session for evenings when home routine is not feasible.",
          "duration_minutes": 20,
          "facilitator_type": "remote_coach",
          "frequency": {
            "count": 2,
            "preferred_days": [
              "monday",
              "thursday"
            ],
            "preferred_time_windows": [
              "21:00-22:15"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Counts as recovery if primary is blocked by time or provider constraints.",
              "role": "recovery",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "sleep_quality",
            "mobility",
            "recovery"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sleep_quality_next_morning"
          ],
          "prep_required": false,
          "priority": 262,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_yoga_mat"
          ],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed": true,
            "reason": "If member is traveling, use travel-specific variant."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_evening_mobility_home_primary",
          "substitution_notes": "Preserves evening recovery intent when home routine is not feasible.",
          "substitution_reason_codes": [
            "time_conflict",
            "provider_unavailable"
          ],
          "title": "Remote-guided evening mobility session"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_evening_mobility_home_sub_time_conflict",
          "reason": "Shorter remote-guided session maintains recovery intent with less time and location constraint.",
          "when": "member has late work obligations or is unable to complete full home routine"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      },
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_travel",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a hotel-based evening mobility/recovery session for travel windows.",
        "Substitution is an in-room session for facility unavailability or late arrival.",
        "Both are travel adaptations and count toward recovery goals during travel weeks because fatigue management is higher priority while travelling."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "travel",
        "mobility",
        "recovery",
        "evening_routine"
      ],
      "intent": "evening_recovery",
      "primary_activity": {
        "activity_family_id": "b04_recovery_evening_mobility_travel",
        "activity_id": "act_b04_recovery_evening_mobility_travel_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel fatigue",
          "recent sleep duration"
        ],
        "dependencies": [],
        "details": "Travel-adapted mobility or stretching session in hotel room or gym, supporting sleep and recovery during travel.",
        "duration_minutes": 20,
        "facilitator_type": "self_or_remote_coach",
        "frequency": {
          "count": 3,
          "preferred_time_windows": [
            "20:00-21:30"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Travel mobility counts toward weekly recovery because fatigue reduction is especially important during travel weeks.",
            "role": "recovery",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "goal_id": "goal_travel_resilience",
            "notes": "Supports travel continuity.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "travel",
          "mobility",
          "recovery"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sleep_quality_next_morning"
        ],
        "prep_required": false,
        "priority": 263,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_mini_band",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If hotel gym is unavailable, use in-room variant."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_evening_mobility_travel_sub_facility_unavailable"
        ],
        "title": "Hotel-based evening mobility and recovery session"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_evening_mobility_travel",
          "activity_id": "act_b04_recovery_evening_mobility_travel_sub_facility_unavailable",
          "activity_type": "therapy",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel fatigue"
          ],
          "dependencies": [],
          "details": "Short in-room mobility or stretching session when hotel gym is unavailable or late arrival limits options.",
          "duration_minutes": 15,
          "facilitator_type": "self",
          "frequency": {
            "count": 3,
            "preferred_time_windows": [
              "21:00-22:15"
            ],
            "type": "travel_window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "value": 1
            }
          ],
          "goal_tags": [
            "travel",
            "mobility",
            "recovery"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion"
          ],
          "prep_required": false,
          "priority": 264,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight",
            "eq_mini_band"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed": true,
            "reason": "If member is fatigued or arrives late, use this variant."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_evening_mobility_travel_primary",
          "substitution_notes": "Preserves recovery intent when hotel gym or facilities are unavailable.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable"
          ],
          "title": "In-room mobility and stretching session (travel)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_evening_mobility_travel_sub_facility_unavailable",
          "reason": "In-room session ensures recovery intent is preserved despite facility constraints.",
          "when": "hotel gym or facilities are unavailable or member arrives late"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_sleep_routine_support",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 2,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a home-based sleep wind-down routine.",
        "No substitutions; counts toward weekly recovery/sleep goal.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Core recovery target is 4 actions/week across evening mobility + sleep wind-down families."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly"
      ],
      "goal_tags": [
        "sleep_quality",
        "evening_routine",
        "wind_down"
      ],
      "intent": "sleep_routine",
      "primary_activity": {
        "activity_family_id": "b04_recovery_sleep_routine_support",
        "activity_id": "act_b04_recovery_sleep_routine_support_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent sleep duration"
        ],
        "dependencies": [],
        "details": "Guided wind-down protocol including light stretching, breathwork, and screen cutoff to support sleep onset.",
        "duration_minutes": 20,
        "facilitator_type": "self",
        "frequency": {
          "count": 2,
          "preferred_days": [
            "tuesday",
            "sunday"
          ],
          "preferred_time_windows": [
            "22:00-22:30"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Directly supports weekly recovery/sleep goal.",
            "role": "recovery",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "sleep_quality",
          "evening_routine"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sleep_onset_time",
          "sleep_quality_next_morning"
        ],
        "prep_required": false,
        "priority": 265,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [],
        "skip_adjustment": {
          "allowed": false
        },
        "substitution_activity_ids": [
          "act_b04_recovery_sleep_routine_support_hotel_wind_down_sub"
        ],
        "title": "Home-based sleep wind-down routine"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_sleep_routine_support",
          "activity_id": "act_b04_recovery_sleep_routine_support_hotel_wind_down_sub",
          "activity_type": "therapy",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "recent sleep duration"
          ],
          "dependencies": [],
          "details": "Hotel-room version of the wind-down protocol with breathwork, light mobility, and screen cutoff when Marcus is travelling.",
          "duration_minutes": 20,
          "facilitator_type": "self",
          "frequency": {
            "count": 2,
            "preferred_days": [
              "tuesday",
              "sunday"
            ],
            "preferred_time_windows": [
              "22:00-22:30"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Preserves sleep-routine intent when Marcus is away from home.",
              "role": "recovery",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "sleep_quality",
            "evening_routine"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "sleep_onset_time",
            "sleep_quality_next_morning"
          ],
          "prep_required": false,
          "priority": 268,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_yoga_mat"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_sleep_routine_support_primary",
          "substitution_notes": "Preserves sleep-routine intent when Marcus is away from home.",
          "substitution_reason_codes": [
            "travel_window"
          ],
          "title": "Hotel sleep wind-down routine"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_sleep_routine_support_hotel_wind_down_sub",
          "reason": "Preserves sleep-routine intent when Marcus is away from home.",
          "when": "travel_window"
        }
      ],
      "weekly_fitness_validation": {
        "aerobic_sessions_target_per_week": 2,
        "avoid_walk_only_weeks": true,
        "recovery_actions_target_per_week": 4,
        "strength_sessions_target_per_week": 2,
        "walk_only_week_requires_reason": true,
        "walking_breaks_count_as_strength": false
      },
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a post-travel fatigue recovery session at home.",
        "Substitution is a shorter, lower-load session for severe fatigue or pain.",
        "Both are travel adaptations and count toward recovery goals during travel weeks because fatigue management is higher priority while travelling."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly",
        "ga_behavior_coaching_weekly"
      ],
      "goal_tags": [
        "post_travel",
        "fatigue",
        "recovery",
        "mobility"
      ],
      "intent": "post_travel_recovery",
      "primary_activity": {
        "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
        "activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "travel fatigue",
          "pain escalation"
        ],
        "dependencies": [],
        "details": "Mobility, stretching, and guided recovery session at home after return from travel over 3 hours.",
        "duration_minutes": 25,
        "facilitator_type": "self_or_remote_coach",
        "frequency": {
          "count": 3,
          "preferred_time_windows": [
            "18:45-20:00"
          ],
          "type": "post_travel"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Post-travel adaptation; does not count toward normal-week denominator.",
            "role": "recovery",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_behavior_coaching_weekly",
            "goal_id": "goal_travel_resilience",
            "notes": "Supports travel continuity.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "post_travel",
          "fatigue",
          "recovery"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "fatigue_score",
          "mobility_score"
        ],
        "prep_required": false,
        "priority": 266,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_yoga_mat",
          "eq_bodyweight"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member experiences pain or severe fatigue, use lower-load variant."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_post_travel_fatigue_adjustment_sub_fatigue"
        ],
        "title": "Post-travel fatigue recovery session at home"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
          "activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_sub_fatigue",
          "activity_type": "therapy",
          "allowed_locations": [
            "home"
          ],
          "care_context_required": [
            "travel fatigue"
          ],
          "dependencies": [],
          "details": "Shortened, gentle stretching or breathwork session for severe fatigue or pain after travel.",
          "duration_minutes": 10,
          "facilitator_type": "self",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "19:30-20:00"
            ],
            "type": "post_travel"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "value": 1
            }
          ],
          "goal_tags": [
            "post_travel",
            "fatigue",
            "recovery"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion"
          ],
          "prep_required": false,
          "priority": 267,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [],
          "skip_adjustment": {
            "allowed": true,
            "reason": "If member is too fatigued for full session, use this variant."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_primary",
          "substitution_notes": "Preserves recovery intent when member is too fatigued for full session.",
          "substitution_reason_codes": [
            "travel_window",
            "pain_or_fatigue"
          ],
          "title": "Short fatigue-adjusted recovery session (post-travel)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_sub_fatigue",
          "reason": "Shorter session maintains recovery focus with lower load.",
          "when": "member experiences severe fatigue or pain after travel"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_breathwork_support",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a breathwork or stress regulation session for sleep/recovery support.",
        "Support-only; does not count toward core goal.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly"
      ],
      "goal_tags": [
        "breathwork",
        "stress_regulation",
        "fatigue_support"
      ],
      "intent": "fatigue_adjustment",
      "primary_activity": {
        "activity_family_id": "b04_recovery_breathwork_support",
        "activity_id": "act_b04_recovery_breathwork_support_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent stressors"
        ],
        "dependencies": [],
        "details": "Guided or self-led breathwork, mindfulness, or stress regulation session to support sleep and recovery.",
        "duration_minutes": 10,
        "facilitator_type": "self",
        "frequency": {
          "count": 0,
          "preferred_time_windows": [
            "20:30-22:30"
          ],
          "type": "as_needed"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Support-only; does not count toward core goal.",
            "role": "support",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "breathwork",
          "stress_regulation"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "stress_score"
        ],
        "prep_required": false,
        "priority": 268,
        "raw_clinical_data_required": false,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": true,
        "share_with_provider_types": [],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member is traveling, can be performed in hotel room."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_breathwork_support_audio_guided_sub"
        ],
        "title": "Breathwork or stress regulation session"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_breathwork_support",
          "activity_id": "act_b04_recovery_breathwork_support_audio_guided_sub",
          "activity_type": "therapy",
          "allowed_locations": [
            "home",
            "travel_hotel",
            "remote"
          ],
          "care_context_required": [
            "recent stressors"
          ],
          "dependencies": [],
          "details": "Self-guided breathwork using a short audio protocol when coach support or a quiet home window is not available.",
          "duration_minutes": 10,
          "facilitator_type": "self",
          "frequency": {
            "count": 0,
            "preferred_time_windows": [
              "20:30-22:30"
            ],
            "type": "as_needed"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Preserves stress-regulation intent with a lower-friction delivery mode.",
              "role": "support",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "breathwork",
            "stress_regulation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "stress_score"
          ],
          "prep_required": false,
          "priority": 271,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": true,
          "share_with_provider_types": [],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_breathwork_support_primary",
          "substitution_notes": "Preserves stress-regulation intent with a lower-friction delivery mode.",
          "substitution_reason_codes": [
            "time_conflict",
            "remote_delivery_needed"
          ],
          "title": "Audio-guided breathwork session"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_breathwork_support_audio_guided_sub",
          "reason": "Preserves stress-regulation intent with a lower-friction delivery mode.",
          "when": "time_conflict or remote_delivery_needed"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": false,
        "support_counts": true,
        "target_units": 0,
        "unit_label": "travel continuity reviews"
      },
      "family_validation_notes": [
        "Primary activity is a remote coach check-in for recovery and sleep during travel.",
        "Support-only; does not count as a recovery action.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
      ],
      "goal_action_ids": [
        "ga_care_team_followthrough_3month"
      ],
      "goal_tags": [
        "travel",
        "remote_support",
        "recovery_checkin"
      ],
      "intent": "remote_handoff",
      "primary_activity": {
        "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
        "activity_id": "act_b04_recovery_remote_coach_recovery_checkin_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote",
          "travel_hotel"
        ],
        "care_context_required": [
          "travel fatigue",
          "recent sleep duration"
        ],
        "dependencies": [],
        "details": "Remote check-in with Elyx coach to review recovery, sleep, and fatigue during travel windows.",
        "duration_minutes": 15,
        "facilitator_type": "remote_coach",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "19:00-20:00"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "goal_id": "goal_travel_resilience",
            "notes": "Support-only; does not count as a recovery action.",
            "role": "support",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "travel",
          "remote_support"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "fatigue_score",
          "sleep_quality"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "context_review",
          "required_inputs": [
            "travel fatigue",
            "recent sleep duration"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member is unavailable, coach may send asynchronous check-in."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_remote_coach_recovery_checkin_async_sleep_note_sub"
        ],
        "title": "Remote coach check-in for recovery and sleep (travel)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
          "activity_id": "act_b04_recovery_remote_coach_recovery_checkin_async_sleep_note_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "travel fatigue",
            "recent sleep duration"
          ],
          "dependencies": [],
          "details": "Remote coach reviews sleep notes and travel context asynchronously, then updates the recovery plan.",
          "duration_minutes": 10,
          "facilitator_type": "remote_coach",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "19:00-20:00"
            ],
            "type": "travel_window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "goal_id": "goal_travel_resilience",
              "notes": "Preserves recovery check-in support when live coach availability is limited.",
              "role": "support",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "travel",
            "remote_support"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "fatigue_score",
            "sleep_quality"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "context_review",
            "required_inputs": [
              "travel fatigue",
              "recent sleep duration"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "remote_coach_pool"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_remote_coach_recovery_checkin_primary",
          "substitution_notes": "Preserves recovery check-in support when live coach availability is limited.",
          "substitution_reason_codes": [
            "time_conflict",
            "travel_window"
          ],
          "title": "Async sleep recovery note review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_remote_coach_recovery_checkin_async_sleep_note_sub",
          "reason": "Preserves recovery check-in support when live coach availability is limited.",
          "when": "time_conflict or travel_window"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_evening_routine_travel",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a hotel-based evening sleep routine for travel windows.",
        "Substitution is a shortened routine for late arrival or high fatigue.",
        "Both are travel adaptations and do not count toward normal-week denominator."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly"
      ],
      "goal_tags": [
        "travel",
        "sleep_quality",
        "evening_routine"
      ],
      "intent": "sleep_routine",
      "primary_activity": {
        "activity_family_id": "b04_recovery_evening_routine_travel",
        "activity_id": "act_b04_recovery_evening_routine_travel_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "travel_hotel"
        ],
        "care_context_required": [
          "travel fatigue"
        ],
        "dependencies": [],
        "details": "Adapted wind-down protocol for hotel environment: screen cutoff, light stretching, and breathwork to support sleep onset during travel.",
        "duration_minutes": 15,
        "facilitator_type": "self",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "22:00-22:30"
          ],
          "type": "travel_window"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Travel sleep routine counts toward weekly recovery because fatigue reduction is especially important during travel weeks.",
            "role": "recovery",
            "unit": "activity",
            "value": 1
          }
        ],
        "goal_tags": [
          "travel",
          "sleep_quality"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sleep_onset_time"
        ],
        "prep_required": false,
        "priority": 270,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member is fatigued or arrives late, use shorter variant."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_evening_routine_travel_sub_facility_unavailable"
        ],
        "title": "Hotel-based evening sleep routine"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_evening_routine_travel",
          "activity_id": "act_b04_recovery_evening_routine_travel_sub_facility_unavailable",
          "activity_type": "therapy",
          "allowed_locations": [
            "travel_hotel"
          ],
          "care_context_required": [
            "travel fatigue"
          ],
          "dependencies": [],
          "details": "Very brief wind-down protocol for late arrival or high fatigue: screen cutoff and 3-minute breathwork.",
          "duration_minutes": 8,
          "facilitator_type": "self",
          "frequency": {
            "count": 3,
            "preferred_time_windows": [
              "22:15-22:30"
            ],
            "type": "travel_window"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Short hotel wind-down counts toward weekly recovery when travel fatigue makes the full routine impractical.",
              "role": "recovery",
              "unit": "activity",
              "value": 1
            }
          ],
          "goal_tags": [
            "travel",
            "sleep_quality"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion"
          ],
          "prep_required": false,
          "priority": 271,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [],
          "skip_adjustment": {
            "allowed": true,
            "reason": "If member is too fatigued for full routine, use this variant."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_evening_routine_travel_primary",
          "substitution_notes": "Preserves sleep routine intent when member is too fatigued or arrives late.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable"
          ],
          "title": "Shortened hotel wind-down routine (travel)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_evening_routine_travel_sub_facility_unavailable",
          "reason": "Shortened routine maintains sleep support intent with minimal time.",
          "when": "member is too fatigued or arrives late during travel"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
      "care_domain": "recovery_sleep_stress",
      "family_target": {
        "goal_action_id": "ga_sleep_recovery_weekly",
        "period": "weekly",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "actions"
      },
      "family_validation_notes": [
        "Primary activity is a load adjustment and recovery protocol after poor sleep or fatigue.",
        "Substitution is a short mobility or breathwork session for lower-load need.",
        "Both are recovery adaptations and do not count as core actions.",
        "Poor-sleep load adjustment is fallback logic and must not create four extra recovery actions."
      ],
      "goal_action_ids": [
        "ga_sleep_recovery_weekly"
      ],
      "goal_tags": [
        "load_adjustment",
        "poor_sleep",
        "fatigue",
        "recovery"
      ],
      "intent": "poor_sleep_load_adjustment",
      "primary_activity": {
        "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
        "activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_primary",
        "activity_type": "therapy",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent sleep duration",
          "fatigue"
        ],
        "dependencies": [],
        "details": "Explicit protocol to lower planned training load and insert recovery/mobility after poor sleep, pain, or fatigue.",
        "duration_minutes": 15,
        "facilitator_type": "self_or_remote_coach",
        "frequency": {
          "applies_when": [
            "poor_sleep",
            "pain_or_fatigue",
            "lower_load_needed"
          ],
          "count": 0,
          "preferred_time_windows": [
            "06:30-08:00",
            "18:45-20:00"
          ],
          "type": "constraint_scoped"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_sleep_recovery_weekly",
            "goal_id": "goal_sleep_recovery",
            "notes": "Recovery logic for poor sleep or fatigue; does not count as core action.",
            "role": "recovery",
            "unit": "activity",
            "value": 0
          }
        ],
        "goal_tags": [
          "load_adjustment",
          "poor_sleep",
          "recovery"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "sleep_quality_next_morning",
          "fatigue_score"
        ],
        "prep_required": false,
        "priority": 272,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [
          "eq_bodyweight",
          "eq_yoga_mat"
        ],
        "required_provider_ids": [],
        "same_day_repeat_allowed": true,
        "share_with_provider_types": [
          "remote_coach_pool"
        ],
        "skip_adjustment": {
          "allowed": true,
          "reason": "If member is traveling, use travel-compatible variant."
        },
        "substitution_activity_ids": [
          "act_b04_recovery_load_adjustment_after_poor_sleep_sub_lower_load"
        ],
        "title": "Load adjustment and recovery protocol after poor sleep"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
          "activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_sub_lower_load",
          "activity_type": "therapy",
          "allowed_locations": [
            "home",
            "remote"
          ],
          "care_context_required": [
            "recent sleep duration"
          ],
          "dependencies": [],
          "details": "Short mobility or breathwork session to replace planned higher-load activity after poor sleep or fatigue.",
          "duration_minutes": 8,
          "facilitator_type": "self",
          "frequency": {
            "applies_when": [
              "lower_load_needed",
              "pain_or_fatigue",
              "time_conflict"
            ],
            "count": 0,
            "preferred_time_windows": [
              "07:00-07:30",
              "19:00-19:30"
            ],
            "type": "constraint_scoped"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_sleep_recovery_weekly",
              "goal_id": "goal_sleep_recovery",
              "notes": "Lower-load substitution for poor sleep/fatigue; does not count as core action.",
              "role": "recovery",
              "unit": "activity",
              "value": 0
            }
          ],
          "goal_tags": [
            "load_adjustment",
            "poor_sleep",
            "recovery"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion"
          ],
          "prep_required": false,
          "priority": 273,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [
            "eq_bodyweight"
          ],
          "required_provider_ids": [],
          "same_day_repeat_allowed": true,
          "share_with_provider_types": [],
          "skip_adjustment": {
            "allowed": true,
            "reason": "If member is traveling, use travel-compatible variant."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_primary",
          "substitution_notes": "Preserves recovery intent when higher-load activity is not appropriate.",
          "substitution_reason_codes": [
            "lower_load_needed",
            "pain_or_fatigue",
            "time_conflict"
          ],
          "title": "Short mobility or breathwork session after poor sleep"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_sub_lower_load",
          "reason": "Shorter, lower-load session maintains recovery intent.",
          "when": "member has poor sleep, pain, or fatigue and cannot complete planned higher-load activity"
        }
      ],
      "weekly_recovery_target_metadata": {
        "core_counting_families": [
          "b04_recovery_evening_mobility_home",
          "b04_recovery_sleep_routine_support"
        ],
        "fallback_families_do_not_create_extra_demand": true,
        "target_actions_per_week": 4
      }
    },
    {
      "activity_family_id": "b05_clinical_lab_draw_due_week",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Lab draw is only possible at the Singapore clinic; travel or facility unavailability triggers rescheduling.",
        "Metabolic review lab draw requires at least 8 hours fasting.",
        "No breakfast, caloric beverage, caloric supplement, or other caloric meal may be scheduled before the lab draw on the same calendar day.",
        "If breakfast is skipped for the lab draw, the generated calendar row must include skip_reason_code=fasting_lab_same_morning."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "measurement",
        "metabolic_review",
        "lab_due_week"
      ],
      "intent": "lab",
      "primary_activity": {
        "activity_family_id": "b05_clinical_lab_draw_due_week",
        "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "clinic"
        ],
        "care_context_required": [
          "recent medication/supplement list",
          "last meal time",
          "fasting start time",
          "current metabolic goal"
        ],
        "dependencies": [
          {
            "must_happen": "before",
            "notes": "Member must fast for at least 8 hours before the lab draw.",
            "offset_minutes_min": 480,
            "type": "fasting"
          },
          {
            "blocked_activity_types": [
              "food"
            ],
            "blocked_goal_tags": [
              "breakfast",
              "structured_meal"
            ],
            "blocked_meal_slots": [
              "breakfast"
            ],
            "calendar_skip_reason_required": true,
            "must_happen": "before",
            "notes": "Do not schedule breakfast or any caloric food activity before the fasting lab draw on the same day.",
            "scope": "same_calendar_day_before_lab_draw",
            "skip_reason_code": "fasting_lab_same_morning",
            "type": "same_day_meal_exclusion"
          }
        ],
        "details": "Fasting blood panel for metabolic markers at the Elyx Partner Clinic. Requires at least 8 hours fasting. Do not schedule breakfast, caloric beverages, caloric supplements, or any caloric meal before the lab draw on the same day.",
        "duration_minutes": 30,
        "facilitator_type": "phlebotomist",
        "fasting_hours_required": 8,
        "fasting_metadata": {
          "allowed_during_fast": [
            "water",
            "non-caloric prescribed medication only if approved by clinician"
          ],
          "confirmation_fields": [
            "last_meal_time",
            "fasting_start_time",
            "fasting_confirmed"
          ],
          "fasting_hours_required": 8,
          "fasting_required": true,
          "fasting_window_minutes_min": 480,
          "not_allowed_before_lab_same_day": [
            "breakfast",
            "caloric beverages",
            "caloric supplements",
            "caloric meals"
          ],
          "same_day_meal_rule": {
            "calendar_skip_reason_required": true,
            "no_caloric_food_before_lab": true,
            "skip_meal_slots_before_lab": [
              "breakfast"
            ],
            "skip_reason_code": "fasting_lab_same_morning",
            "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
          }
        },
        "fasting_required": true,
        "frequency": {
          "preferred_time_windows": [
            "07:30-10:00"
          ],
          "type": "once",
          "window_days": 7
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Lab draw is required for clinical review and counts toward the 3-month review target.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "lab",
          "metabolic_review"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "fasting_confirmed",
          "last_meal_time",
          "lab_panel_collected"
        ],
        "prep_metadata": {
          "calendar_skip_reason_required_for_blocked_breakfast": true,
          "due_before_minutes": 720,
          "fasting_hours_required": 8,
          "fasting_required": true,
          "missing_data_policy": "reschedule_lab_draw_until_fasting_confirmed",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "fasting_lab_prep",
          "required_inputs": [
            "recent medication/supplement list",
            "last meal time",
            "fasting start time",
            "current metabolic goal"
          ],
          "requires_no_caloric_meal_before_activity": true,
          "skip_reason_code": "fasting_lab_same_morning"
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": true,
        "remote_allowed": false,
        "required_equipment_ids": [
          "eq_lab_kits"
        ],
        "required_provider_ids": [
          "provider_lab_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_lab_draw_due_week_sub_travel"
        ],
        "title": "Lab draw for metabolic review (clinic, due week)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_lab_draw_due_week",
          "activity_id": "act_b05_clinical_lab_draw_due_week_sub_travel",
          "activity_type": "consultation",
          "allowed_locations": [
            "clinic"
          ],
          "care_context_required": [
            "recent medication/supplement list",
            "last meal time",
            "fasting start time",
            "current metabolic goal"
          ],
          "dependencies": [
            {
              "must_happen": "before",
              "notes": "Member must fast for at least 8 hours before the lab draw.",
              "offset_minutes_min": 480,
              "type": "fasting"
            },
            {
              "blocked_activity_types": [
                "food"
              ],
              "blocked_goal_tags": [
                "breakfast",
                "structured_meal"
              ],
              "blocked_meal_slots": [
                "breakfast"
              ],
              "calendar_skip_reason_required": true,
              "must_happen": "before",
              "notes": "Do not schedule breakfast or any caloric food activity before the fasting lab draw on the same day.",
              "scope": "same_calendar_day_before_lab_draw",
              "skip_reason_code": "fasting_lab_same_morning",
              "type": "same_day_meal_exclusion"
            }
          ],
          "details": "Lab draw rescheduled to the nearest valid morning window before or after travel. Requires at least 8 hours fasting. Do not schedule breakfast, caloric beverages, caloric supplements, or any caloric meal before the lab draw on the same day.",
          "duration_minutes": 30,
          "facilitator_type": "phlebotomist",
          "fasting_hours_required": 8,
          "fasting_metadata": {
            "allowed_during_fast": [
              "water",
              "non-caloric prescribed medication only if approved by clinician"
            ],
            "confirmation_fields": [
              "last_meal_time",
              "fasting_start_time",
              "fasting_confirmed"
            ],
            "fasting_hours_required": 8,
            "fasting_required": true,
            "fasting_window_minutes_min": 480,
            "not_allowed_before_lab_same_day": [
              "breakfast",
              "caloric beverages",
              "caloric supplements",
              "caloric meals"
            ],
            "same_day_meal_rule": {
              "calendar_skip_reason_required": true,
              "no_caloric_food_before_lab": true,
              "skip_meal_slots_before_lab": [
                "breakfast"
              ],
              "skip_reason_code": "fasting_lab_same_morning",
              "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
            }
          },
          "fasting_required": true,
          "frequency": {
            "preferred_time_windows": [
              "07:30-10:00"
            ],
            "type": "once",
            "window_days": 14
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Lab draw rescheduled before or after travel to preserve clinical review continuity.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "lab",
            "travel_adaptation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "fasting_confirmed",
            "last_meal_time",
            "lab_panel_collected"
          ],
          "prep_metadata": {
            "calendar_skip_reason_required_for_blocked_breakfast": true,
            "due_before_minutes": 720,
            "fasting_hours_required": 8,
            "fasting_required": true,
            "missing_data_policy": "reschedule_lab_draw_until_fasting_confirmed",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "fasting_lab_prep",
            "required_inputs": [
              "recent medication/supplement list",
              "last meal time",
              "fasting start time",
              "current metabolic goal"
            ],
            "requires_no_caloric_meal_before_activity": true,
            "skip_reason_code": "fasting_lab_same_morning"
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": true,
          "remote_allowed": false,
          "required_equipment_ids": [
            "eq_lab_kits"
          ],
          "required_provider_ids": [
            "provider_lab_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "dietitian"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "substitution_notes": "Preserves lab measurement intent by rescheduling outside travel or clinic unavailability.",
          "substitution_reason_codes": [
            "travel_window",
            "facility_unavailable",
            "time_conflict"
          ],
          "title": "Lab draw rescheduled (pre/post travel)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_lab_draw_due_week_sub_travel",
          "reason": "Reschedules lab draw to before or after travel, preserving measurement intent and fasting requirement.",
          "when": "Lab due week overlaps with travel or clinic is unavailable."
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_physician_review_due_week",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Physician review must follow lab completion; remote review is valid when travel or provider constraints exist.",
        "Counts toward the 3-month clinical review target.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "measurement",
        "physician_review",
        "lab_followup"
      ],
      "intent": "physician_review",
      "primary_activity": {
        "activity_family_id": "b05_clinical_physician_review_due_week",
        "activity_id": "act_b05_clinical_physician_review_due_week_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "clinic"
        ],
        "care_context_required": [
          "recent lab results",
          "current medication/supplement list",
          "metabolic goal summary",
          "recent symptoms or adverse events"
        ],
        "dependencies": [
          {
            "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
            "must_happen": "before",
            "notes": "Physician review must occur after lab results are available.",
            "offset_minutes_min": 60,
            "type": "prerequisite_activity"
          },
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent lab results",
              "current medication/supplement list",
              "metabolic goal summary",
              "recent symptoms or adverse events"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "In-person physician review at the clinic after labs are completed. Focus on metabolic markers and protocol updates.",
        "duration_minutes": 30,
        "facilitator_type": "physician",
        "frequency": {
          "preferred_time_windows": [
            "09:00-11:00",
            "19:00-20:00"
          ],
          "type": "once",
          "window_days": 7
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Physician review after labs counts toward the 3-month clinical review target.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "physician_review",
          "lab_followup"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "provider_notes",
          "next_actions"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent lab results",
            "current medication/supplement list",
            "metabolic goal summary",
            "recent symptoms or adverse events"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": true,
        "remote_allowed": false,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_physician_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "dietitian",
          "trainer"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_physician_review_due_week_sub_remote"
        ],
        "title": "Physician review after labs (clinic, due week)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_physician_review_due_week",
          "activity_id": "act_b05_clinical_physician_review_due_week_sub_remote",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent lab results",
            "current medication/supplement list",
            "metabolic goal summary",
            "recent symptoms or adverse events"
          ],
          "dependencies": [
            {
              "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
              "must_happen": "before",
              "notes": "Remote review must occur after lab results are available.",
              "offset_minutes_min": 60,
              "type": "prerequisite_activity"
            },
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent lab results",
                "current medication/supplement list",
                "metabolic goal summary",
                "recent symptoms or adverse events"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Remote video or phone review with physician after labs, used when travel or provider unavailability prevents in-person review.",
          "duration_minutes": 25,
          "facilitator_type": "physician",
          "frequency": {
            "preferred_time_windows": [
              "09:00-11:00",
              "18:00-19:00",
              "19:00-20:00"
            ],
            "type": "once",
            "window_days": 7
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Remote physician review preserves the clinical review target when in-person is not possible.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "physician_review",
            "remote_adaptation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "provider_notes",
            "next_actions"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent lab results",
              "current medication/supplement list",
              "metabolic goal summary",
              "recent symptoms or adverse events"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": true,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_physician_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "dietitian",
            "trainer"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_physician_review_due_week_primary",
          "substitution_notes": "Preserves physician review intent when in-person is not feasible due to travel or provider constraints.",
          "substitution_reason_codes": [
            "travel_window",
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "title": "Remote physician review after labs"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_physician_review_due_week_sub_remote",
          "reason": "Remote review preserves the clinical review target and allows timely lab follow-up.",
          "when": "Travel or provider unavailability prevents in-person review."
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_dietitian_review_monthly",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Monthly dietitian review is required for ongoing nutrition adaptation.",
        "Remote review is valid when provider or member is unavailable for in-person.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "measurement",
        "dietitian_review",
        "nutrition_review"
      ],
      "intent": "dietitian_review",
      "primary_activity": {
        "activity_family_id": "b05_clinical_dietitian_review_monthly",
        "activity_id": "act_b05_clinical_dietitian_review_monthly_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "home"
        ],
        "care_context_required": [
          "recent meal logs",
          "travel meal summary",
          "current nutrition goal",
          "current supplement list",
          "recent CGM or fasting glucose notes if available"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent meal logs",
              "travel meal summary",
              "current nutrition goal",
              "current supplement list",
              "recent CGM or fasting glucose notes if available"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Monthly review with dietitian to adapt nutrition plan, review meal adherence, and address travel or restaurant meal strategies.",
        "duration_minutes": 25,
        "facilitator_type": "dietitian",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "tuesday"
          ],
          "preferred_time_windows": [
            "10:00-11:00",
            "18:00-19:00",
            "19:00-20:00"
          ],
          "preferred_week": "second",
          "preferred_weeks": [
            "second",
            "first",
            "second"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Monthly dietitian review counts toward the 3-month clinical review target.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "dietitian_review",
          "nutrition_review"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "provider_notes",
          "nutrition_adherence"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent meal logs",
            "travel meal summary",
            "current nutrition goal",
            "current supplement list",
            "recent CGM or fasting glucose notes if available"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_dietitian_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "trainer"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_dietitian_review_monthly_sub_remote"
        ],
        "title": "Monthly dietitian review (home or remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_dietitian_review_monthly",
          "activity_id": "act_b05_clinical_dietitian_review_monthly_sub_remote",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote",
            "travel_hotel"
          ],
          "care_context_required": [
            "recent meal logs",
            "travel meal summary",
            "current nutrition goal",
            "current supplement list",
            "recent CGM or fasting glucose notes if available"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent meal logs",
                "travel meal summary",
                "current nutrition goal",
                "current supplement list",
                "recent CGM or fasting glucose notes if available"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Remote video or phone review with dietitian, used when travel or provider unavailability prevents in-person review.",
          "duration_minutes": 20,
          "facilitator_type": "dietitian",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "tuesday"
            ],
            "preferred_time_windows": [
              "10:00-11:00",
              "18:00-19:00",
              "19:00-20:00"
            ],
            "preferred_week": "second",
            "preferred_weeks": [
              "second",
              "first",
              "second"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Remote dietitian review preserves the clinical review target when in-person is not possible.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "dietitian_review",
            "remote_adaptation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "provider_notes",
            "nutrition_adherence"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent meal logs",
              "travel meal summary",
              "current nutrition goal",
              "current supplement list",
              "recent CGM or fasting glucose notes if available"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_dietitian_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "trainer"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_dietitian_review_monthly_primary",
          "substitution_notes": "Preserves dietitian review intent when in-person is not feasible due to travel or provider constraints.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "title": "Remote dietitian review (travel or provider unavailable)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_dietitian_review_monthly_sub_remote",
          "reason": "Remote review preserves the clinical review target and allows timely nutrition adaptation.",
          "when": "Provider is unavailable or member is traveling."
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 1,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Physio reassessment is required after travel.",
        "Remote is primary due to travel context, but in-person is valid when feasible.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "measurement",
        "physio_review",
        "post_travel"
      ],
      "intent": "physio_assessment",
      "primary_activity": {
        "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
        "activity_id": "act_b05_clinical_physio_reassessment_post_travel_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent pain log",
          "travel summary",
          "current mobility goal",
          "recent training load notes"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent pain log",
              "travel summary",
              "current mobility goal",
              "recent training load notes"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote physio assessment to review mobility, pain, and post-travel adaptation. Used after travel.",
        "duration_minutes": 25,
        "facilitator_type": "physiotherapist",
        "frequency": {
          "preferred_time_windows": [
            "16:00-18:00",
            "19:00-20:00"
          ],
          "target_date": "2026-06-26",
          "type": "once",
          "window_days": 7
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Physio reassessment after travel counts toward the 3-month review target.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "physio_review",
          "post_travel"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "mobility_score",
          "pain_level"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent pain log",
            "travel summary",
            "current mobility goal",
            "recent training load notes"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_physio_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_physio_reassessment_post_travel_sub_inperson"
        ],
        "title": "Physio reassessment after travel (remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
          "activity_id": "act_b05_clinical_physio_reassessment_post_travel_sub_inperson",
          "activity_type": "consultation",
          "allowed_locations": [
            "home",
            "gym"
          ],
          "care_context_required": [
            "recent pain log",
            "travel summary",
            "current mobility goal",
            "recent training load notes"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent pain log",
                "travel summary",
                "current mobility goal",
                "recent training load notes"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "In-person physio assessment at home or gym, used when remote review is not possible after travel.",
          "duration_minutes": 30,
          "facilitator_type": "physiotherapist",
          "frequency": {
            "preferred_time_windows": [
              "16:00-18:00",
              "18:45-20:00",
              "19:00-20:00"
            ],
            "target_date": "2026-06-26",
            "type": "once",
            "window_days": 7
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_strength_and_mobility",
              "notes": "In-person physio review preserves the measurement intent when remote is not feasible.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "physio_review",
            "post_travel"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "mobility_score",
            "pain_level"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent pain log",
              "travel summary",
              "current mobility goal",
              "recent training load notes"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": false,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_physio_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_physio_reassessment_post_travel_primary",
          "substitution_notes": "Preserves physio review intent by enabling in-person assessment when remote is not feasible.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "title": "In-person physio reassessment (post-travel/pain)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_physio_reassessment_post_travel_sub_inperson",
          "reason": "In-person physio review preserves the measurement intent after travel.",
          "when": "Remote review is not feasible or provider is available in-person."
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_lab_reschedule_coordination",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Lab reschedule coordination is support-only and does not count toward the review denominator.",
        "Occurs only when lab draw is blocked by travel or facility unavailability.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "support",
        "lab_reschedule",
        "care_team"
      ],
      "intent": "care_team_review",
      "primary_activity": {
        "activity_family_id": "b05_clinical_lab_reschedule_coordination",
        "activity_id": "act_b05_clinical_lab_reschedule_coordination_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "lab due date",
          "travel window summary",
          "clinic availability",
          "fasting feasibility window"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "lab due date",
              "travel window summary",
              "clinic availability",
              "fasting feasibility window"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote care-team coordination to reschedule lab draws when travel or facility unavailability occurs. Member is notified of new lab date.",
        "duration_minutes": 15,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "09:00-17:00",
            "19:00-20:00"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Care-team lab reschedule coordination is support-only and does not count toward the review target.",
            "role": "support",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "support",
          "lab_reschedule",
          "care_team"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_002",
          "phase_marcus_004",
          "phase_marcus_006"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "lab_reschedule_confirmed"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "lab due date",
            "travel window summary",
            "clinic availability",
            "fasting feasibility window"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "dietitian"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_lab_reschedule_coordination_facility_change_sub"
        ],
        "title": "Care-team lab reschedule coordination (remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_lab_reschedule_coordination",
          "activity_id": "act_b05_clinical_lab_reschedule_coordination_facility_change_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "lab due date",
            "travel window summary",
            "clinic availability",
            "fasting feasibility window"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "lab due date",
                "travel window summary",
                "clinic availability",
                "fasting feasibility window"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Care team coordinates an alternate lab booking when the preferred lab or due-week window becomes unavailable.",
          "duration_minutes": 15,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "09:00-17:00",
              "19:00-20:00"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
              "role": "support",
              "unit": "activity",
              "value": 0
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "support",
            "lab_reschedule",
            "care_team"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_002",
            "phase_marcus_004",
            "phase_marcus_006"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "lab_reschedule_confirmed"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "lab due date",
              "travel window summary",
              "clinic availability",
              "fasting feasibility window"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "dietitian"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_lab_reschedule_coordination_primary",
          "substitution_notes": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
          "substitution_reason_codes": [
            "facility_unavailable",
            "time_conflict"
          ],
          "title": "Alternate lab booking coordination"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_lab_reschedule_coordination_facility_change_sub",
          "reason": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
          "when": "facility_unavailable or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_biometric_review_support",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Biometric review is support-only and does not count toward the review denominator.",
        "Occurs monthly to support care-team context and member feedback.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "support",
        "biometric_review",
        "care_team"
      ],
      "intent": "care_team_review",
      "primary_activity": {
        "activity_family_id": "b05_clinical_biometric_review_support",
        "activity_id": "act_b05_clinical_biometric_review_support_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent biometric data",
          "goal progress summary",
          "sleep summary",
          "activity summary",
          "CGM data if available"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent biometric data",
              "goal progress summary",
              "sleep summary",
              "activity summary",
              "CGM data if available"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Physician-led review of biometric data (weight, sleep, activity, CGM if available) with summary sent to member and providers.",
        "duration_minutes": 20,
        "facilitator_type": "physician",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "thursday"
          ],
          "preferred_time_windows": [
            "09:00-11:00",
            "19:00-20:00"
          ],
          "preferred_week": "third",
          "preferred_weeks": [
            "third",
            "fourth",
            "third"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Biometric review summary is support-only and does not count toward the review target.",
            "role": "support",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "support",
          "biometric_review",
          "care_team"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "biometric_summary_sent"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent biometric data",
            "goal progress summary",
            "sleep summary",
            "activity summary",
            "CGM data if available"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_physician_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "dietitian",
          "trainer"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_biometric_review_support_async_summary_sub"
        ],
        "title": "Physician biometric review and care-plan summary (remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_biometric_review_support",
          "activity_id": "act_b05_clinical_biometric_review_support_async_summary_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent biometric data",
            "goal progress summary",
            "sleep summary",
            "activity summary",
            "CGM data if available"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent biometric data",
                "goal progress summary",
                "sleep summary",
                "activity summary",
                "CGM data if available"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Physician reviews CGM, sleep, and session notes asynchronously and summarizes flags for physician or dietitian follow-up.",
          "duration_minutes": 15,
          "facilitator_type": "physician",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "thursday"
            ],
            "preferred_time_windows": [
              "09:00-11:00",
              "19:00-20:00"
            ],
            "preferred_week": "third",
            "preferred_weeks": [
              "third",
              "fourth",
              "third"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Preserves biometric review support when a live care-team review is not realistic.",
              "role": "support",
              "unit": "activity",
              "value": 0
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "support",
            "biometric_review",
            "care_team"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "biometric_summary_sent"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent biometric data",
              "goal progress summary",
              "sleep summary",
              "activity summary",
              "CGM data if available"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_physician_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "dietitian",
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_biometric_review_support_primary",
          "substitution_notes": "Preserves biometric review support when a live care-team review is not realistic.",
          "substitution_reason_codes": [
            "remote_delivery_needed",
            "time_conflict"
          ],
          "title": "Async physician biometric summary review"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_biometric_review_support_async_summary_sub",
          "reason": "Preserves biometric review support when a live care-team review is not realistic.",
          "when": "remote_delivery_needed or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_trainer_physio_handoff",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": false,
        "support_counts": false,
        "target_units": 0,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Trainer-physio handoff is support-only and does not count toward the review denominator.",
        "Occurs after travel or when clinically indicated in the clinical follow-up phase.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "support",
        "trainer_physio_handoff",
        "pain_escalation"
      ],
      "intent": "care_team_review",
      "primary_activity": {
        "activity_family_id": "b05_clinical_trainer_physio_handoff",
        "activity_id": "act_b05_clinical_trainer_physio_handoff_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent pain log",
          "mobility status",
          "training plan update",
          "recent strength progression log"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent pain log",
              "mobility status",
              "training plan update",
              "recent strength progression log"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote care-team handoff between trainer and physiotherapist after travel or when clinically indicated, to coordinate safe return to training.",
        "duration_minutes": 20,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "10:00-11:00",
            "18:00-19:00",
            "19:00-20:00"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_strength_and_mobility",
            "notes": "Trainer-physio handoff is support-only and does not count toward the review target.",
            "role": "support",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "support",
          "trainer_physio_handoff",
          "pain_escalation"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_005"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "handoff_notes"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent pain log",
            "mobility status",
            "training plan update",
            "recent strength progression log"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_trainer_01",
          "provider_physio_01",
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_trainer_physio_handoff_async_handoff_sub"
        ],
        "title": "Trainer-physio care-team handoff after travel (remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_trainer_physio_handoff",
          "activity_id": "act_b05_clinical_trainer_physio_handoff_async_handoff_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent pain log",
            "mobility status",
            "training plan update",
            "recent strength progression log"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent pain log",
                "mobility status",
                "training plan update",
                "recent strength progression log"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Trainer and physio exchange knee-pain and load notes asynchronously before the next strength progression.",
          "duration_minutes": 10,
          "facilitator_type": "physiotherapist",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "10:00-11:00",
              "18:00-19:00",
              "19:00-20:00"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_strength_and_mobility",
              "notes": "Preserves trainer-physio coordination when both providers cannot meet live.",
              "role": "support",
              "unit": "activity",
              "value": 0
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "support",
            "trainer_physio_handoff",
            "pain_escalation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_005"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "handoff_notes"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent pain log",
              "mobility status",
              "training plan update",
              "recent strength progression log"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_trainer_01",
            "provider_physio_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_trainer_physio_handoff_primary",
          "substitution_notes": "Preserves trainer-physio coordination when both providers cannot meet live.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "time_conflict"
          ],
          "title": "Async trainer physio handoff"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_trainer_physio_handoff_async_handoff_sub",
          "reason": "Preserves trainer-physio coordination when both providers cannot meet live.",
          "when": "provider_unavailable or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_adherence_checkin_support",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "weekly",
        "substitutions_count": false,
        "support_counts": true,
        "target_units": 0,
        "unit_label": "protocol checks"
      },
      "family_validation_notes": [
        "Weekly adherence check-in is support-only and does not count toward the review denominator.",
        "Remote coach is always available for this support task.",
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_adherence_support_weekly"
      ],
      "goal_tags": [
        "support",
        "adherence_check",
        "remote_coach"
      ],
      "intent": "adherence_check",
      "primary_activity": {
        "activity_family_id": "b05_clinical_adherence_checkin_support",
        "activity_id": "act_b05_clinical_adherence_checkin_support_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent adherence log",
          "protocol checklist",
          "missed-session reasons",
          "meal/supplement completion notes"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent adherence log",
              "protocol checklist",
              "missed-session reasons",
              "meal/supplement completion notes"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote check-in to review adherence to meal, training, and supplement protocols. Provides support and flags for care-team follow-up if needed.",
        "duration_minutes": 10,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "09:00-10:00",
            "18:00-19:00",
            "19:00-20:00"
          ],
          "type": "weekly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": false,
            "goal_action_id": "ga_adherence_support_weekly",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Weekly adherence check-in is support-only and does not count toward the review target.",
            "role": "support",
            "unit": "activity",
            "value": 0
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "support",
          "adherence_check",
          "remote_coach"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_001",
          "phase_marcus_003",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "adherence_score",
          "flagged_issues"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent adherence log",
            "protocol checklist",
            "missed-session reasons",
            "meal/supplement completion notes"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "dietitian",
          "trainer"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_adherence_checkin_support_message_check_sub"
        ],
        "title": "Weekly adherence check-in with remote coach"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_adherence_checkin_support",
          "activity_id": "act_b05_clinical_adherence_checkin_support_message_check_sub",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent adherence log",
            "protocol checklist",
            "missed-session reasons",
            "meal/supplement completion notes"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent adherence log",
                "protocol checklist",
                "missed-session reasons",
                "meal/supplement completion notes"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Brief message-based adherence check-in to resolve barriers after missed sessions, travel disruption, or meal-prep gaps.",
          "duration_minutes": 10,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "09:00-10:00",
              "18:00-19:00",
              "19:00-20:00"
            ],
            "type": "weekly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": false,
              "goal_action_id": "ga_adherence_support_weekly",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
              "role": "support",
              "unit": "activity",
              "value": 0
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "support",
            "adherence_check",
            "remote_coach"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_001",
            "phase_marcus_003",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "adherence_score",
            "flagged_issues"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent adherence log",
              "protocol checklist",
              "missed-session reasons",
              "meal/supplement completion notes"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "dietitian",
            "trainer"
          ],
          "skip_adjustment": {
            "allowed_after_poor_sleep": true,
            "allowed_after_travel": true,
            "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
          },
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_adherence_checkin_support_primary",
          "substitution_notes": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
          "substitution_reason_codes": [
            "travel_window",
            "time_conflict"
          ],
          "title": "Message-based adherence check-in"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_adherence_checkin_support_message_check_sub",
          "reason": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
          "when": "travel_window or time_conflict"
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_dietitian_lab_followup",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 4,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Dietitian lab follow-up is required after labs or CGM review.",
        "Remote and rescheduled windows are valid when provider or member is unavailable.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month"
      ],
      "goal_tags": [
        "measurement",
        "dietitian_lab_followup",
        "nutrition_review"
      ],
      "intent": "dietitian_lab_followup",
      "primary_activity": {
        "activity_family_id": "b05_clinical_dietitian_lab_followup",
        "activity_id": "act_b05_clinical_dietitian_lab_followup_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote"
        ],
        "care_context_required": [
          "recent lab or CGM results",
          "nutrition adherence summary",
          "current supplement list",
          "recent meal logs"
        ],
        "dependencies": [
          {
            "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
            "must_happen": "before",
            "notes": "Dietitian follow-up must occur after lab or CGM results are available.",
            "offset_minutes_min": 60,
            "type": "prerequisite_activity"
          },
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent lab or CGM results",
              "nutrition adherence summary",
              "current supplement list",
              "recent meal logs"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote dietitian follow-up after lab or CGM review to adjust nutrition plan and address metabolic markers.",
        "duration_minutes": 20,
        "facilitator_type": "dietitian",
        "frequency": {
          "count": 1,
          "preferred_days": [
            "tuesday"
          ],
          "preferred_time_windows": [
            "10:00-11:00",
            "18:00-19:00",
            "19:00-20:00"
          ],
          "preferred_week": "fourth",
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Dietitian lab follow-up counts toward the 3-month clinical review package.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "dietitian_lab_followup",
          "nutrition_review"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_003",
          "phase_marcus_005"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "provider_notes",
          "nutrition_plan_update"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent lab or CGM results",
            "nutrition adherence summary",
            "current supplement list",
            "recent meal logs"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_dietitian_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_dietitian_lab_followup_sub_timeconflict"
        ],
        "title": "Dietitian follow-up after lab or CGM review (remote)"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_dietitian_lab_followup",
          "activity_id": "act_b05_clinical_dietitian_lab_followup_sub_timeconflict",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote"
          ],
          "care_context_required": [
            "recent lab or CGM results",
            "nutrition adherence summary",
            "current supplement list",
            "recent meal logs"
          ],
          "dependencies": [
            {
              "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
              "must_happen": "before",
              "notes": "Dietitian follow-up must occur after lab or CGM results are available.",
              "offset_minutes_min": 60,
              "type": "prerequisite_activity"
            },
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent lab or CGM results",
                "nutrition adherence summary",
                "current supplement list",
                "recent meal logs"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Remote dietitian follow-up is rescheduled to a later window due to provider or member time conflict.",
          "duration_minutes": 15,
          "facilitator_type": "dietitian",
          "frequency": {
            "count": 1,
            "preferred_days": [
              "tuesday"
            ],
            "preferred_time_windows": [
              "18:00-19:00",
              "19:00-20:00"
            ],
            "preferred_week": "fourth",
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Remote dietitian follow-up is rescheduled to a feasible time when provider or member is unavailable.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "dietitian_lab_followup",
            "remote_adaptation"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_003",
            "phase_marcus_005"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "provider_notes",
            "nutrition_plan_update"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent lab or CGM results",
              "nutrition adherence summary",
              "current supplement list",
              "recent meal logs"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_dietitian_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_dietitian_lab_followup_primary",
          "substitution_notes": "Preserves dietitian lab follow-up intent by rescheduling to a feasible remote window.",
          "substitution_reason_codes": [
            "provider_unavailable",
            "remote_delivery_needed",
            "time_conflict"
          ],
          "title": "Dietitian follow-up rescheduled (remote, time conflict)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_dietitian_lab_followup_sub_timeconflict",
          "reason": "Reschedules remote follow-up to a feasible window, preserving measurement intent.",
          "when": "Provider or member is unavailable at the original time."
        }
      ]
    },
    {
      "activity_family_id": "b05_clinical_remote_care_team_handoff",
      "care_domain": "clinical_review_measurement",
      "family_target": {
        "goal_action_id": "ga_care_team_followthrough_3month",
        "period": "3_month",
        "substitutions_count": true,
        "support_counts": false,
        "target_units": 4,
        "unit_label": "reviews"
      },
      "family_validation_notes": [
        "Care-team handoff is required during travel or remote delivery to ensure plan continuity.",
        "Asynchronous delivery is valid when provider is unavailable for live remote handoff.",
        "Activities in this family require prep/context metadata before scheduling."
      ],
      "goal_action_ids": [
        "ga_clinical_review_3month",
        "ga_care_team_followthrough_3month"
      ],
      "goal_tags": [
        "measurement",
        "care_team_handoff",
        "travel_continuity"
      ],
      "intent": "remote_care_team_handoff",
      "primary_activity": {
        "activity_family_id": "b05_clinical_remote_care_team_handoff",
        "activity_id": "act_b05_clinical_remote_care_team_handoff_primary",
        "activity_type": "consultation",
        "allowed_locations": [
          "remote",
          "travel_hotel"
        ],
        "care_context_required": [
          "recent travel summary",
          "plan adaptation notes",
          "missed or substituted activity log",
          "current medication/supplement list"
        ],
        "dependencies": [
          {
            "must_exist": true,
            "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
            "required_inputs": [
              "recent travel summary",
              "plan adaptation notes",
              "missed or substituted activity log",
              "current medication/supplement list"
            ],
            "type": "required_context_available"
          }
        ],
        "details": "Remote care-team handoff to coordinate plan changes during travel or remote delivery. Ensures continuity of clinical review and adaptation.",
        "duration_minutes": 15,
        "facilitator_type": "remote_coach_pool",
        "frequency": {
          "count": 1,
          "preferred_time_windows": [
            "10:00-11:00",
            "18:00-19:00",
            "19:00-20:00"
          ],
          "type": "monthly"
        },
        "goal_contributions": [
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_clinical_review_3month",
            "goal_id": "goal_adherence_and_careteam",
            "notes": "Care-team handoff during travel or remote delivery supports clinical review continuity.",
            "role": "measurement",
            "unit": "activity",
            "value": 1
          },
          {
            "counts_toward_weekly_target": true,
            "goal_action_id": "ga_care_team_followthrough_3month",
            "value": 1
          }
        ],
        "goal_tags": [
          "measurement",
          "care_team_handoff",
          "travel_continuity"
        ],
        "is_primary": true,
        "journey_phase_applicability": [
          "phase_marcus_004",
          "phase_marcus_006",
          "phase_marcus_007"
        ],
        "load_level": "low",
        "metrics_to_collect": [
          "completion",
          "handoff_notes",
          "plan_update"
        ],
        "prep_metadata": {
          "due_before_minutes": 1440,
          "missing_data_policy": "reschedule_or_convert_to_async_review",
          "owner": "care_team_or_activity_facilitator",
          "prep_required": true,
          "prep_type": "clinical_context_review",
          "required_inputs": [
            "recent travel summary",
            "plan adaptation notes",
            "missed or substituted activity log",
            "current medication/supplement list"
          ]
        },
        "prep_required": true,
        "priority": 125,
        "raw_clinical_data_required": false,
        "remote_allowed": true,
        "required_equipment_ids": [],
        "required_provider_ids": [
          "provider_remote_coach_01"
        ],
        "same_day_repeat_allowed": false,
        "share_with_provider_types": [
          "physician",
          "dietitian",
          "trainer",
          "physiotherapist"
        ],
        "skip_adjustment": false,
        "substitution_activity_ids": [
          "act_b05_clinical_remote_care_team_handoff_sub_provider_unavailable"
        ],
        "title": "Remote care-team handoff during travel or remote delivery"
      },
      "substitution_activities": [
        {
          "activity_family_id": "b05_clinical_remote_care_team_handoff",
          "activity_id": "act_b05_clinical_remote_care_team_handoff_sub_provider_unavailable",
          "activity_type": "consultation",
          "allowed_locations": [
            "remote",
            "travel_hotel"
          ],
          "care_context_required": [
            "recent travel summary",
            "plan adaptation notes",
            "missed or substituted activity log",
            "current medication/supplement list"
          ],
          "dependencies": [
            {
              "must_exist": true,
              "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
              "required_inputs": [
                "recent travel summary",
                "plan adaptation notes",
                "missed or substituted activity log",
                "current medication/supplement list"
              ],
              "type": "required_context_available"
            }
          ],
          "details": "Care-team handoff is completed asynchronously (e.g., via secure message or app) when provider is unavailable for live remote handoff.",
          "duration_minutes": 10,
          "facilitator_type": "remote_coach_pool",
          "frequency": {
            "count": 1,
            "preferred_time_windows": [
              "18:00-19:00",
              "19:00-20:00"
            ],
            "type": "monthly"
          },
          "goal_contributions": [
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_clinical_review_3month",
              "goal_id": "goal_adherence_and_careteam",
              "notes": "Care-team handoff is rescheduled or delivered asynchronously when provider is unavailable.",
              "role": "measurement",
              "unit": "activity",
              "value": 1
            },
            {
              "counts_toward_weekly_target": true,
              "goal_action_id": "ga_care_team_followthrough_3month",
              "value": 1
            }
          ],
          "goal_tags": [
            "measurement",
            "care_team_handoff",
            "travel_continuity"
          ],
          "is_primary": false,
          "journey_phase_applicability": [
            "phase_marcus_004",
            "phase_marcus_006",
            "phase_marcus_007"
          ],
          "load_level": "low",
          "metrics_to_collect": [
            "completion",
            "handoff_notes",
            "plan_update"
          ],
          "prep_metadata": {
            "due_before_minutes": 1440,
            "missing_data_policy": "reschedule_or_convert_to_async_review",
            "owner": "care_team_or_activity_facilitator",
            "prep_required": true,
            "prep_type": "clinical_context_review",
            "required_inputs": [
              "recent travel summary",
              "plan adaptation notes",
              "missed or substituted activity log",
              "current medication/supplement list"
            ]
          },
          "prep_required": true,
          "priority": 126,
          "raw_clinical_data_required": false,
          "remote_allowed": true,
          "required_equipment_ids": [],
          "required_provider_ids": [
            "provider_remote_coach_01"
          ],
          "same_day_repeat_allowed": false,
          "share_with_provider_types": [
            "physician",
            "dietitian",
            "trainer",
            "physiotherapist"
          ],
          "skip_adjustment": false,
          "substitution_activity_ids": [],
          "substitution_for_activity_id": "act_b05_clinical_remote_care_team_handoff_primary",
          "substitution_notes": "Preserves care-team handoff intent by enabling asynchronous delivery when provider is unavailable.",
          "substitution_reason_codes": [
            "travel_window",
            "provider_unavailable",
            "remote_delivery_needed"
          ],
          "title": "Asynchronous care-team handoff (provider unavailable)"
        }
      ],
      "substitution_rules": [
        {
          "prefer_activity_id": "act_b05_clinical_remote_care_team_handoff_sub_provider_unavailable",
          "reason": "Asynchronous handoff preserves care-team adaptation and clinical review continuity.",
          "when": "Provider is unavailable for live remote handoff during travel or remote delivery."
        }
      ]
    }
  ]
}
```

---

## action_plan.json

```json
{
  "activities": [
    {
      "activity_family_id": "b01_nutrition_breakfast_chef_home",
      "activity_id": "act_b01_breakfast_chef_home_primary",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current dietary preference",
        "protein target"
      ],
      "dependencies": [],
      "details": "Breakfast at home, chef-prepped or prepped in advance. High-protein, low-effort, tailored to metabolic goals. Chef Liyang prepares up to 2x/week; other days use prepped or low-prep options.",
      "dining_source": "home",
      "duration_minutes": 20,
      "facilitator_type": "chef",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "food_provider_id": "provider_chef_01",
      "frequency": {
        "count": 5,
        "preferred_days": [
          "monday",
          "tuesday",
          "wednesday",
          "thursday",
          "friday"
        ],
        "preferred_time_windows": [
          "06:30-08:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Directly supports weekly structured meal goal as home chef-prepped breakfast.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "metabolic_health"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "home",
        "facilitator_type": "chef",
        "meal_slot": "breakfast",
        "prep_source": "chef_prepped"
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings",
        "post_meal_energy"
      ],
      "prep_required": false,
      "prep_source": "chef_prepped",
      "priority": 10,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_kitchen_home"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [
        "act_b01_breakfast_home_lowprep",
        "act_b01_breakfast_skip_for_fasting_lab"
      ],
      "title": "Chef-prepared high-protein breakfast",
      "weekly_primary_cap": 4
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_chef_home",
      "activity_id": "act_b01_breakfast_home_lowprep",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "protein target"
      ],
      "dependencies": [],
      "details": "Member assembles a high-protein breakfast (e.g., Greek yogurt, eggs, fruit, nuts) when chef prep is unavailable or time is limited.",
      "dining_source": "home",
      "duration_minutes": 10,
      "facilitator_type": "member",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:30-08:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts as structured meal if chef unavailable; preserves high-protein, low-effort intent.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "metabolic_health"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "home",
        "facilitator_type": "member",
        "meal_slot": "breakfast",
        "prep_source": "member_assembled"
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings"
      ],
      "prep_required": false,
      "prep_source": "member_assembled",
      "priority": 20,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_kitchen_home"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_breakfast_chef_home_primary",
      "substitution_notes": "Preserves structured, high-protein breakfast intent when chef prep is unavailable or time is limited.",
      "substitution_reason_codes": [
        "prep_unavailable",
        "time_conflict"
      ],
      "title": "Low-prep high-protein breakfast at home",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_office_delivery",
      "activity_id": "act_b01_breakfast_office_delivery_primary",
      "activity_type": "food",
      "allowed_locations": [
        "office"
      ],
      "care_context_required": [
        "office schedule"
      ],
      "delivery_source": "office_delivery",
      "dependencies": [],
      "details": "Breakfast delivered to office for early workdays or when home prep is not possible. Chef-prepped or office delivery, high-protein and low-effort.",
      "dining_source": "office",
      "duration_minutes": 10,
      "facilitator_type": "chef",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "food_provider_id": "provider_chef_01",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "08:30-09:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Support-only; does not count unless explicitly scheduled as structured meal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "office",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "office",
        "facilitator_type": "chef",
        "meal_slot": "breakfast",
        "prep_source": "chef_prepped"
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings"
      ],
      "prep_required": false,
      "prep_source": "chef_prepped",
      "priority": 40,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [
        "act_b01_breakfast_office_member_assembled",
        "act_b01_breakfast_skip_for_fasting_lab",
        "act_b01_breakfast_home_lowprep"
      ],
      "title": "Office-delivered breakfast",
      "wfh_scheduling_constraint": {
        "calendar_rejection_reason_required_if_no_substitution": true,
        "on_member_location_home_day": "do_not_schedule_office_location",
        "preferred_substitution_activity_id": "act_b01_breakfast_home_lowprep",
        "rejection_reason_code": "wfh_no_office_location_activity"
      }
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_office_delivery",
      "activity_id": "act_b01_breakfast_office_member_assembled",
      "activity_type": "food",
      "allowed_locations": [
        "office"
      ],
      "care_context_required": [
        "office schedule"
      ],
      "delivery_source": "none",
      "dependencies": [],
      "details": "Member assembles a simple high-protein breakfast at office (e.g., protein shake, nuts, fruit) if delivery is unavailable.",
      "dining_source": "office",
      "duration_minutes": 10,
      "facilitator_type": "member",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "08:30-09:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Support-only; member-assembled office breakfast if delivery fails.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "office",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "office",
        "facilitator_type": "member",
        "meal_slot": "breakfast",
        "prep_source": "member_assembled",
        "structured_meal": true
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "member_assembled",
      "priority": 50,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_breakfast_office_delivery_primary",
      "substitution_notes": "Preserves breakfast intent at office when delivery is unavailable or time is limited.",
      "substitution_reason_codes": [
        "prep_unavailable",
        "time_conflict"
      ],
      "title": "Simple high-protein breakfast at office"
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
      "activity_id": "act_b01_breakfast_travel_hotel_primary",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "dietitian guidance"
      ],
      "dependencies": [],
      "details": "Breakfast at hotel buffet or via room service during travel. Focus on protein and fiber; chef prep unavailable.",
      "dining_source": "hotel_buffet",
      "duration_minutes": 15,
      "facilitator_type": "member",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-09:00"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Travel hotel breakfast as substitution for structured home breakfast; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "travel",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "hotel_buffet",
        "facilitator_type": "member",
        "meal_slot": "breakfast",
        "prep_source": "none"
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 60,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [
        "act_b01_breakfast_travel_hotel_restaurant",
        "act_b01_breakfast_skip_for_fasting_lab"
      ],
      "title": "Hotel buffet or room-service breakfast (travel)"
    },
    {
      "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
      "activity_id": "act_b01_breakfast_travel_hotel_restaurant",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window"
      ],
      "dependencies": [],
      "details": "Breakfast at a local restaurant when hotel buffet or room service is unavailable during travel.",
      "dining_source": "restaurant",
      "duration_minutes": 15,
      "facilitator_type": "member",
      "fasting_lab_scheduling_constraint": {
        "blocked_when_activity_id_scheduled_same_morning": "act_b05_clinical_lab_draw_due_week_primary",
        "calendar_skip_reason_required": true,
        "do_not_schedule_before_fasting_lab_same_day": true,
        "replacement_activity_id": "act_b01_breakfast_skip_for_fasting_lab",
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-09:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Restaurant breakfast during travel; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "breakfast",
        "travel",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "breakfast",
        "prep_source": "none"
      },
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 70,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_for_fasting_lab": true,
        "fasting_lab_skip_reason_code": "fasting_lab_same_morning",
        "fasting_lab_skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_breakfast_travel_hotel_primary",
      "substitution_notes": "Preserves travel breakfast intent when hotel buffet or room service is unavailable.",
      "substitution_reason_codes": [
        "travel_window",
        "prep_unavailable"
      ],
      "title": "Restaurant breakfast (travel)",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_lunch_office_delivery",
      "activity_id": "act_b01_lunch_office_delivery_primary",
      "activity_type": "food",
      "allowed_locations": [
        "office"
      ],
      "care_context_required": [
        "office schedule",
        "protein target"
      ],
      "delivery_source": "office_delivery",
      "dependencies": [],
      "details": "Lunch at office, delivered or packed by chef. High-protein, balanced, and easy to eat during work blocks.",
      "dining_source": "office",
      "duration_minutes": 25,
      "facilitator_type": "chef",
      "food_provider_id": "provider_chef_01",
      "frequency": {
        "count": 5,
        "preferred_days": [
          "monday",
          "tuesday",
          "wednesday",
          "thursday",
          "friday"
        ],
        "preferred_time_windows": [
          "12:00-13:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Directly supports structured meal goal as office lunch.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "office",
        "metabolic_health"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "office",
        "facilitator_type": "chef",
        "meal_slot": "lunch",
        "prep_source": "chef_prepped"
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings",
        "fiber_servings"
      ],
      "prep_required": false,
      "prep_source": "chef_prepped",
      "priority": 15,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_lunch_office_member_assembled",
        "act_b01_lunch_member_assembled_home_primary"
      ],
      "title": "Chef-prepped or delivered office lunch",
      "weekly_primary_cap": 4,
      "wfh_scheduling_constraint": {
        "calendar_rejection_reason_required_if_no_substitution": true,
        "on_member_location_home_day": "do_not_schedule_office_location",
        "preferred_substitution_activity_id": "act_b01_lunch_member_assembled_home_primary",
        "rejection_reason_code": "wfh_no_office_location_activity"
      }
    },
    {
      "activity_family_id": "b01_nutrition_lunch_office_delivery",
      "activity_id": "act_b01_lunch_office_member_assembled",
      "activity_type": "food",
      "allowed_locations": [
        "office"
      ],
      "care_context_required": [
        "office schedule"
      ],
      "delivery_source": "none",
      "dependencies": [],
      "details": "Member assembles a high-protein, balanced lunch at office (e.g., protein bowl, salad, pre-packed meal) if chef or delivery is unavailable.",
      "dining_source": "office",
      "duration_minutes": 15,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "12:00-13:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts as structured meal if chef or delivery is unavailable and member assembles lunch at office.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "office",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "office",
        "facilitator_type": "member",
        "meal_slot": "lunch",
        "prep_source": "member_assembled",
        "structured_meal": true
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "member_assembled",
      "priority": 25,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_lunch_office_delivery_primary",
      "substitution_notes": "Preserves structured lunch intent at office when chef or delivery is unavailable.",
      "substitution_reason_codes": [
        "prep_unavailable",
        "time_conflict"
      ],
      "title": "Balanced office lunch bowl",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
      "activity_id": "act_b01_lunch_restaurant_travel_primary",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "dietitian guidance"
      ],
      "dependencies": [],
      "details": "Lunch at restaurant or hotel during travel. Focus on protein and fiber; chef prep and office delivery unavailable.",
      "dining_source": "restaurant",
      "duration_minutes": 30,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "12:00-13:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Travel lunch as substitution for structured office lunch; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "travel",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "lunch",
        "prep_source": "none"
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 65,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_lunch_travel_room_service"
      ],
      "title": "Restaurant or hotel lunch (travel)"
    },
    {
      "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
      "activity_id": "act_b01_lunch_travel_room_service",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window"
      ],
      "dependencies": [],
      "details": "Lunch via hotel room service when restaurant is not feasible during travel.",
      "dining_source": "room_service",
      "duration_minutes": 25,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "12:00-13:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Room-service lunch during travel; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "travel",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "room_service",
        "facilitator_type": "member",
        "meal_slot": "lunch",
        "prep_source": "none"
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 75,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_lunch_restaurant_travel_primary",
      "substitution_notes": "Preserves travel lunch intent when restaurant is not feasible.",
      "substitution_reason_codes": [
        "travel_window",
        "prep_unavailable"
      ],
      "title": "Room-service lunch (travel)",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
      "activity_id": "act_b01_lunch_member_assembled_home_primary",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "home schedule"
      ],
      "dependencies": [],
      "details": "Member assembles a high-protein, balanced lunch at home (e.g., salad, grain bowl, leftovers) if chef prep or office delivery is unavailable.",
      "dining_source": "home",
      "duration_minutes": 15,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "12:00-13:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Member-assembled lunch at home as fallback; does not count unless explicitly scheduled as structured meal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "home",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "home",
        "facilitator_type": "member",
        "meal_slot": "lunch",
        "prep_source": "member_assembled",
        "structured_meal": true
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "member_assembled",
      "priority": 55,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_kitchen_home"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_lunch_home_no_prep"
      ],
      "title": "Simple high-protein lunch at home"
    },
    {
      "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
      "activity_id": "act_b01_lunch_home_no_prep",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "home schedule"
      ],
      "dependencies": [],
      "details": "Quick, no-prep lunch at home (e.g., protein shake, pre-packed meal) if member assembly is not feasible.",
      "dining_source": "home",
      "duration_minutes": 5,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "12:00-13:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "No-prep lunch at home (e.g., protein shake, pre-packed meal) if member assembly is not feasible.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "lunch",
        "home",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "home",
        "facilitator_type": "member",
        "meal_slot": "lunch",
        "prep_source": "none",
        "structured_meal": true
      },
      "meal_slot": "lunch",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 65,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_lunch_member_assembled_home_primary",
      "substitution_notes": "Preserves lunch intent at home when member assembly is not feasible.",
      "substitution_reason_codes": [
        "prep_unavailable"
      ],
      "title": "Quick protein lunch at home"
    },
    {
      "activity_family_id": "b01_nutrition_dinner_chef_home",
      "activity_id": "act_b01_dinner_chef_home_primary",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current dietary preference",
        "protein target"
      ],
      "dependencies": [],
      "details": "Dinner at home, chef-prepped. Balanced, high-protein, and tailored to metabolic goals. Chef Liyang prepares up to 2x/week; other days use prepped or low-prep options.",
      "dining_source": "home",
      "duration_minutes": 40,
      "facilitator_type": "chef",
      "food_provider_id": "provider_chef_01",
      "frequency": {
        "count": 4,
        "preferred_days": [
          "monday",
          "tuesday",
          "wednesday",
          "sunday"
        ],
        "preferred_time_windows": [
          "19:00-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Directly supports structured meal goal as home chef-prepped dinner.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "home",
        "metabolic_health"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "home",
        "facilitator_type": "chef",
        "meal_slot": "dinner",
        "prep_source": "chef_prepped"
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings",
        "fiber_servings"
      ],
      "prep_required": false,
      "prep_source": "chef_prepped",
      "priority": 20,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_kitchen_home"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_dinner_home_restaurant"
      ],
      "title": "Chef-prepared dinner at home",
      "weekly_primary_cap": 3
    },
    {
      "activity_family_id": "b01_nutrition_dinner_chef_home",
      "activity_id": "act_b01_dinner_home_restaurant",
      "activity_type": "food",
      "allowed_locations": [
        "restaurant"
      ],
      "care_context_required": [
        "dining out context"
      ],
      "dependencies": [],
      "details": "Dinner at a structured restaurant when chef prep is unavailable or client dinner is required. Focus on protein, fiber, and metabolic balance.",
      "dining_source": "restaurant",
      "duration_minutes": 60,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "19:00-20:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts as structured meal if chef prep is unavailable and Marcus dines at a structured restaurant.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "home",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "dinner",
        "prep_source": "none",
        "structured_meal": true
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 30,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_dinner_chef_home_primary",
      "substitution_notes": "Preserves structured dinner intent when chef prep is unavailable or client dinner is required.",
      "substitution_reason_codes": [
        "prep_unavailable",
        "time_conflict"
      ],
      "title": "Balanced restaurant dinner",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_dinner_restaurant",
      "activity_id": "act_b01_dinner_restaurant_primary",
      "activity_type": "food",
      "allowed_locations": [
        "restaurant"
      ],
      "care_context_required": [
        "dining out context"
      ],
      "dependencies": [],
      "details": "Dinner at a structured restaurant when chef prep is unavailable or client dinner is required. Focus on protein, fiber, and metabolic balance.",
      "dining_source": "restaurant",
      "duration_minutes": 60,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "19:00-20:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Structured restaurant dinner as fallback; does not count unless explicitly scheduled as structured meal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "restaurant",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "dinner",
        "prep_source": "none",
        "structured_meal": true
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 45,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_dinner_restaurant_no_prep"
      ],
      "title": "Balanced restaurant dinner"
    },
    {
      "activity_family_id": "b01_nutrition_dinner_restaurant",
      "activity_id": "act_b01_dinner_restaurant_no_prep",
      "activity_type": "food",
      "allowed_locations": [
        "restaurant"
      ],
      "care_context_required": [
        "dining out context"
      ],
      "dependencies": [],
      "details": "Quick, no-prep dinner at restaurant (e.g., set menu or pre-ordered) if time is limited.",
      "dining_source": "restaurant",
      "duration_minutes": 45,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "19:00-20:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "No-prep dinner at restaurant (e.g., set menu or pre-ordered) if time is limited.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "restaurant",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "dinner",
        "prep_source": "none",
        "structured_meal": true
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 55,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_dinner_restaurant_primary",
      "substitution_notes": "Preserves dinner intent at restaurant when time is limited.",
      "substitution_reason_codes": [
        "prep_unavailable",
        "time_conflict"
      ],
      "title": "Quick restaurant dinner"
    },
    {
      "activity_family_id": "b01_nutrition_dinner_travel_hotel",
      "activity_id": "act_b01_dinner_travel_hotel_primary",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "dietitian guidance"
      ],
      "dependencies": [],
      "details": "Dinner at hotel restaurant or via room service during travel. Focus on protein and metabolic balance; chef prep unavailable.",
      "dining_source": "restaurant",
      "duration_minutes": 45,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "19:00-20:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Travel dinner as substitution for structured home dinner; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "travel",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "restaurant",
        "facilitator_type": "member",
        "meal_slot": "dinner",
        "prep_source": "none"
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion",
        "protein_servings"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 70,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_dinner_travel_room_service"
      ],
      "title": "Hotel or restaurant dinner (travel)"
    },
    {
      "activity_family_id": "b01_nutrition_dinner_travel_hotel",
      "activity_id": "act_b01_dinner_travel_room_service",
      "activity_type": "food",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window"
      ],
      "dependencies": [],
      "details": "Dinner via hotel room service when restaurant is not feasible during travel.",
      "dining_source": "room_service",
      "duration_minutes": 40,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "19:00-20:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Room-service dinner during travel; does not count toward normal-week denominator.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "structured_meal",
        "dinner",
        "travel",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": "room_service",
        "facilitator_type": "member",
        "meal_slot": "dinner",
        "prep_source": "none"
      },
      "meal_slot": "dinner",
      "metrics_to_collect": [
        "meal_completion"
      ],
      "prep_required": false,
      "prep_source": "none",
      "priority": 80,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_dinner_travel_hotel_primary",
      "substitution_notes": "Preserves travel dinner intent when restaurant is not feasible.",
      "substitution_reason_codes": [
        "travel_window",
        "prep_unavailable"
      ],
      "title": "Room-service dinner (travel)",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
      "activity_id": "act_b01_fasting_aware_meal_support_primary",
      "activity_type": "food",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "lab schedule"
      ],
      "dependencies": [],
      "details": "Supports meal scheduling logic around fasting labs. Member receives reminder and meal plan adjustment for fasting requirement.",
      "duration_minutes": 0,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:00-10:00"
        ],
        "type": "due_week"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Supports meal timing and structure around fasting labs; does not count as a meal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "fasting",
        "meal_timing",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": null,
        "facilitator_type": "member",
        "meal_slot": null,
        "prep_source": null
      },
      "metrics_to_collect": [
        "meal_timing_adherence"
      ],
      "prep_required": false,
      "priority": 85,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_fasting_aware_meal_support_remote_check_sub",
        "act_b01_breakfast_skip_for_fasting_lab"
      ],
      "title": "Fasting-aware meal timing support"
    },
    {
      "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
      "activity_id": "act_b01_fasting_aware_meal_support_remote_check_sub",
      "activity_type": "food",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "lab schedule"
      ],
      "dependencies": [],
      "details": "Remote review of fasting timing, hydration, and first-meal plan when lab timing changes or travel creates uncertainty.",
      "duration_minutes": 10,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:00-10:00"
        ],
        "type": "due_week"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "fasting",
        "meal_timing",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_metadata": {
        "dining_source": null,
        "facilitator_type": "member",
        "meal_slot": null,
        "prep_source": null
      },
      "metrics_to_collect": [
        "meal_timing_adherence"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "lab schedule"
        ]
      },
      "prep_required": true,
      "priority": 88,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_fasting_aware_meal_support_primary",
      "substitution_notes": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
      "substitution_reason_codes": [
        "remote_delivery_needed",
        "time_conflict"
      ],
      "title": "Remote fasting meal timing check",
      "variety_role": "planned_variety",
      "weekly_variety_min": 1
    },
    {
      "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
      "activity_id": "act_b01_breakfast_skip_for_fasting_lab",
      "activity_type": "food",
      "allowed_locations": [
        "home",
        "clinic",
        "remote"
      ],
      "care_context_required": [
        "lab schedule",
        "fasting start time"
      ],
      "dependencies": [
        {
          "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "must_happen": "after",
          "notes": "Use only on a day with a scheduled fasting lab draw before the normal breakfast window closes.",
          "type": "same_day_activity_context"
        }
      ],
      "details": "Explicit skipped breakfast row for a fasting metabolic lab draw. Water only until the lab draw is complete; first caloric meal should be scheduled after labs.",
      "duration_minutes": 0,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:30-10:00"
        ],
        "type": "constraint_scoped"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_structured_meals_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Skipped breakfast does not count as a structured meal; it preserves fasting validity for metabolic lab draw.",
          "role": "skip",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "fasting",
        "breakfast",
        "skip",
        "metabolic_review"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "meal_slot": "breakfast",
      "metrics_to_collect": [
        "skip_reason_recorded",
        "fasting_confirmed"
      ],
      "prep_metadata": {
        "calendar_skip_reason_required": true,
        "due_before_minutes": 720,
        "missing_data_policy": "do_not_schedule_skip_without_lab_draw",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "fasting_lab_breakfast_skip",
        "required_inputs": [
          "lab schedule",
          "fasting start time"
        ],
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "prep_required": true,
      "priority": 10,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian",
        "physician"
      ],
      "skip_adjustment": {
        "is_skip": true,
        "reschedule_first_meal_after_activity": true,
        "skip_reason_code": "fasting_lab_same_morning",
        "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting.",
        "valid_only_before_activity_id": "act_b05_clinical_lab_draw_due_week_primary"
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_breakfast_chef_home_primary",
      "substitution_notes": "Use instead of breakfast when a fasting lab draw is scheduled before breakfast.",
      "substitution_reason_codes": [
        "fasting_lab_same_morning"
      ],
      "title": "Skip breakfast for fasting lab draw"
    },
    {
      "activity_family_id": "b01_nutrition_supplement_protocol_support",
      "activity_id": "act_b01_supplement_protocol_support_primary",
      "activity_type": "medication",
      "allowed_locations": [
        "home",
        "office",
        "travel_hotel"
      ],
      "care_context_required": [
        "current supplement protocol"
      ],
      "dependencies": [],
      "details": "Member takes prescribed supplements with breakfast or dinner. Protocol is reviewed weekly by dietitian.",
      "duration_minutes": 5,
      "facilitator_type": "member",
      "food_timing": "with_breakfast_or_dinner",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "07:00-08:30",
          "19:00-20:30"
        ],
        "type": "daily"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Daily supplement protocol supports adherence but does not count as a core meal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "supplement",
        "adherence",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_002",
        "phase_marcus_003",
        "phase_marcus_004",
        "phase_marcus_005",
        "phase_marcus_006",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "protocol_completion",
        "miss_reason"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "current supplement protocol"
        ]
      },
      "prep_required": true,
      "priority": 90,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_supplement_protocol_support_travel_timing_sub"
      ],
      "title": "Daily supplement protocol with breakfast or dinner"
    },
    {
      "activity_family_id": "b01_nutrition_supplement_protocol_support",
      "activity_id": "act_b01_supplement_protocol_support_travel_timing_sub",
      "activity_type": "medication",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "current supplement protocol"
      ],
      "dependencies": [],
      "details": "Travel-compatible supplement timing review tied to the available breakfast or dinner window, without replacing a meal.",
      "duration_minutes": 10,
      "facilitator_type": "member",
      "food_timing": "with_breakfast_or_dinner",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "07:00-08:30",
          "19:00-20:30"
        ],
        "type": "daily"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Preserves supplement adherence support when travel disrupts the usual meal window.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "supplement",
        "adherence",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_002",
        "phase_marcus_003",
        "phase_marcus_004",
        "phase_marcus_005",
        "phase_marcus_006",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "protocol_completion",
        "miss_reason"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "current supplement protocol"
        ]
      },
      "prep_required": true,
      "priority": 93,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_supplement_protocol_support_primary",
      "substitution_notes": "Preserves supplement adherence support when travel disrupts the usual meal window.",
      "substitution_reason_codes": [
        "travel_window",
        "remote_delivery_needed"
      ],
      "title": "Travel supplement timing review"
    },
    {
      "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
      "activity_id": "act_b01_travel_meal_adherence_check_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "travel window",
        "recent meal log"
      ],
      "dependencies": [],
      "details": "Remote check-in with dietitian or health coach to review meal adherence and troubleshoot barriers during travel.",
      "duration_minutes": 15,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "19:00-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "meal_adherence",
        "support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "adherence_score",
        "barrier_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "travel window",
          "recent meal log"
        ]
      },
      "prep_required": true,
      "priority": 95,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01",
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian",
        "remote_coach_pool"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b01_travel_meal_adherence_check_photo_review_sub"
      ],
      "title": "Remote meal adherence check-in (travel)"
    },
    {
      "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
      "activity_id": "act_b01_travel_meal_adherence_check_photo_review_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "travel window",
        "recent meal log"
      ],
      "dependencies": [],
      "details": "Asynchronous dietitian or coach review of travel meal photos and notes to keep structured eating aligned with metabolic goals.",
      "duration_minutes": 10,
      "facilitator_type": "dietitian",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "19:00-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "meal_adherence",
        "support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "adherence_score",
        "barrier_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "travel window",
          "recent meal log"
        ]
      },
      "prep_required": true,
      "priority": 98,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b01_travel_meal_adherence_check_primary",
      "substitution_notes": "Preserves travel meal adherence support when a live check-in cannot be scheduled.",
      "substitution_reason_codes": [
        "travel_window",
        "time_conflict"
      ],
      "title": "Async travel meal photo review"
    },
    {
      "activity_family_id": "b02_cardio_zone2_gym",
      "activity_id": "act_b02_cardio_zone2_gym_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "gym"
      ],
      "care_context_required": [
        "current aerobic goal",
        "recent knee/back status"
      ],
      "dependencies": [],
      "details": "Structured aerobic session using rower or stationary bike at preferred gym. Prioritizes Zone 2 heart rate. Trainer available for guidance if scheduled.",
      "duration_minutes": 45,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "saturday"
        ],
        "preferred_time_windows": [
          "08:00-10:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Directly satisfies weekly aerobic conditioning target.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "metabolic_health"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "average_heart_rate",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 101,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_rower_gym"
      ],
      "required_provider_ids": [
        "provider_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": false,
        "notes": "If post-travel or equipment unavailable, use substitution."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_zone2_gym_home_sub",
        "act_b02_cardio_zone2_gym_time_sub"
      ],
      "title": "Zone 2 aerobic session at gym (rower or bike)"
    },
    {
      "activity_family_id": "b02_cardio_zone2_gym",
      "activity_id": "act_b02_cardio_zone2_gym_home_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Home-based aerobic session using stationary bike, brisk walking, or bodyweight circuit. Used if gym or equipment is unavailable.",
      "duration_minutes": 40,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "saturday"
        ],
        "preferred_time_windows": [
          "08:00-10:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts as aerobic conditioning if gym unavailable.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "metabolic_health"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 102,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Lower-load option if needed."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_zone2_gym_primary",
      "substitution_notes": "Preserves aerobic intent when gym or rower is unavailable.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "equipment_unavailable"
      ],
      "title": "Zone 2 aerobic session at home (bodyweight or cycling)"
    },
    {
      "activity_family_id": "b02_cardio_zone2_gym",
      "activity_id": "act_b02_cardio_zone2_gym_time_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "gym"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Condensed aerobic session at gym (rower or bike) for days with limited time. Used when full session cannot fit after work or due to travel buffer.",
      "duration_minutes": 30,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "saturday"
        ],
        "preferred_time_windows": [
          "10:15-11:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts if gym session cannot be scheduled due to time conflict.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "metabolic_health"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 103,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_rower_gym"
      ],
      "required_provider_ids": [
        "provider_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Shorter session if needed."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_zone2_gym_primary",
      "substitution_notes": "Preserves aerobic intent when only a shorter gym window is available.",
      "substitution_reason_codes": [
        "time_conflict"
      ],
      "title": "Shorter aerobic session at gym (reduced duration)"
    },
    {
      "activity_family_id": "b02_cardio_zone2_home",
      "activity_id": "act_b02_cardio_zone2_home_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Home-based aerobic session using stationary bike, brisk walking, or bodyweight circuit. Self-led, knee-safe.",
      "does_not_count_toward_goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "duration_minutes": 40,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "thursday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30",
          "18:45-20:00",
          "18:00-18:45"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Directly satisfies weekly aerobic conditioning target.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "home_fitness"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 104,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Can be replaced by travel variant if home unavailable."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_zone2_home_travel_sub"
      ],
      "title": "Zone 2 aerobic session at home (cycling or brisk walk)",
      "walking_activity_metadata": {
        "counts_as_full_aerobic_session": true,
        "counts_as_strength": false,
        "walk_only_week_reason_field": "calendar_week_validation_reason",
        "walk_only_week_requires_reason": true
      }
    },
    {
      "activity_family_id": "b02_cardio_zone2_home",
      "activity_id": "act_b02_cardio_zone2_home_travel_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Travel-compatible aerobic session using bodyweight and mini bands in hotel room. Used if home is unavailable due to travel.",
      "duration_minutes": 35,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "thursday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30",
          "18:45-20:00",
          "18:00-18:45"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts if home session is blocked by travel.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "travel_adapted"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 105,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel-compatible."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_zone2_home_primary",
      "substitution_notes": "Preserves aerobic intent when home is unavailable due to travel.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable"
      ],
      "title": "Zone 2 aerobic session in hotel room (bodyweight/band circuit)"
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
      "activity_id": "act_b02_cardio_zone2_travel_hotel_gym_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Aerobic session using hotel gym bike or treadmill during travel. Used when normal gym/home sessions are not possible.",
      "duration_minutes": 35,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-08:00"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Travel hotel gym aerobic session counts toward weekly aerobic conditioning.",
          "role": "core",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "goal_id": "goal_travel_resilience",
          "notes": "Supports travel continuity.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "travel_adapted",
        "hotel_gym"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 106,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_basic_gym_hotel_tokyo"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_zone2_travel_hotel_gym_pool_sub"
      ],
      "title": "Aerobic session in hotel gym (bike or treadmill)"
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
      "activity_id": "act_b02_cardio_zone2_travel_hotel_gym_pool_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Aerobic swim session in hotel pool during travel. Used if hotel gym equipment is unavailable or pool is preferred.",
      "duration_minutes": 30,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-08:00"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "zone2",
        "travel_adapted",
        "hotel_pool"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 107,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_pool_hotel_hk"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_zone2_travel_hotel_gym_primary",
      "substitution_notes": "Preserves aerobic intent using hotel pool when gym equipment is unavailable.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "equipment_unavailable"
      ],
      "title": "Aerobic swim session in hotel pool"
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
      "activity_id": "act_b02_cardio_zone2_travel_bodyweight_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Aerobic session using bodyweight and mini bands in hotel room during low-resource travel. Used when no gym or pool is available.",
      "duration_minutes": 25,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:30-07:15"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Hotel pool aerobic session counts toward weekly aerobic conditioning.",
          "role": "core",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "goal_id": "goal_travel_resilience",
          "notes": "Supports travel continuity.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "travel_adapted",
        "bodyweight"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 108,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation for low-resource hotel."
      },
      "substitution_activity_ids": [],
      "title": "Bodyweight aerobic session in hotel room"
    },
    {
      "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
      "activity_id": "act_b02_cardio_zone2_travel_bodyweight_walk_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Brisk walking session outside or in hotel corridors during travel when no equipment is available.",
      "does_not_count_toward_goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "duration_minutes": 30,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-07:45"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "travel_adapted",
        "walking"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_006"
      ],
      "last_resort_substitution_metadata": {
        "avoid_week_with_only_walks_unless_impossible": true,
        "calendar_reason_required_if_scheduled": true,
        "last_resort": true,
        "prefer_non_walk_aerobic_before_walk": true,
        "reason_code_examples": [
          "facility_unavailable",
          "equipment_unavailable",
          "travel_window",
          "time_conflict",
          "pain_or_fatigue"
        ]
      },
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 109,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation for lowest-resource scenario."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_zone2_travel_bodyweight_primary",
      "substitution_notes": "Preserves aerobic intent using walking when even bodyweight circuit is not feasible.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "equipment_unavailable"
      ],
      "title": "Brisk walking session near hotel",
      "walking_activity_metadata": {
        "counts_as_full_aerobic_session": true,
        "counts_as_strength": false,
        "walk_only_week_reason_field": "calendar_week_validation_reason",
        "walk_only_week_requires_reason": true
      }
    },
    {
      "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
      "activity_id": "act_b02_cardio_swim_pool_hotel_hk_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Aerobic swim session in hotel pool during Hong Kong travel. Used as a travel-specific aerobic alternative.",
      "duration_minutes": 30,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-08:00"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Hotel pool aerobic session counts toward weekly aerobic conditioning.",
          "role": "core",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "goal_id": "goal_travel_resilience",
          "notes": "Supports travel continuity.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "swimming",
        "travel_adapted",
        "hotel_pool"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 110,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_pool_hotel_hk"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_swim_pool_hotel_hk_bodyweight_sub"
      ],
      "title": "Swimming aerobic session in hotel pool (Hong Kong)"
    },
    {
      "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
      "activity_id": "act_b02_cardio_swim_pool_hotel_hk_bodyweight_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Bodyweight/band aerobic session in hotel room if pool is unavailable or access is restricted.",
      "duration_minutes": 25,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "07:00-07:45"
        ],
        "type": "travel-window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "travel_adapted",
        "bodyweight"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 111,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel adaptation."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_swim_pool_hotel_hk_primary",
      "substitution_notes": "Preserves aerobic intent when pool is unavailable.",
      "substitution_reason_codes": [
        "facility_unavailable"
      ],
      "title": "Bodyweight aerobic session in hotel room (if pool unavailable)"
    },
    {
      "activity_family_id": "b02_cardio_walking_office",
      "activity_id": "act_b02_cardio_walking_office_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "office"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Short walking or movement break during office hours to support aerobic activity when full session is not possible.",
      "does_not_count_toward_goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "duration_minutes": 10,
      "facilitator_type": "self",
      "frequency": {
        "count": 3,
        "preferred_days": [
          "monday",
          "wednesday",
          "friday"
        ],
        "preferred_time_windows": [
          "10:30-11:00",
          "15:00-15:30"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "walking",
        "office_support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "last_resort_substitution_metadata": {
        "avoid_week_with_only_walks_unless_impossible": true,
        "calendar_reason_required_if_scheduled": true,
        "last_resort": true,
        "prefer_non_walk_aerobic_before_walk": true,
        "reason_code_examples": [
          "facility_unavailable",
          "equipment_unavailable",
          "travel_window",
          "time_conflict",
          "pain_or_fatigue"
        ]
      },
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 112,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Support-only."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_walking_office_remote_sub"
      ],
      "title": "Short walking or movement break at office",
      "walking_activity_metadata": {
        "counts_as_full_aerobic_session": false,
        "counts_as_strength": false,
        "walk_only_week_reason_field": "calendar_week_validation_reason",
        "walk_only_week_requires_reason": true
      },
      "wfh_scheduling_constraint": {
        "calendar_rejection_reason_required": true,
        "if_substitution_unavailable": "reject_or_unschedule",
        "on_member_location_home_day": "do_not_schedule_office_location",
        "preferred_substitution_activity_id": "act_b02_cardio_walking_office_remote_sub",
        "rejection_reason_code": "wfh_no_office_location_activity"
      }
    },
    {
      "activity_family_id": "b02_cardio_walking_office",
      "activity_id": "act_b02_cardio_walking_office_remote_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current aerobic goal"
      ],
      "dependencies": [],
      "details": "Short walking or movement break at home during WFH days to support movement without scheduling an office-location activity.",
      "does_not_count_toward_goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "duration_minutes": 10,
      "facilitator_type": "self",
      "frequency": {
        "count": 3,
        "preferred_days": [
          "monday",
          "wednesday",
          "friday"
        ],
        "preferred_time_windows": [
          "10:30-11:00",
          "15:00-15:30"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "walking",
        "home_support",
        "wfh"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "last_resort_substitution_metadata": {
        "avoid_week_with_only_walks_unless_impossible": true,
        "calendar_reason_required_if_scheduled": true,
        "last_resort": true,
        "prefer_non_walk_aerobic_before_walk": true,
        "reason_code_examples": [
          "facility_unavailable",
          "equipment_unavailable",
          "travel_window",
          "time_conflict",
          "pain_or_fatigue"
        ]
      },
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 113,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Support-only."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_walking_office_primary",
      "substitution_notes": "Preserves movement-break intent on WFH days without using office location.",
      "substitution_reason_codes": [
        "wfh_location_override",
        "facility_unavailable",
        "time_conflict"
      ],
      "title": "Short walking break at home during WFH",
      "walking_activity_metadata": {
        "counts_as_full_aerobic_session": false,
        "counts_as_strength": false,
        "walk_only_week_reason_field": "calendar_week_validation_reason",
        "walk_only_week_requires_reason": true
      },
      "wfh_scheduling_constraint": {
        "calendar_substitution_reason_required": true,
        "replaces_office_location_activity": true,
        "substitution_reason_code": "wfh_location_override",
        "valid_on_member_location_home_day": true
      }
    },
    {
      "activity_family_id": "b02_cardio_remote_coach_progression_review",
      "activity_id": "act_b02_cardio_remote_coach_progression_review_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent aerobic session data",
        "session duration",
        "RPE",
        "average heart rate if available",
        "barriers or missed-session notes"
      ],
      "dependencies": [
        {
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "lookback_days": 14,
          "minimum_sessions": 1,
          "must_exist": true,
          "notes": "Coach progression review requires at least one recent aerobic session log in the prior 14 days.",
          "type": "recent_session_data"
        }
      ],
      "details": "Remote check-in with Elyx health coach to review aerobic session adherence, barriers, and plan adjustments.",
      "duration_minutes": 20,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "monday"
        ],
        "preferred_time_windows": [
          "09:00-09:30",
          "19:00-20:00"
        ],
        "preferred_week": "second",
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Remote coach review supports adherence but does not count as a session.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "remote_coach",
        "progression_review"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "coach_notes",
        "next_action"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "lookback_days": 14,
        "minimum_recent_sessions": 1,
        "missing_data_policy": "defer_review_until_recent_aerobic_session_data_exists",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "aerobic_progression_data_review",
        "required_inputs": [
          "recent aerobic session data",
          "session duration",
          "RPE",
          "average heart rate if available",
          "barriers or missed-session notes"
        ],
        "required_recent_activity_goal_action_id": "ga_aerobic_conditioning_weekly",
        "requires_recent_activity_data": true
      },
      "prep_required": true,
      "priority": 114,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Support-only."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_remote_coach_progression_review_async_log_sub"
      ],
      "title": "Remote coach review of aerobic progression"
    },
    {
      "activity_family_id": "b02_cardio_remote_coach_progression_review",
      "activity_id": "act_b02_cardio_remote_coach_progression_review_async_log_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent aerobic session data",
        "session duration",
        "RPE",
        "average heart rate if available",
        "barriers or missed-session notes"
      ],
      "dependencies": [
        {
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "lookback_days": 14,
          "minimum_sessions": 1,
          "must_exist": true,
          "notes": "Coach progression review requires at least one recent aerobic session log in the prior 14 days.",
          "type": "recent_session_data"
        }
      ],
      "details": "Coach reviews wearable or session notes asynchronously and adjusts the next aerobic target when schedules prevent a live review.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "monday"
        ],
        "preferred_time_windows": [
          "09:00-09:30",
          "19:00-20:00"
        ],
        "preferred_week": "second",
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Preserves aerobic progression support when live coach availability is blocked.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "remote_coach",
        "progression_review"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "coach_notes",
        "next_action"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "lookback_days": 14,
        "minimum_recent_sessions": 1,
        "missing_data_policy": "defer_review_until_recent_aerobic_session_data_exists",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "aerobic_progression_data_review",
        "required_inputs": [
          "recent aerobic session data",
          "session duration",
          "RPE",
          "average heart rate if available",
          "barriers or missed-session notes"
        ],
        "required_recent_activity_goal_action_id": "ga_aerobic_conditioning_weekly",
        "requires_recent_activity_data": true
      },
      "prep_required": true,
      "priority": 117,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_remote_coach_progression_review_primary",
      "substitution_notes": "Preserves aerobic progression support when live coach availability is blocked.",
      "substitution_reason_codes": [
        "time_conflict",
        "remote_delivery_needed"
      ],
      "title": "Async aerobic log review"
    },
    {
      "activity_family_id": "b02_cardio_cgm_log_support",
      "activity_id": "act_b02_cardio_cgm_log_support_primary",
      "activity_type": "medication",
      "allowed_locations": [
        "home",
        "office",
        "travel_hotel"
      ],
      "care_context_required": [
        "recent aerobic or meal session"
      ],
      "dependencies": [],
      "details": "Continuous glucose monitor (CGM) check and log to support metabolic tracking. Performed as needed after aerobic or meal sessions.",
      "duration_minutes": 5,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "07:00-08:00",
          "19:00-20:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "CGM log supports adherence but does not count as a core outcome.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "cgm",
        "adherence_support",
        "metabolic_tracking"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "glucose_value",
        "log_time"
      ],
      "prep_required": false,
      "priority": 115,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "dietitian",
        "physician"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Support-only."
      },
      "substitution_activity_ids": [],
      "title": "CGM check and log (as needed)"
    },
    {
      "activity_family_id": "b02_cardio_hydration_protocol_support",
      "activity_id": "act_b02_cardio_hydration_protocol_support_primary",
      "activity_type": "medication",
      "allowed_locations": [
        "home",
        "travel_hotel",
        "office"
      ],
      "care_context_required": [
        "travel window",
        "recent aerobic session"
      ],
      "dependencies": [],
      "details": "Hydration and electrolyte protocol to support energy and recovery, especially during travel or after aerobic sessions.",
      "duration_minutes": 5,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "07:00-08:00",
          "18:00-19:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Hydration protocol supports adherence but does not count as a core outcome.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "hydration",
        "adherence_support",
        "travel_support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "hydration_amount"
      ],
      "prep_required": false,
      "priority": 116,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "dietitian",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Support-only."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_hydration_protocol_support_hotel_protocol_sub"
      ],
      "title": "Hydration and electrolyte protocol (especially during travel)"
    },
    {
      "activity_family_id": "b02_cardio_hydration_protocol_support",
      "activity_id": "act_b02_cardio_hydration_protocol_support_hotel_protocol_sub",
      "activity_type": "medication",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel window",
        "recent aerobic session"
      ],
      "dependencies": [],
      "details": "Travel-compatible hydration and electrolyte check using hotel-room supplies before or after aerobic work.",
      "duration_minutes": 5,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "07:00-08:00",
          "18:00-19:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Preserves hydration support when the member is travelling or away from the usual setup.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "hydration",
        "adherence_support",
        "travel_support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "hydration_amount"
      ],
      "prep_required": false,
      "priority": 119,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "dietitian",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_hydration_protocol_support_primary",
      "substitution_notes": "Preserves hydration support when the member is travelling or away from the usual setup.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable"
      ],
      "title": "Hotel-room hydration protocol"
    },
    {
      "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
      "activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "travel_hotel",
        "office"
      ],
      "care_context_required": [
        "facility/equipment status"
      ],
      "dependencies": [],
      "details": "Aerobic session using bodyweight and mini bands when gym or equipment is unavailable due to travel, maintenance, or time conflict.",
      "duration_minutes": 35,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_days": [
          "thursday",
          "sunday"
        ],
        "preferred_time_windows": [
          "18:45-20:00",
          "08:00-10:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Counts as aerobic conditioning if gym or equipment is unavailable.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "facility_unavailable",
        "travel_adapted"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 117,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel/facility adaptation."
      },
      "substitution_activity_ids": [
        "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub"
      ],
      "title": "Aerobic session using bodyweight/bands (facility unavailable)"
    },
    {
      "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
      "activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "travel_hotel",
        "office"
      ],
      "care_context_required": [
        "facility/equipment status"
      ],
      "dependencies": [],
      "details": "Brisk walking session outdoors or in hotel corridors when all other aerobic options are blocked.",
      "does_not_count_toward_goal_action_ids": [
        "ga_strength_sessions_weekly"
      ],
      "duration_minutes": 30,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_days": [
          "thursday",
          "sunday"
        ],
        "preferred_time_windows": [
          "18:45-20:00",
          "08:00-10:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_aerobic_conditioning_weekly",
          "goal_id": "goal_metabolic_health",
          "notes": "Walking does not count as strength. It may count as an aerobic fallback only when non-walk aerobic options are impossible; scheduler must record why if the week would otherwise contain only walks.",
          "role": "core",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "aerobic_conditioning",
        "facility_unavailable",
        "walking"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "last_resort_substitution_metadata": {
        "avoid_week_with_only_walks_unless_impossible": true,
        "calendar_reason_required_if_scheduled": true,
        "last_resort": true,
        "prefer_non_walk_aerobic_before_walk": true,
        "reason_code_examples": [
          "facility_unavailable",
          "equipment_unavailable",
          "travel_window",
          "time_conflict",
          "pain_or_fatigue"
        ]
      },
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "RPE",
        "session_duration"
      ],
      "prep_required": false,
      "priority": 118,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Travel/facility adaptation."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_primary",
      "substitution_notes": "Preserves aerobic intent with brisk walking when all other options are blocked.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "equipment_unavailable",
        "time_conflict"
      ],
      "title": "Brisk walking session (facility/equipment unavailable)",
      "walking_activity_metadata": {
        "counts_as_full_aerobic_session": true,
        "counts_as_strength": false,
        "walk_only_week_reason_field": "calendar_week_validation_reason",
        "walk_only_week_requires_reason": true
      }
    },
    {
      "activity_family_id": "b03_strength_trainer_gym",
      "activity_id": "act_b03_strength_trainer_gym_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "gym"
      ],
      "care_context_required": [
        "current knee/back status",
        "recent physio notes",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Full-body strength session with knee-safe modifications, led by Elyx Performance Trainer. Focus on progressive overload and safe lower-body work.",
      "duration_minutes": 60,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "sunday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "19:30-20:30",
          "18:45-20:00",
          "11:00-12:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Trainer-led gym strength session directly counts toward weekly strength goal.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "high",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 181,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_strength_machines_gym",
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_strength_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule lower-load or mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [
        "act_b03_strength_trainer_gym_remote"
      ],
      "title": "Trainer-led knee-safe strength session at gym"
    },
    {
      "activity_family_id": "b03_strength_trainer_gym",
      "activity_id": "act_b03_strength_trainer_gym_remote",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status",
        "recent physio notes",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Live remote session with Elyx Performance Trainer using available home or travel equipment. Focus on knee-safe movements and maintaining progression.",
      "duration_minutes": 50,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "sunday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "19:30-20:30",
          "18:45-20:00",
          "11:00-12:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Remote trainer-led session counts toward weekly strength goal if in-person is unavailable.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led",
        "remote"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 182,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_strength_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule lower-load or mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_trainer_gym_primary",
      "substitution_notes": "Preserves trainer-led strength intent when in-person or gym is unavailable.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "facility_unavailable",
        "time_conflict"
      ],
      "title": "Remote trainer-led strength session"
    },
    {
      "activity_family_id": "b03_strength_home_strength",
      "activity_id": "act_b03_strength_home_strength_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "current knee/back status",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Strength session using dumbbells, bands, and bodyweight at home. Focus on knee-safe lower-body and core movements.",
      "duration_minutes": 45,
      "facilitator_type": "member",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday",
          "sunday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "19:45-20:30",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Home-based strength session directly counts toward weekly strength goal.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "home_based"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 183,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_dumbbells_home",
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule mobility or lower-load session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [
        "act_b03_strength_hotel_gym_strength_primary",
        "act_b03_strength_home_strength_travel"
      ],
      "title": "Home-based knee-safe strength session"
    },
    {
      "activity_family_id": "b03_strength_home_strength",
      "activity_id": "act_b03_strength_home_strength_travel",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel",
        "remote"
      ],
      "care_context_required": [
        "current knee/back status",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Strength session using portable bands and bodyweight in hotel or remote setting. Focus on maintaining movement quality and knee safety.",
      "duration_minutes": 35,
      "facilitator_type": "member",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday",
          "sunday",
          "wednesday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Travel-adapted session counts toward weekly strength goal if home is unavailable.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "travel_adapted"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 184,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
      "substitution_notes": "Preserves home-based strength intent using travel-compatible equipment.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "equipment_unavailable",
        "time_conflict"
      ],
      "title": "Travel-adapted strength session (bands/bodyweight)"
    },
    {
      "activity_family_id": "b03_strength_home_strength",
      "activity_id": "act_b03_strength_hotel_gym_strength_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status"
      ],
      "dependencies": [],
      "details": "Strength session using available hotel gym equipment. Focus on maintaining strength and mobility during travel.",
      "duration_minutes": 40,
      "facilitator_type": "member",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "tuesday",
          "sunday",
          "wednesday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Hotel gym strength session counts toward weekly strength goal when travel prevents home strength.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "hotel_gym",
        "travel_continuity"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 183,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_basic_gym_hotel_tokyo",
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule bodyweight/band session.",
        "trigger": "equipment_unavailable"
      },
      "substitution_activity_ids": [
        "act_b03_strength_hotel_gym_strength_bodyweight"
      ],
      "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
      "substitution_notes": "Use hotel gym equipment during Tokyo-style travel before falling back to in-room bands/bodyweight.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_available",
        "equipment_available"
      ],
      "title": "Hotel gym strength session (travel window)"
    },
    {
      "activity_family_id": "b03_strength_home_strength",
      "activity_id": "act_b03_strength_hotel_gym_strength_bodyweight",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status"
      ],
      "dependencies": [],
      "details": "Strength session using only bodyweight and portable bands in hotel room. Focus on movement quality and knee safety.",
      "duration_minutes": 30,
      "facilitator_type": "member",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "tuesday",
          "sunday",
          "wednesday"
        ],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "In-room bodyweight/band session counts toward weekly strength goal only when hotel gym equipment is unavailable.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "bodyweight",
        "travel_continuity"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 186,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_home_strength_primary",
      "substitution_notes": "Preserves travel strength intent when hotel gym equipment is unavailable.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable",
        "equipment_unavailable"
      ],
      "title": "Bodyweight/band strength session in hotel room"
    },
    {
      "activity_family_id": "b03_strength_bodyweight_travel_substitution",
      "activity_id": "act_b03_strength_bodyweight_travel_substitution_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status"
      ],
      "dependencies": [],
      "details": "Travel-adapted strength session coached by Ravi using bodyweight and portable bands in the hotel room. Focus on movement quality and knee safety.",
      "duration_minutes": 25,
      "facilitator_type": "travel_trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "18:45-20:00",
          "07:00-08:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Ravi-led bodyweight/band session counts toward weekly strength only for low-resource travel when no hotel gym is available.",
          "role": "core",
          "unit": "session",
          "value": 1
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "bodyweight",
        "travel_low_resource"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 187,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_travel_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [
        "act_b03_strength_bodyweight_travel_substitution_remote"
      ],
      "title": "Bodyweight/band strength session (low-resource travel)"
    },
    {
      "activity_family_id": "b03_strength_bodyweight_travel_substitution",
      "activity_id": "act_b03_strength_bodyweight_travel_substitution_remote",
      "activity_type": "fitness",
      "allowed_locations": [
        "travel_hotel",
        "remote"
      ],
      "care_context_required": [
        "current knee/back status"
      ],
      "dependencies": [],
      "details": "Remote coach provides live or asynchronous guidance for bodyweight/band strength session in hotel room.",
      "duration_minutes": 20,
      "facilitator_type": "travel_trainer",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "18:45-20:00",
          "07:00-08:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Remote coach check-in supports travel continuity when member needs guidance.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "remote_coach",
        "travel_low_resource"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 188,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_travel_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "adjustment": "Schedule mobility session and flag for care-team review.",
        "trigger": "pain_or_fatigue"
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_bodyweight_travel_substitution_primary",
      "substitution_notes": "Preserves travel strength intent with remote coach support when member needs guidance.",
      "substitution_reason_codes": [
        "travel_window",
        "equipment_unavailable",
        "lower_load_needed"
      ],
      "title": "Remote coach-guided strength session (travel)"
    },
    {
      "activity_family_id": "b03_strength_mobility_post_travel",
      "activity_id": "act_b03_strength_mobility_post_travel_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent travel details",
        "current pain/tightness status"
      ],
      "dependencies": [],
      "details": "Guided mobility and stretching session at home to address fatigue and lower-back tightness after travel.",
      "duration_minutes": 30,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "18:45-20:00",
          "20:00-21:30"
        ],
        "type": "post_travel"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Post-travel mobility session supports recovery but does not count as strength unless explicitly substituted.",
          "role": "recovery",
          "unit": "action",
          "value": 0
        }
      ],
      "goal_tags": [
        "mobility",
        "recovery",
        "post_travel"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "mobility_score",
        "pain_level"
      ],
      "prep_required": false,
      "priority": 189,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_yoga_mat",
        "eq_mini_band"
      ],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physiotherapist",
        "trainer"
      ],
      "skip_adjustment": {
        "adjustment": "Member-led mobility session.",
        "trigger": "provider_unavailable"
      },
      "substitution_activity_ids": [
        "act_b03_strength_mobility_post_travel_member"
      ],
      "title": "Mobility and recovery session after travel"
    },
    {
      "activity_family_id": "b03_strength_mobility_post_travel",
      "activity_id": "act_b03_strength_mobility_post_travel_member",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent travel details",
        "current pain/tightness status"
      ],
      "dependencies": [],
      "details": "Self-guided mobility and stretching routine at home using mat and bands to address post-travel fatigue.",
      "duration_minutes": 25,
      "facilitator_type": "member",
      "frequency": {
        "count": 1,
        "preferred_days": [],
        "preferred_time_windows": [
          "18:45-20:00",
          "06:30-08:00",
          "07:15-08:00",
          "19:50-20:30"
        ],
        "type": "post_travel"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Member-led session supports recovery if physio is unavailable.",
          "role": "recovery",
          "unit": "action",
          "value": 0
        }
      ],
      "goal_tags": [
        "mobility",
        "recovery",
        "post_travel",
        "member_led"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "mobility_score",
        "pain_level"
      ],
      "prep_required": false,
      "priority": 190,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_yoga_mat",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physiotherapist",
        "trainer"
      ],
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_mobility_post_travel_primary",
      "substitution_notes": "Preserves post-travel recovery intent when provider is unavailable.",
      "substitution_reason_codes": [
        "travel_window",
        "pain_or_fatigue"
      ],
      "title": "Member-led mobility and stretching after travel"
    },
    {
      "activity_family_id": "b03_strength_physio_assessment_due",
      "activity_id": "act_b03_strength_physio_assessment_due_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "home",
        "gym",
        "clinic"
      ],
      "care_context_required": [
        "recent pain escalation details",
        "current movement plan",
        "recent training load notes",
        "mobility limitation summary"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain escalation details",
            "current movement plan",
            "recent training load notes",
            "mobility limitation summary"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "In-person physiotherapist assessment to review knee/back status and update movement plan after travel or when clinically indicated.",
      "duration_minutes": 30,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "preferred_time_windows": [
          "08:00-09:00",
          "18:45-20:00",
          "19:00-20:00"
        ],
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Physio assessment counts toward 3-month clinical review goal when due.",
          "role": "measurement",
          "unit": "review",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "physio_assessment",
        "pain_review",
        "measurement"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "pain_level",
        "mobility_score",
        "provider_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain escalation details",
          "current movement plan",
          "recent training load notes",
          "mobility limitation summary"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_yoga_mat",
        "eq_mini_band"
      ],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [
        "act_b03_strength_physio_assessment_due_remote"
      ],
      "title": "Initial physiotherapist assessment"
    },
    {
      "activity_family_id": "b03_strength_physio_assessment_due",
      "activity_id": "act_b03_strength_physio_assessment_due_remote",
      "activity_type": "consultation",
      "allowed_locations": [
        "home",
        "remote"
      ],
      "care_context_required": [
        "recent pain escalation details",
        "current movement plan",
        "recent training load notes",
        "mobility limitation summary"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain escalation details",
            "current movement plan",
            "recent training load notes",
            "mobility limitation summary"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote video assessment with physiotherapist to review pain and update movement plan after escalation or travel.",
      "duration_minutes": 30,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "preferred_time_windows": [
          "08:00-09:00",
          "18:45-20:00",
          "19:00-20:00"
        ],
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Remote physio assessment counts toward 3-month review goal if in-person is unavailable.",
          "role": "measurement",
          "unit": "review",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "physio_assessment",
        "pain_review",
        "remote"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "pain_level",
        "mobility_score",
        "provider_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain escalation details",
          "current movement plan",
          "recent training load notes",
          "mobility limitation summary"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_physio_assessment_due_primary",
      "substitution_notes": "Preserves assessment intent when in-person provider is unavailable.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "remote_delivery_needed"
      ],
      "title": "Remote physiotherapist assessment"
    },
    {
      "activity_family_id": "b03_strength_trainer_remote_substitution",
      "activity_id": "act_b03_strength_trainer_remote_substitution_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status",
        "recent physio notes",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Live remote session with Elyx Performance Trainer using available equipment. Used when in-person session is not possible.",
      "duration_minutes": 45,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "08:00-09:00",
          "18:45-20:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Remote trainer-led session is support-only unless explicitly scheduled as core.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led",
        "remote"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 193,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [
        "act_b03_strength_trainer_remote_substitution_async_plan_sub"
      ],
      "title": "Remote trainer-led strength session (as-needed)"
    },
    {
      "activity_family_id": "b03_strength_trainer_remote_substitution",
      "activity_id": "act_b03_strength_trainer_remote_substitution_async_plan_sub",
      "activity_type": "fitness",
      "allowed_locations": [
        "remote",
        "home",
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status",
        "recent physio notes",
        "strength progression log"
      ],
      "dependencies": [],
      "details": "Trainer sends a knee-safe strength plan for self-guided completion when a live remote session cannot be scheduled.",
      "duration_minutes": 15,
      "facilitator_type": "trainer",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "08:00-09:00",
          "18:45-20:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "trainer_led",
        "remote"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 196,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_trainer_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_trainer_remote_substitution_primary",
      "substitution_notes": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "time_conflict"
      ],
      "title": "Async trainer strength plan"
    },
    {
      "activity_family_id": "b03_strength_lower_load_strength_adjustment",
      "activity_id": "act_b03_strength_lower_load_strength_adjustment_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent pain/fatigue details"
      ],
      "dependencies": [],
      "details": "Reduced-load strength session at home with focus on safe movement and pain avoidance. Used after pain escalation or fatigue.",
      "duration_minutes": 30,
      "facilitator_type": "member",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "18:45-20:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Lower-load session is support-only unless explicitly scheduled as core after pain/fatigue.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "lower_load",
        "pain_fatigue"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "pain_level"
      ],
      "prep_required": false,
      "priority": 194,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [],
      "title": "Lower-load strength session after pain or fatigue"
    },
    {
      "activity_family_id": "b03_strength_lower_load_strength_adjustment",
      "activity_id": "act_b03_strength_lower_load_strength_adjustment_remote",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "remote"
      ],
      "care_context_required": [
        "recent pain/fatigue details"
      ],
      "dependencies": [],
      "details": "Remote coach provides guidance for lower-load strength session after pain or fatigue.",
      "duration_minutes": 20,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 0,
        "preferred_days": [],
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "18:45-20:00"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Remote coach check-in supports lower-load session if member needs guidance.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "lower_load",
        "remote"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "pain_level"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "recent pain/fatigue details"
        ]
      },
      "prep_required": true,
      "priority": 195,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_lower_load_strength_adjustment_primary",
      "substitution_notes": "Preserves lower-load strength intent with remote coach support after pain/fatigue.",
      "substitution_reason_codes": [
        "lower_load_needed",
        "pain_or_fatigue"
      ],
      "title": "Remote coach check-in for lower-load strength"
    },
    {
      "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
      "activity_id": "act_b03_strength_mobility_pain_recovery_checkin_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "recent travel or skipped session details",
        "current pain/mobility status"
      ],
      "dependencies": [],
      "details": "Physiotherapist check-in to review pain, mobility, and recovery after travel or missed high-load session.",
      "duration_minutes": 15,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "friday"
        ],
        "preferred_time_windows": [
          "16:00-18:00",
          "19:00-20:00"
        ],
        "preferred_week": "third",
        "preferred_weeks": [
          "third",
          "fourth",
          "third"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "goal_id": "goal_travel_resilience",
          "notes": "Remote check-in supports travel continuity and pain/mobility review.",
          "role": "support",
          "unit": "review",
          "value": 1
        }
      ],
      "goal_tags": [
        "mobility",
        "pain_review",
        "travel_recovery",
        "remote_checkin"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_005",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "pain_level",
        "mobility_score",
        "next_actions"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "recent travel or skipped session details",
          "current pain/mobility status"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physiotherapist",
        "trainer"
      ],
      "substitution_activity_ids": [
        "act_b03_strength_mobility_pain_recovery_checkin_pain_note_sub"
      ],
      "title": "Physiotherapist recovery check-in after travel or skipped session"
    },
    {
      "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
      "activity_id": "act_b03_strength_mobility_pain_recovery_checkin_pain_note_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent travel or skipped session details",
        "current pain/mobility status"
      ],
      "dependencies": [],
      "details": "Coach or physio reviews pain, fatigue, and travel notes asynchronously and recommends the safest next session option.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "20:00-21:30",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "goal_id": "goal_travel_resilience",
          "notes": "Preserves pain-aware recovery support when a live check-in cannot fit.",
          "role": "support",
          "unit": "review",
          "value": 1
        }
      ],
      "goal_tags": [
        "mobility",
        "pain_review",
        "travel_recovery",
        "remote_checkin"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_005",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "pain_level",
        "mobility_score",
        "next_actions"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "recent travel or skipped session details",
          "current pain/mobility status"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physiotherapist",
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_mobility_pain_recovery_checkin_primary",
      "substitution_notes": "Preserves pain-aware recovery support when a live check-in cannot fit.",
      "substitution_reason_codes": [
        "pain_or_fatigue",
        "remote_delivery_needed"
      ],
      "title": "Async pain recovery note review"
    },
    {
      "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
      "activity_id": "act_b03_strength_provider_unavailable_strength_substitution_primary",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status",
        "approved protocol"
      ],
      "dependencies": [],
      "details": "Member-led or remote-guided knee-safe strength session when trainer is unavailable. Follows approved protocol.",
      "duration_minutes": 40,
      "facilitator_type": "member",
      "frequency": {
        "applies_when": [
          "provider_unavailable",
          "remote_delivery_needed"
        ],
        "count": 0,
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Trainer-unavailable strength alternative is support-only unless scheduled as core.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "provider_unavailable",
        "remote"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_required": false,
      "priority": 197,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [
        "act_b03_strength_provider_unavailable_strength_substitution_remote"
      ],
      "title": "Knee-safe strength session when trainer unavailable"
    },
    {
      "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
      "activity_id": "act_b03_strength_provider_unavailable_strength_substitution_remote",
      "activity_type": "fitness",
      "allowed_locations": [
        "home",
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "current knee/back status",
        "approved protocol"
      ],
      "dependencies": [],
      "details": "Remote coach provides protocol check and guidance for knee-safe strength session when trainer is unavailable.",
      "duration_minutes": 20,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "applies_when": [
          "provider_unavailable",
          "remote_delivery_needed"
        ],
        "count": 0,
        "preferred_time_windows": [
          "06:30-08:00",
          "07:15-08:00",
          "18:45-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_strength_sessions_weekly",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Remote coach check-in supports member-led session if trainer is unavailable.",
          "role": "support",
          "unit": "session",
          "value": 0
        }
      ],
      "goal_tags": [
        "strength",
        "knee_safe",
        "provider_unavailable",
        "remote"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "load_level": "medium",
      "metrics_to_collect": [
        "completion",
        "sets_reps",
        "RPE",
        "knee_discomfort"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "current knee/back status",
          "approved protocol"
        ]
      },
      "prep_required": true,
      "priority": 198,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b03_strength_provider_unavailable_strength_substitution_primary",
      "substitution_notes": "Preserves knee-safe strength intent with remote coach support when trainer is unavailable.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "remote_delivery_needed",
        "time_conflict"
      ],
      "title": "Remote coach check-in for trainer-unavailable strength"
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_home",
      "activity_id": "act_b04_recovery_evening_mobility_home_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent sleep duration",
        "mobility limitation summary"
      ],
      "dependencies": [],
      "details": "Guided mobility, stretching, or foam rolling at home to support sleep quality and recovery. Can be member-led or with remote coach input.",
      "duration_minutes": 30,
      "facilitator_type": "self_or_remote_coach",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "monday",
          "thursday"
        ],
        "preferred_time_windows": [
          "20:00-21:30"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Directly supports weekly recovery/sleep goal.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "sleep_quality",
        "mobility",
        "recovery"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_quality_next_morning",
        "mobility_score"
      ],
      "prep_required": false,
      "priority": 261,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_yoga_mat",
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is traveling or has late work obligations, use travel/remote variant."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_evening_mobility_home_sub_time_conflict"
      ],
      "title": "Evening home-based mobility and recovery session"
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_home",
      "activity_id": "act_b04_recovery_evening_mobility_home_sub_time_conflict",
      "activity_type": "therapy",
      "allowed_locations": [
        "home",
        "remote"
      ],
      "care_context_required": [
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Shorter, remote-guided mobility or stretching session for evenings when home routine is not feasible.",
      "duration_minutes": 20,
      "facilitator_type": "remote_coach",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "monday",
          "thursday"
        ],
        "preferred_time_windows": [
          "21:00-22:15"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Counts as recovery if primary is blocked by time or provider constraints.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "sleep_quality",
        "mobility",
        "recovery"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_quality_next_morning"
      ],
      "prep_required": false,
      "priority": 262,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is traveling, use travel-specific variant."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_evening_mobility_home_primary",
      "substitution_notes": "Preserves evening recovery intent when home routine is not feasible.",
      "substitution_reason_codes": [
        "time_conflict",
        "provider_unavailable"
      ],
      "title": "Remote-guided evening mobility session"
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_travel",
      "activity_id": "act_b04_recovery_evening_mobility_travel_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel fatigue",
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Travel-adapted mobility or stretching session in hotel room or gym, supporting sleep and recovery during travel.",
      "duration_minutes": 20,
      "facilitator_type": "self_or_remote_coach",
      "frequency": {
        "count": 3,
        "preferred_time_windows": [
          "20:00-21:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Travel mobility counts toward weekly recovery because fatigue reduction is especially important during travel weeks.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "goal_id": "goal_travel_resilience",
          "notes": "Supports travel continuity.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "mobility",
        "recovery"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_quality_next_morning"
      ],
      "prep_required": false,
      "priority": 263,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If hotel gym is unavailable, use in-room variant."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_evening_mobility_travel_sub_facility_unavailable"
      ],
      "title": "Hotel-based evening mobility and recovery session"
    },
    {
      "activity_family_id": "b04_recovery_evening_mobility_travel",
      "activity_id": "act_b04_recovery_evening_mobility_travel_sub_facility_unavailable",
      "activity_type": "therapy",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel fatigue"
      ],
      "dependencies": [],
      "details": "Short in-room mobility or stretching session when hotel gym is unavailable or late arrival limits options.",
      "duration_minutes": 15,
      "facilitator_type": "self",
      "frequency": {
        "count": 3,
        "preferred_time_windows": [
          "21:00-22:15"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "mobility",
        "recovery"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 264,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is fatigued or arrives late, use this variant."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_evening_mobility_travel_primary",
      "substitution_notes": "Preserves recovery intent when hotel gym or facilities are unavailable.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable"
      ],
      "title": "In-room mobility and stretching session (travel)"
    },
    {
      "activity_family_id": "b04_recovery_sleep_routine_support",
      "activity_id": "act_b04_recovery_sleep_routine_support_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Guided wind-down protocol including light stretching, breathwork, and screen cutoff to support sleep onset.",
      "duration_minutes": 20,
      "facilitator_type": "self",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "tuesday",
          "sunday"
        ],
        "preferred_time_windows": [
          "22:00-22:30"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Directly supports weekly recovery/sleep goal.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "sleep_quality",
        "evening_routine"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_onset_time",
        "sleep_quality_next_morning"
      ],
      "prep_required": false,
      "priority": 265,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": false
      },
      "substitution_activity_ids": [
        "act_b04_recovery_sleep_routine_support_hotel_wind_down_sub"
      ],
      "title": "Home-based sleep wind-down routine"
    },
    {
      "activity_family_id": "b04_recovery_sleep_routine_support",
      "activity_id": "act_b04_recovery_sleep_routine_support_hotel_wind_down_sub",
      "activity_type": "therapy",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Hotel-room version of the wind-down protocol with breathwork, light mobility, and screen cutoff when Marcus is travelling.",
      "duration_minutes": 20,
      "facilitator_type": "self",
      "frequency": {
        "count": 2,
        "preferred_days": [
          "tuesday",
          "sunday"
        ],
        "preferred_time_windows": [
          "22:00-22:30"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Preserves sleep-routine intent when Marcus is away from home.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "sleep_quality",
        "evening_routine"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_onset_time",
        "sleep_quality_next_morning"
      ],
      "prep_required": false,
      "priority": 268,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_sleep_routine_support_primary",
      "substitution_notes": "Preserves sleep-routine intent when Marcus is away from home.",
      "substitution_reason_codes": [
        "travel_window"
      ],
      "title": "Hotel sleep wind-down routine"
    },
    {
      "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
      "activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "travel fatigue",
        "pain escalation"
      ],
      "dependencies": [],
      "details": "Mobility, stretching, and guided recovery session at home after return from travel over 3 hours.",
      "duration_minutes": 25,
      "facilitator_type": "self_or_remote_coach",
      "frequency": {
        "count": 3,
        "preferred_time_windows": [
          "18:45-20:00"
        ],
        "type": "post_travel"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Post-travel adaptation; does not count toward normal-week denominator.",
          "role": "recovery",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_behavior_coaching_weekly",
          "goal_id": "goal_travel_resilience",
          "notes": "Supports travel continuity.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "post_travel",
        "fatigue",
        "recovery"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "fatigue_score",
        "mobility_score"
      ],
      "prep_required": false,
      "priority": 266,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_yoga_mat",
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member experiences pain or severe fatigue, use lower-load variant."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_post_travel_fatigue_adjustment_sub_fatigue"
      ],
      "title": "Post-travel fatigue recovery session at home"
    },
    {
      "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
      "activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_sub_fatigue",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "travel fatigue"
      ],
      "dependencies": [],
      "details": "Shortened, gentle stretching or breathwork session for severe fatigue or pain after travel.",
      "duration_minutes": 10,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "19:30-20:00"
        ],
        "type": "post_travel"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "value": 1
        }
      ],
      "goal_tags": [
        "post_travel",
        "fatigue",
        "recovery"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 267,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is too fatigued for full session, use this variant."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_primary",
      "substitution_notes": "Preserves recovery intent when member is too fatigued for full session.",
      "substitution_reason_codes": [
        "travel_window",
        "pain_or_fatigue"
      ],
      "title": "Short fatigue-adjusted recovery session (post-travel)"
    },
    {
      "activity_family_id": "b04_recovery_breathwork_support",
      "activity_id": "act_b04_recovery_breathwork_support_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent stressors"
      ],
      "dependencies": [],
      "details": "Guided or self-led breathwork, mindfulness, or stress regulation session to support sleep and recovery.",
      "duration_minutes": 10,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "20:30-22:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Support-only; does not count toward core goal.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "breathwork",
        "stress_regulation"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "stress_score"
      ],
      "prep_required": false,
      "priority": 268,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is traveling, can be performed in hotel room."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_breathwork_support_audio_guided_sub"
      ],
      "title": "Breathwork or stress regulation session"
    },
    {
      "activity_family_id": "b04_recovery_breathwork_support",
      "activity_id": "act_b04_recovery_breathwork_support_audio_guided_sub",
      "activity_type": "therapy",
      "allowed_locations": [
        "home",
        "travel_hotel",
        "remote"
      ],
      "care_context_required": [
        "recent stressors"
      ],
      "dependencies": [],
      "details": "Self-guided breathwork using a short audio protocol when coach support or a quiet home window is not available.",
      "duration_minutes": 10,
      "facilitator_type": "self",
      "frequency": {
        "count": 0,
        "preferred_time_windows": [
          "20:30-22:30"
        ],
        "type": "as_needed"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Preserves stress-regulation intent with a lower-friction delivery mode.",
          "role": "support",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "breathwork",
        "stress_regulation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "stress_score"
      ],
      "prep_required": false,
      "priority": 271,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_breathwork_support_primary",
      "substitution_notes": "Preserves stress-regulation intent with a lower-friction delivery mode.",
      "substitution_reason_codes": [
        "time_conflict",
        "remote_delivery_needed"
      ],
      "title": "Audio-guided breathwork session"
    },
    {
      "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
      "activity_id": "act_b04_recovery_remote_coach_recovery_checkin_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "travel fatigue",
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Remote check-in with Elyx coach to review recovery, sleep, and fatigue during travel windows.",
      "duration_minutes": 15,
      "facilitator_type": "remote_coach",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "19:00-20:00"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "goal_id": "goal_travel_resilience",
          "notes": "Support-only; does not count as a recovery action.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "remote_support"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "fatigue_score",
        "sleep_quality"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "travel fatigue",
          "recent sleep duration"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is unavailable, coach may send asynchronous check-in."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_remote_coach_recovery_checkin_async_sleep_note_sub"
      ],
      "title": "Remote coach check-in for recovery and sleep (travel)"
    },
    {
      "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
      "activity_id": "act_b04_recovery_remote_coach_recovery_checkin_async_sleep_note_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "travel fatigue",
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Remote coach reviews sleep notes and travel context asynchronously, then updates the recovery plan.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "19:00-20:00"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "goal_id": "goal_travel_resilience",
          "notes": "Preserves recovery check-in support when live coach availability is limited.",
          "role": "support",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "remote_support"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "fatigue_score",
        "sleep_quality"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "context_review",
        "required_inputs": [
          "travel fatigue",
          "recent sleep duration"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_remote_coach_recovery_checkin_primary",
      "substitution_notes": "Preserves recovery check-in support when live coach availability is limited.",
      "substitution_reason_codes": [
        "time_conflict",
        "travel_window"
      ],
      "title": "Async sleep recovery note review"
    },
    {
      "activity_family_id": "b04_recovery_evening_routine_travel",
      "activity_id": "act_b04_recovery_evening_routine_travel_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel fatigue"
      ],
      "dependencies": [],
      "details": "Adapted wind-down protocol for hotel environment: screen cutoff, light stretching, and breathwork to support sleep onset during travel.",
      "duration_minutes": 15,
      "facilitator_type": "self",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "22:00-22:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Travel sleep routine counts toward weekly recovery because fatigue reduction is especially important during travel weeks.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "sleep_quality"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_onset_time"
      ],
      "prep_required": false,
      "priority": 270,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is fatigued or arrives late, use shorter variant."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_evening_routine_travel_sub_facility_unavailable"
      ],
      "title": "Hotel-based evening sleep routine"
    },
    {
      "activity_family_id": "b04_recovery_evening_routine_travel",
      "activity_id": "act_b04_recovery_evening_routine_travel_sub_facility_unavailable",
      "activity_type": "therapy",
      "allowed_locations": [
        "travel_hotel"
      ],
      "care_context_required": [
        "travel fatigue"
      ],
      "dependencies": [],
      "details": "Very brief wind-down protocol for late arrival or high fatigue: screen cutoff and 3-minute breathwork.",
      "duration_minutes": 8,
      "facilitator_type": "self",
      "frequency": {
        "count": 3,
        "preferred_time_windows": [
          "22:15-22:30"
        ],
        "type": "travel_window"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Short hotel wind-down counts toward weekly recovery when travel fatigue makes the full routine impractical.",
          "role": "recovery",
          "unit": "activity",
          "value": 1
        }
      ],
      "goal_tags": [
        "travel",
        "sleep_quality"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 271,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is too fatigued for full routine, use this variant."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_evening_routine_travel_primary",
      "substitution_notes": "Preserves sleep routine intent when member is too fatigued or arrives late.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable"
      ],
      "title": "Shortened hotel wind-down routine (travel)"
    },
    {
      "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
      "activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_primary",
      "activity_type": "therapy",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent sleep duration",
        "fatigue"
      ],
      "dependencies": [],
      "details": "Explicit protocol to lower planned training load and insert recovery/mobility after poor sleep, pain, or fatigue.",
      "duration_minutes": 15,
      "facilitator_type": "self_or_remote_coach",
      "frequency": {
        "applies_when": [
          "poor_sleep",
          "pain_or_fatigue",
          "lower_load_needed"
        ],
        "count": 0,
        "preferred_time_windows": [
          "06:30-08:00",
          "18:45-20:00"
        ],
        "type": "constraint_scoped"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Recovery logic for poor sleep or fatigue; does not count as core action.",
          "role": "recovery",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "load_adjustment",
        "poor_sleep",
        "recovery"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "sleep_quality_next_morning",
        "fatigue_score"
      ],
      "prep_required": false,
      "priority": 272,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight",
        "eq_yoga_mat"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [
        "remote_coach_pool"
      ],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is traveling, use travel-compatible variant."
      },
      "substitution_activity_ids": [
        "act_b04_recovery_load_adjustment_after_poor_sleep_sub_lower_load"
      ],
      "title": "Load adjustment and recovery protocol after poor sleep"
    },
    {
      "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
      "activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_sub_lower_load",
      "activity_type": "therapy",
      "allowed_locations": [
        "home",
        "remote"
      ],
      "care_context_required": [
        "recent sleep duration"
      ],
      "dependencies": [],
      "details": "Short mobility or breathwork session to replace planned higher-load activity after poor sleep or fatigue.",
      "duration_minutes": 8,
      "facilitator_type": "self",
      "frequency": {
        "applies_when": [
          "lower_load_needed",
          "pain_or_fatigue",
          "time_conflict"
        ],
        "count": 0,
        "preferred_time_windows": [
          "07:00-07:30",
          "19:00-19:30"
        ],
        "type": "constraint_scoped"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_sleep_recovery_weekly",
          "goal_id": "goal_sleep_recovery",
          "notes": "Lower-load substitution for poor sleep/fatigue; does not count as core action.",
          "role": "recovery",
          "unit": "activity",
          "value": 0
        }
      ],
      "goal_tags": [
        "load_adjustment",
        "poor_sleep",
        "recovery"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion"
      ],
      "prep_required": false,
      "priority": 273,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [
        "eq_bodyweight"
      ],
      "required_provider_ids": [],
      "same_day_repeat_allowed": true,
      "share_with_provider_types": [],
      "skip_adjustment": {
        "allowed": true,
        "reason": "If member is traveling, use travel-compatible variant."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_primary",
      "substitution_notes": "Preserves recovery intent when higher-load activity is not appropriate.",
      "substitution_reason_codes": [
        "lower_load_needed",
        "pain_or_fatigue",
        "time_conflict"
      ],
      "title": "Short mobility or breathwork session after poor sleep"
    },
    {
      "activity_family_id": "b05_clinical_lab_draw_due_week",
      "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "clinic"
      ],
      "care_context_required": [
        "recent medication/supplement list",
        "last meal time",
        "fasting start time",
        "current metabolic goal"
      ],
      "dependencies": [
        {
          "must_happen": "before",
          "notes": "Member must fast for at least 8 hours before the lab draw.",
          "offset_minutes_min": 480,
          "type": "fasting"
        },
        {
          "blocked_activity_types": [
            "food"
          ],
          "blocked_goal_tags": [
            "breakfast",
            "structured_meal"
          ],
          "blocked_meal_slots": [
            "breakfast"
          ],
          "calendar_skip_reason_required": true,
          "must_happen": "before",
          "notes": "Do not schedule breakfast or any caloric food activity before the fasting lab draw on the same day.",
          "scope": "same_calendar_day_before_lab_draw",
          "skip_reason_code": "fasting_lab_same_morning",
          "type": "same_day_meal_exclusion"
        }
      ],
      "details": "Fasting blood panel for metabolic markers at the Elyx Partner Clinic. Requires at least 8 hours fasting. Do not schedule breakfast, caloric beverages, caloric supplements, or any caloric meal before the lab draw on the same day.",
      "duration_minutes": 30,
      "facilitator_type": "phlebotomist",
      "fasting_hours_required": 8,
      "fasting_metadata": {
        "allowed_during_fast": [
          "water",
          "non-caloric prescribed medication only if approved by clinician"
        ],
        "confirmation_fields": [
          "last_meal_time",
          "fasting_start_time",
          "fasting_confirmed"
        ],
        "fasting_hours_required": 8,
        "fasting_required": true,
        "fasting_window_minutes_min": 480,
        "not_allowed_before_lab_same_day": [
          "breakfast",
          "caloric beverages",
          "caloric supplements",
          "caloric meals"
        ],
        "same_day_meal_rule": {
          "calendar_skip_reason_required": true,
          "no_caloric_food_before_lab": true,
          "skip_meal_slots_before_lab": [
            "breakfast"
          ],
          "skip_reason_code": "fasting_lab_same_morning",
          "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
        }
      },
      "fasting_required": true,
      "frequency": {
        "preferred_time_windows": [
          "07:30-10:00"
        ],
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Lab draw is required for clinical review and counts toward the 3-month review target.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "lab",
        "metabolic_review"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "fasting_confirmed",
        "last_meal_time",
        "lab_panel_collected"
      ],
      "prep_metadata": {
        "calendar_skip_reason_required_for_blocked_breakfast": true,
        "due_before_minutes": 720,
        "fasting_hours_required": 8,
        "fasting_required": true,
        "missing_data_policy": "reschedule_lab_draw_until_fasting_confirmed",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "fasting_lab_prep",
        "required_inputs": [
          "recent medication/supplement list",
          "last meal time",
          "fasting start time",
          "current metabolic goal"
        ],
        "requires_no_caloric_meal_before_activity": true,
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": true,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_lab_kits"
      ],
      "required_provider_ids": [
        "provider_lab_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_lab_draw_due_week_sub_travel"
      ],
      "title": "Lab draw for metabolic review (clinic, due week)"
    },
    {
      "activity_family_id": "b05_clinical_lab_draw_due_week",
      "activity_id": "act_b05_clinical_lab_draw_due_week_sub_travel",
      "activity_type": "consultation",
      "allowed_locations": [
        "clinic"
      ],
      "care_context_required": [
        "recent medication/supplement list",
        "last meal time",
        "fasting start time",
        "current metabolic goal"
      ],
      "dependencies": [
        {
          "must_happen": "before",
          "notes": "Member must fast for at least 8 hours before the lab draw.",
          "offset_minutes_min": 480,
          "type": "fasting"
        },
        {
          "blocked_activity_types": [
            "food"
          ],
          "blocked_goal_tags": [
            "breakfast",
            "structured_meal"
          ],
          "blocked_meal_slots": [
            "breakfast"
          ],
          "calendar_skip_reason_required": true,
          "must_happen": "before",
          "notes": "Do not schedule breakfast or any caloric food activity before the fasting lab draw on the same day.",
          "scope": "same_calendar_day_before_lab_draw",
          "skip_reason_code": "fasting_lab_same_morning",
          "type": "same_day_meal_exclusion"
        }
      ],
      "details": "Lab draw rescheduled to the nearest valid morning window before or after travel. Requires at least 8 hours fasting. Do not schedule breakfast, caloric beverages, caloric supplements, or any caloric meal before the lab draw on the same day.",
      "duration_minutes": 30,
      "facilitator_type": "phlebotomist",
      "fasting_hours_required": 8,
      "fasting_metadata": {
        "allowed_during_fast": [
          "water",
          "non-caloric prescribed medication only if approved by clinician"
        ],
        "confirmation_fields": [
          "last_meal_time",
          "fasting_start_time",
          "fasting_confirmed"
        ],
        "fasting_hours_required": 8,
        "fasting_required": true,
        "fasting_window_minutes_min": 480,
        "not_allowed_before_lab_same_day": [
          "breakfast",
          "caloric beverages",
          "caloric supplements",
          "caloric meals"
        ],
        "same_day_meal_rule": {
          "calendar_skip_reason_required": true,
          "no_caloric_food_before_lab": true,
          "skip_meal_slots_before_lab": [
            "breakfast"
          ],
          "skip_reason_code": "fasting_lab_same_morning",
          "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting."
        }
      },
      "fasting_required": true,
      "frequency": {
        "preferred_time_windows": [
          "07:30-10:00"
        ],
        "type": "once",
        "window_days": 14
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Lab draw rescheduled before or after travel to preserve clinical review continuity.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "lab",
        "travel_adaptation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "fasting_confirmed",
        "last_meal_time",
        "lab_panel_collected"
      ],
      "prep_metadata": {
        "calendar_skip_reason_required_for_blocked_breakfast": true,
        "due_before_minutes": 720,
        "fasting_hours_required": 8,
        "fasting_required": true,
        "missing_data_policy": "reschedule_lab_draw_until_fasting_confirmed",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "fasting_lab_prep",
        "required_inputs": [
          "recent medication/supplement list",
          "last meal time",
          "fasting start time",
          "current metabolic goal"
        ],
        "requires_no_caloric_meal_before_activity": true,
        "skip_reason_code": "fasting_lab_same_morning"
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": true,
      "remote_allowed": false,
      "required_equipment_ids": [
        "eq_lab_kits"
      ],
      "required_provider_ids": [
        "provider_lab_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_lab_draw_due_week_primary",
      "substitution_notes": "Preserves lab measurement intent by rescheduling outside travel or clinic unavailability.",
      "substitution_reason_codes": [
        "travel_window",
        "facility_unavailable",
        "time_conflict"
      ],
      "title": "Lab draw rescheduled (pre/post travel)"
    },
    {
      "activity_family_id": "b05_clinical_physician_review_due_week",
      "activity_id": "act_b05_clinical_physician_review_due_week_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "clinic"
      ],
      "care_context_required": [
        "recent lab results",
        "current medication/supplement list",
        "metabolic goal summary",
        "recent symptoms or adverse events"
      ],
      "dependencies": [
        {
          "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "must_happen": "before",
          "notes": "Physician review must occur after lab results are available.",
          "offset_minutes_min": 60,
          "type": "prerequisite_activity"
        },
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent lab results",
            "current medication/supplement list",
            "metabolic goal summary",
            "recent symptoms or adverse events"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "In-person physician review at the clinic after labs are completed. Focus on metabolic markers and protocol updates.",
      "duration_minutes": 30,
      "facilitator_type": "physician",
      "frequency": {
        "preferred_time_windows": [
          "09:00-11:00",
          "19:00-20:00"
        ],
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Physician review after labs counts toward the 3-month clinical review target.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "physician_review",
        "lab_followup"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "next_actions"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent lab results",
          "current medication/supplement list",
          "metabolic goal summary",
          "recent symptoms or adverse events"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": true,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physician_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_physician_review_due_week_sub_remote"
      ],
      "title": "Physician review after labs (clinic, due week)"
    },
    {
      "activity_family_id": "b05_clinical_physician_review_due_week",
      "activity_id": "act_b05_clinical_physician_review_due_week_sub_remote",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent lab results",
        "current medication/supplement list",
        "metabolic goal summary",
        "recent symptoms or adverse events"
      ],
      "dependencies": [
        {
          "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "must_happen": "before",
          "notes": "Remote review must occur after lab results are available.",
          "offset_minutes_min": 60,
          "type": "prerequisite_activity"
        },
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent lab results",
            "current medication/supplement list",
            "metabolic goal summary",
            "recent symptoms or adverse events"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote video or phone review with physician after labs, used when travel or provider unavailability prevents in-person review.",
      "duration_minutes": 25,
      "facilitator_type": "physician",
      "frequency": {
        "preferred_time_windows": [
          "09:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Remote physician review preserves the clinical review target when in-person is not possible.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "physician_review",
        "remote_adaptation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "next_actions"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent lab results",
          "current medication/supplement list",
          "metabolic goal summary",
          "recent symptoms or adverse events"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": true,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physician_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_physician_review_due_week_primary",
      "substitution_notes": "Preserves physician review intent when in-person is not feasible due to travel or provider constraints.",
      "substitution_reason_codes": [
        "travel_window",
        "provider_unavailable",
        "remote_delivery_needed"
      ],
      "title": "Remote physician review after labs"
    },
    {
      "activity_family_id": "b05_clinical_dietitian_review_monthly",
      "activity_id": "act_b05_clinical_dietitian_review_monthly_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "home"
      ],
      "care_context_required": [
        "recent meal logs",
        "travel meal summary",
        "current nutrition goal",
        "current supplement list",
        "recent CGM or fasting glucose notes if available"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent meal logs",
            "travel meal summary",
            "current nutrition goal",
            "current supplement list",
            "recent CGM or fasting glucose notes if available"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Monthly review with dietitian to adapt nutrition plan, review meal adherence, and address travel or restaurant meal strategies.",
      "duration_minutes": 25,
      "facilitator_type": "dietitian",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday"
        ],
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "preferred_week": "second",
        "preferred_weeks": [
          "second",
          "first",
          "second"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Monthly dietitian review counts toward the 3-month clinical review target.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "dietitian_review",
        "nutrition_review"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "nutrition_adherence"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent meal logs",
          "travel meal summary",
          "current nutrition goal",
          "current supplement list",
          "recent CGM or fasting glucose notes if available"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_dietitian_review_monthly_sub_remote"
      ],
      "title": "Monthly dietitian review (home or remote)"
    },
    {
      "activity_family_id": "b05_clinical_dietitian_review_monthly",
      "activity_id": "act_b05_clinical_dietitian_review_monthly_sub_remote",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "recent meal logs",
        "travel meal summary",
        "current nutrition goal",
        "current supplement list",
        "recent CGM or fasting glucose notes if available"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent meal logs",
            "travel meal summary",
            "current nutrition goal",
            "current supplement list",
            "recent CGM or fasting glucose notes if available"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote video or phone review with dietitian, used when travel or provider unavailability prevents in-person review.",
      "duration_minutes": 20,
      "facilitator_type": "dietitian",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday"
        ],
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "preferred_week": "second",
        "preferred_weeks": [
          "second",
          "first",
          "second"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Remote dietitian review preserves the clinical review target when in-person is not possible.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "dietitian_review",
        "remote_adaptation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "nutrition_adherence"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent meal logs",
          "travel meal summary",
          "current nutrition goal",
          "current supplement list",
          "recent CGM or fasting glucose notes if available"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_dietitian_review_monthly_primary",
      "substitution_notes": "Preserves dietitian review intent when in-person is not feasible due to travel or provider constraints.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "remote_delivery_needed"
      ],
      "title": "Remote dietitian review (travel or provider unavailable)"
    },
    {
      "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
      "activity_id": "act_b05_clinical_physio_reassessment_post_travel_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent pain log",
        "travel summary",
        "current mobility goal",
        "recent training load notes"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain log",
            "travel summary",
            "current mobility goal",
            "recent training load notes"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote physio assessment to review mobility, pain, and post-travel adaptation. Used after travel.",
      "duration_minutes": 25,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "preferred_time_windows": [
          "16:00-18:00",
          "19:00-20:00"
        ],
        "target_date": "2026-06-26",
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Physio reassessment after travel counts toward the 3-month review target.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "physio_review",
        "post_travel"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "mobility_score",
        "pain_level"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain log",
          "travel summary",
          "current mobility goal",
          "recent training load notes"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_physio_reassessment_post_travel_sub_inperson"
      ],
      "title": "Physio reassessment after travel (remote)"
    },
    {
      "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
      "activity_id": "act_b05_clinical_physio_reassessment_post_travel_sub_inperson",
      "activity_type": "consultation",
      "allowed_locations": [
        "home",
        "gym"
      ],
      "care_context_required": [
        "recent pain log",
        "travel summary",
        "current mobility goal",
        "recent training load notes"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain log",
            "travel summary",
            "current mobility goal",
            "recent training load notes"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "In-person physio assessment at home or gym, used when remote review is not possible after travel.",
      "duration_minutes": 30,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "preferred_time_windows": [
          "16:00-18:00",
          "18:45-20:00",
          "19:00-20:00"
        ],
        "target_date": "2026-06-26",
        "type": "once",
        "window_days": 7
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_strength_and_mobility",
          "notes": "In-person physio review preserves the measurement intent when remote is not feasible.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "physio_review",
        "post_travel"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "mobility_score",
        "pain_level"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain log",
          "travel summary",
          "current mobility goal",
          "recent training load notes"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": false,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_physio_reassessment_post_travel_primary",
      "substitution_notes": "Preserves physio review intent by enabling in-person assessment when remote is not feasible.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "remote_delivery_needed"
      ],
      "title": "In-person physio reassessment (post-travel/pain)"
    },
    {
      "activity_family_id": "b05_clinical_lab_reschedule_coordination",
      "activity_id": "act_b05_clinical_lab_reschedule_coordination_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "lab due date",
        "travel window summary",
        "clinic availability",
        "fasting feasibility window"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "lab due date",
            "travel window summary",
            "clinic availability",
            "fasting feasibility window"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote care-team coordination to reschedule lab draws when travel or facility unavailability occurs. Member is notified of new lab date.",
      "duration_minutes": 15,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "09:00-17:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Care-team lab reschedule coordination is support-only and does not count toward the review target.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "lab_reschedule",
        "care_team"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "lab_reschedule_confirmed"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "lab due date",
          "travel window summary",
          "clinic availability",
          "fasting feasibility window"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_lab_reschedule_coordination_facility_change_sub"
      ],
      "title": "Care-team lab reschedule coordination (remote)"
    },
    {
      "activity_family_id": "b05_clinical_lab_reschedule_coordination",
      "activity_id": "act_b05_clinical_lab_reschedule_coordination_facility_change_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "lab due date",
        "travel window summary",
        "clinic availability",
        "fasting feasibility window"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "lab due date",
            "travel window summary",
            "clinic availability",
            "fasting feasibility window"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Care team coordinates an alternate lab booking when the preferred lab or due-week window becomes unavailable.",
      "duration_minutes": 15,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "09:00-17:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "lab_reschedule",
        "care_team"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_002",
        "phase_marcus_004",
        "phase_marcus_006"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "lab_reschedule_confirmed"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "lab due date",
          "travel window summary",
          "clinic availability",
          "fasting feasibility window"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_lab_reschedule_coordination_primary",
      "substitution_notes": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
      "substitution_reason_codes": [
        "facility_unavailable",
        "time_conflict"
      ],
      "title": "Alternate lab booking coordination"
    },
    {
      "activity_family_id": "b05_clinical_biometric_review_support",
      "activity_id": "act_b05_clinical_biometric_review_support_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent biometric data",
        "goal progress summary",
        "sleep summary",
        "activity summary",
        "CGM data if available"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent biometric data",
            "goal progress summary",
            "sleep summary",
            "activity summary",
            "CGM data if available"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Physician-led review of biometric data (weight, sleep, activity, CGM if available) with summary sent to member and providers.",
      "duration_minutes": 20,
      "facilitator_type": "physician",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "thursday"
        ],
        "preferred_time_windows": [
          "09:00-11:00",
          "19:00-20:00"
        ],
        "preferred_week": "third",
        "preferred_weeks": [
          "third",
          "fourth",
          "third"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Biometric review summary is support-only and does not count toward the review target.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "biometric_review",
        "care_team"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "biometric_summary_sent"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent biometric data",
          "goal progress summary",
          "sleep summary",
          "activity summary",
          "CGM data if available"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physician_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_biometric_review_support_async_summary_sub"
      ],
      "title": "Physician biometric review and care-plan summary (remote)"
    },
    {
      "activity_family_id": "b05_clinical_biometric_review_support",
      "activity_id": "act_b05_clinical_biometric_review_support_async_summary_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent biometric data",
        "goal progress summary",
        "sleep summary",
        "activity summary",
        "CGM data if available"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent biometric data",
            "goal progress summary",
            "sleep summary",
            "activity summary",
            "CGM data if available"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Physician reviews CGM, sleep, and session notes asynchronously and summarizes flags for physician or dietitian follow-up.",
      "duration_minutes": 15,
      "facilitator_type": "physician",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "thursday"
        ],
        "preferred_time_windows": [
          "09:00-11:00",
          "19:00-20:00"
        ],
        "preferred_week": "third",
        "preferred_weeks": [
          "third",
          "fourth",
          "third"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Preserves biometric review support when a live care-team review is not realistic.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "biometric_review",
        "care_team"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "biometric_summary_sent"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent biometric data",
          "goal progress summary",
          "sleep summary",
          "activity summary",
          "CGM data if available"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_physician_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_biometric_review_support_primary",
      "substitution_notes": "Preserves biometric review support when a live care-team review is not realistic.",
      "substitution_reason_codes": [
        "remote_delivery_needed",
        "time_conflict"
      ],
      "title": "Async physician biometric summary review"
    },
    {
      "activity_family_id": "b05_clinical_trainer_physio_handoff",
      "activity_id": "act_b05_clinical_trainer_physio_handoff_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent pain log",
        "mobility status",
        "training plan update",
        "recent strength progression log"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain log",
            "mobility status",
            "training plan update",
            "recent strength progression log"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote care-team handoff between trainer and physiotherapist after travel or when clinically indicated, to coordinate safe return to training.",
      "duration_minutes": 20,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Trainer-physio handoff is support-only and does not count toward the review target.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "trainer_physio_handoff",
        "pain_escalation"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "handoff_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain log",
          "mobility status",
          "training plan update",
          "recent strength progression log"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_trainer_physio_handoff_async_handoff_sub"
      ],
      "title": "Trainer-physio care-team handoff after travel (remote)"
    },
    {
      "activity_family_id": "b05_clinical_trainer_physio_handoff",
      "activity_id": "act_b05_clinical_trainer_physio_handoff_async_handoff_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent pain log",
        "mobility status",
        "training plan update",
        "recent strength progression log"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent pain log",
            "mobility status",
            "training plan update",
            "recent strength progression log"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Trainer and physio exchange knee-pain and load notes asynchronously before the next strength progression.",
      "duration_minutes": 10,
      "facilitator_type": "physiotherapist",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_strength_and_mobility",
          "notes": "Preserves trainer-physio coordination when both providers cannot meet live.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "trainer_physio_handoff",
        "pain_escalation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "handoff_notes"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent pain log",
          "mobility status",
          "training plan update",
          "recent strength progression log"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_trainer_physio_handoff_primary",
      "substitution_notes": "Preserves trainer-physio coordination when both providers cannot meet live.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "time_conflict"
      ],
      "title": "Async trainer physio handoff"
    },
    {
      "activity_family_id": "b05_clinical_adherence_checkin_support",
      "activity_id": "act_b05_clinical_adherence_checkin_support_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent adherence log",
        "protocol checklist",
        "missed-session reasons",
        "meal/supplement completion notes"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent adherence log",
            "protocol checklist",
            "missed-session reasons",
            "meal/supplement completion notes"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote check-in to review adherence to meal, training, and supplement protocols. Provides support and flags for care-team follow-up if needed.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "09:00-10:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Weekly adherence check-in is support-only and does not count toward the review target.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "adherence_check",
        "remote_coach"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "adherence_score",
        "flagged_issues"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent adherence log",
          "protocol checklist",
          "missed-session reasons",
          "meal/supplement completion notes"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_adherence_checkin_support_message_check_sub"
      ],
      "title": "Weekly adherence check-in with remote coach"
    },
    {
      "activity_family_id": "b05_clinical_adherence_checkin_support",
      "activity_id": "act_b05_clinical_adherence_checkin_support_message_check_sub",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent adherence log",
        "protocol checklist",
        "missed-session reasons",
        "meal/supplement completion notes"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent adherence log",
            "protocol checklist",
            "missed-session reasons",
            "meal/supplement completion notes"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Brief message-based adherence check-in to resolve barriers after missed sessions, travel disruption, or meal-prep gaps.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "09:00-10:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "weekly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": false,
          "goal_action_id": "ga_adherence_support_weekly",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
          "role": "support",
          "unit": "activity",
          "value": 0
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "support",
        "adherence_check",
        "remote_coach"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_001",
        "phase_marcus_003",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "adherence_score",
        "flagged_issues"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent adherence log",
          "protocol checklist",
          "missed-session reasons",
          "meal/supplement completion notes"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer"
      ],
      "skip_adjustment": {
        "allowed_after_poor_sleep": true,
        "allowed_after_travel": true,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing."
      },
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_adherence_checkin_support_primary",
      "substitution_notes": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
      "substitution_reason_codes": [
        "travel_window",
        "time_conflict"
      ],
      "title": "Message-based adherence check-in"
    },
    {
      "activity_family_id": "b05_clinical_dietitian_lab_followup",
      "activity_id": "act_b05_clinical_dietitian_lab_followup_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent lab or CGM results",
        "nutrition adherence summary",
        "current supplement list",
        "recent meal logs"
      ],
      "dependencies": [
        {
          "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "must_happen": "before",
          "notes": "Dietitian follow-up must occur after lab or CGM results are available.",
          "offset_minutes_min": 60,
          "type": "prerequisite_activity"
        },
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent lab or CGM results",
            "nutrition adherence summary",
            "current supplement list",
            "recent meal logs"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote dietitian follow-up after lab or CGM review to adjust nutrition plan and address metabolic markers.",
      "duration_minutes": 20,
      "facilitator_type": "dietitian",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday"
        ],
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "preferred_week": "fourth",
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Dietitian lab follow-up counts toward the 3-month clinical review package.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "dietitian_lab_followup",
        "nutrition_review"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "nutrition_plan_update"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent lab or CGM results",
          "nutrition adherence summary",
          "current supplement list",
          "recent meal logs"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_dietitian_lab_followup_sub_timeconflict"
      ],
      "title": "Dietitian follow-up after lab or CGM review (remote)"
    },
    {
      "activity_family_id": "b05_clinical_dietitian_lab_followup",
      "activity_id": "act_b05_clinical_dietitian_lab_followup_sub_timeconflict",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote"
      ],
      "care_context_required": [
        "recent lab or CGM results",
        "nutrition adherence summary",
        "current supplement list",
        "recent meal logs"
      ],
      "dependencies": [
        {
          "activity_id": "act_b05_clinical_lab_draw_due_week_primary",
          "must_happen": "before",
          "notes": "Dietitian follow-up must occur after lab or CGM results are available.",
          "offset_minutes_min": 60,
          "type": "prerequisite_activity"
        },
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent lab or CGM results",
            "nutrition adherence summary",
            "current supplement list",
            "recent meal logs"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote dietitian follow-up is rescheduled to a later window due to provider or member time conflict.",
      "duration_minutes": 15,
      "facilitator_type": "dietitian",
      "frequency": {
        "count": 1,
        "preferred_days": [
          "tuesday"
        ],
        "preferred_time_windows": [
          "18:00-19:00",
          "19:00-20:00"
        ],
        "preferred_week": "fourth",
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Remote dietitian follow-up is rescheduled to a feasible time when provider or member is unavailable.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "dietitian_lab_followup",
        "remote_adaptation"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_003",
        "phase_marcus_005"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "provider_notes",
        "nutrition_plan_update"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent lab or CGM results",
          "nutrition adherence summary",
          "current supplement list",
          "recent meal logs"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_dietitian_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_dietitian_lab_followup_primary",
      "substitution_notes": "Preserves dietitian lab follow-up intent by rescheduling to a feasible remote window.",
      "substitution_reason_codes": [
        "provider_unavailable",
        "remote_delivery_needed",
        "time_conflict"
      ],
      "title": "Dietitian follow-up rescheduled (remote, time conflict)"
    },
    {
      "activity_family_id": "b05_clinical_remote_care_team_handoff",
      "activity_id": "act_b05_clinical_remote_care_team_handoff_primary",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "recent travel summary",
        "plan adaptation notes",
        "missed or substituted activity log",
        "current medication/supplement list"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent travel summary",
            "plan adaptation notes",
            "missed or substituted activity log",
            "current medication/supplement list"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Remote care-team handoff to coordinate plan changes during travel or remote delivery. Ensures continuity of clinical review and adaptation.",
      "duration_minutes": 15,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "10:00-11:00",
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Care-team handoff during travel or remote delivery supports clinical review continuity.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "care_team_handoff",
        "travel_continuity"
      ],
      "is_primary": true,
      "journey_phase_applicability": [
        "phase_marcus_004",
        "phase_marcus_006",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "handoff_notes",
        "plan_update"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent travel summary",
          "plan adaptation notes",
          "missed or substituted activity log",
          "current medication/supplement list"
        ]
      },
      "prep_required": true,
      "priority": 125,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [
        "act_b05_clinical_remote_care_team_handoff_sub_provider_unavailable"
      ],
      "title": "Remote care-team handoff during travel or remote delivery"
    },
    {
      "activity_family_id": "b05_clinical_remote_care_team_handoff",
      "activity_id": "act_b05_clinical_remote_care_team_handoff_sub_provider_unavailable",
      "activity_type": "consultation",
      "allowed_locations": [
        "remote",
        "travel_hotel"
      ],
      "care_context_required": [
        "recent travel summary",
        "plan adaptation notes",
        "missed or substituted activity log",
        "current medication/supplement list"
      ],
      "dependencies": [
        {
          "must_exist": true,
          "notes": "Required notes/labs/logs must be available before this review can be scheduled.",
          "required_inputs": [
            "recent travel summary",
            "plan adaptation notes",
            "missed or substituted activity log",
            "current medication/supplement list"
          ],
          "type": "required_context_available"
        }
      ],
      "details": "Care-team handoff is completed asynchronously (e.g., via secure message or app) when provider is unavailable for live remote handoff.",
      "duration_minutes": 10,
      "facilitator_type": "remote_coach_pool",
      "frequency": {
        "count": 1,
        "preferred_time_windows": [
          "18:00-19:00",
          "19:00-20:00"
        ],
        "type": "monthly"
      },
      "goal_contributions": [
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_clinical_review_3month",
          "goal_id": "goal_adherence_and_careteam",
          "notes": "Care-team handoff is rescheduled or delivered asynchronously when provider is unavailable.",
          "role": "measurement",
          "unit": "activity",
          "value": 1
        },
        {
          "counts_toward_weekly_target": true,
          "goal_action_id": "ga_care_team_followthrough_3month",
          "value": 1
        }
      ],
      "goal_tags": [
        "measurement",
        "care_team_handoff",
        "travel_continuity"
      ],
      "is_primary": false,
      "journey_phase_applicability": [
        "phase_marcus_004",
        "phase_marcus_006",
        "phase_marcus_007"
      ],
      "load_level": "low",
      "metrics_to_collect": [
        "completion",
        "handoff_notes",
        "plan_update"
      ],
      "prep_metadata": {
        "due_before_minutes": 1440,
        "missing_data_policy": "reschedule_or_convert_to_async_review",
        "owner": "care_team_or_activity_facilitator",
        "prep_required": true,
        "prep_type": "clinical_context_review",
        "required_inputs": [
          "recent travel summary",
          "plan adaptation notes",
          "missed or substituted activity log",
          "current medication/supplement list"
        ]
      },
      "prep_required": true,
      "priority": 126,
      "raw_clinical_data_required": false,
      "remote_allowed": true,
      "required_equipment_ids": [],
      "required_provider_ids": [
        "provider_remote_coach_01"
      ],
      "same_day_repeat_allowed": false,
      "share_with_provider_types": [
        "physician",
        "dietitian",
        "trainer",
        "physiotherapist"
      ],
      "skip_adjustment": false,
      "substitution_activity_ids": [],
      "substitution_for_activity_id": "act_b05_clinical_remote_care_team_handoff_primary",
      "substitution_notes": "Preserves care-team handoff intent by enabling asynchronous delivery when provider is unavailable.",
      "substitution_reason_codes": [
        "travel_window",
        "provider_unavailable",
        "remote_delivery_needed"
      ],
      "title": "Asynchronous care-team handoff (provider unavailable)"
    }
  ]
}
```
