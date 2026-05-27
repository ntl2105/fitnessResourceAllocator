# Scheduler Variety, Consultations, and Goal Taxonomy Design

## Problem

The generated activity board has reasonable variety, but the produced calendar is
too repetitive. Chef-prepped meals dominate normal weeks, substitutions are used
only after a primary fails, and consultation volume is too low for a high-touch
Elyx member. The `ga_travel_continuity_3month` goal also overlaps with meals,
fitness, recovery, and consultations, so it should not remain a standalone goal.

## Goals

- Make meal schedules varied while preserving structured-meal goal accounting.
- Schedule restaurant and member-prepped meal substitutions intentionally, not
  only after hard failure.
- Schedule enough consultations to reflect Elyx's high-touch care model.
- Replace the overlapping travel-continuity goal with two distinct goal actions:
  care-team decision follow-through and behavior-change coaching.
- Keep travel as a context, phase, dependency, or substitution reason inside the
  underlying care domains.
- Preserve auditability through `decision_traces.json`, `personalized_plan.json`,
  and the generated reviewer documentation.

## Non-Goals

- Do not regenerate the entire activity board from scratch.
- Do not make travel its own Stage 05 batch again.
- Do not count passive logs, reminders, or supplement adherence as clinical or
  behavior-change progress unless the activity is explicitly designed as a
  member-facing coaching or decision follow-up.

## Goal Taxonomy

Remove:

- `ga_travel_continuity_3month`: `Maintain travel continuity adaptations`

Add:

- `ga_care_team_followthrough_3month`: `Complete care-team review and decision follow-through`
  - Period: `3_month`
  - Target: 6 touchpoints
  - Counts: physician review, dietitian review, physio reassessment, remote care-team handoff,
    plan-adjustment review, lab-result follow-up
  - Does not count: passive logs, supplement protocol, generic reminders

- `ga_behavior_coaching_weekly`: `Complete behavior coaching and friction-resolution touchpoints`
  - Period: `weekly`
  - Target: 1 touchpoint
  - Counts: remote coach check-in, adherence barrier review, travel friction planning,
    post-missed-session coaching, meal-prep failure resolution
  - Does not count: daily supplement-taking itself, ordinary meals, ordinary training sessions

Existing goal actions remain:

- structured metabolic meals
- aerobic conditioning
- knee-modified strength sessions
- sleep and fatigue recovery actions
- preventive lab or provider review
- support adherence or supplement protocol

## Meal Variety Policy

Meals should satisfy structured nutrition targets without looking artificially
uniform. The scheduler should still attempt the family primary first, but it may
choose same-family substitutions for planned variety when the substitution counts
toward the same family target.

Minimum behavior:

- Chef-prepped meals should not exceed a configured weekly cap.
- At least one restaurant dinner or restaurant meal should appear in ordinary
  non-travel weeks when a suitable substitution exists.
- At least one member-assembled or low-prep meal should appear in ordinary
  non-travel weeks when a suitable substitution exists.
- Travel meals should count as structured meals when they preserve the structured
  nutrition intent. They should not be routed through a separate travel goal.
- Days should not miss meals merely because the primary home/office meal failed
  while an appropriate same-family substitution exists.

## Consultation Policy

Consultations should be scheduled as first-class member activities where they
represent care-team interaction, coaching, or clinical decision follow-through.

Minimum behavior:

- Schedule at least one care-team or coaching consultation in most weeks.
- Schedule at least six care-team follow-through touchpoints across the
  three-month horizon if candidate activities exist.
- Clinical due-week items should have higher scheduling priority than low-value
  recurring support tasks.
- Remote consultation substitutions should be preferred when in-person provider,
  clinic, lab, or member availability blocks the primary.
- Support-only care-team activities should not all be skipped. Activities tied to
  the behavior-coaching goal or care-team follow-through goal are member-facing
  and should be scheduled.

## Availability Model

Chef availability should represent prep capacity, not chef presence during eating.
Meal activities should retain `prep_source`, `food_provider_id`, and source
metadata, but should not require the chef as a provider during the meal slot.

Availability should include realistic prep scarcity:

- Keep chef prep available only on selected prep windows.
- Add explicit chef-unavailable or prep-unavailable context to selected days so
  the scheduler has a reason to select restaurant or member-prepped alternatives.
- Availability should not force every normal home meal to be chef-prepped.

## Scheduler Changes

Add family-level or activity-level variety controls consumed by the scheduler:

- `variety_role`: `primary_default`, `planned_variety`, `fallback_only`
- `weekly_variety_min`: optional integer for planned variety activities
- `weekly_primary_cap`: optional integer for primary-default activity families

The scheduler should:

- group primary and substitutions by family occurrence as it does today
- try the primary first for ordinary placement
- allow a planned-variety substitution to be selected before the primary when the
  family already met its primary cap or the substitution is needed to satisfy the
  weekly variety minimum
- include the policy reason in the trace, for example:
  `Substitution used for planned variety after chef-prepped meal cap was met.`

## Validation And Tests

Validation should continue to require:

- at least 100 scheduler-facing activities
- exactly 50 families
- all references resolve
- goal action references resolve
- substitutions preserve family-level counted targets

New tests should verify:

- the removed travel-continuity goal no longer appears in active data
- the two replacement goal actions exist
- scheduled calendar output includes consultation rows above a minimum threshold
- scheduled food output includes chef-prepped, restaurant, and member-prepped or
  low-prep meals
- goal reports include the replacement weekly and three-month categories

## Expected Reviewer Outcome

The final schedule should look like a believable high-end Elyx plan: structured
but not monotonous, clinically supervised, and adaptive when the member travels
or when normal resources are unavailable. The audit artifacts should show both
met and unmet goals clearly.
