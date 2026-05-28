# Elyx Resource Allocator Scheduler Logic

This scheduler is designed for the updated Elyx synthetic dataset:

- `activity_families.updated.json`
- `availability.updated.json`

The goal is not merely to place activities into empty time slots. The scheduler must make auditable decisions: why an activity was scheduled, substituted, skipped, rejected, or deferred.

---

## 1. Scheduler outputs

The scheduler should output four inspection artifacts every run:

1. `calendar_rows.json`
   - The final scheduled, skipped, substituted, or deferred rows shown in the app.
2. `rejection_log.json`
   - Every candidate that was considered but rejected, with reason codes.
3. `weekly_goal_summary.json`
   - Weekly counts for aerobic, strength, recovery, meals, and care-team follow-through.
4. `scheduler_trace.json`
   - Step-by-step trace from demand generation → candidate generation → validation → scoring → final placement.

A calendar row should include at minimum:

```json
{
  "calendar_row_id": "row_<activity_id>_<date>",
  "trace_id": "trace_<activity_id>_<date>",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "title": "Human-readable title",
  "activity_id": "...",
  "activity_family_id": "...",
  "activity_type": "food|fitness|therapy|consultation|medication",
  "location_id": "home|office|gym|clinic|lab|remote|travel_hotel",
  "mode": "in_person|remote|self_guided|skipped",
  "status": "scheduled|substituted|skipped|rejected|deferred",
  "substitution_status": "primary|substitution|support|skip_row",
  "goal_action_ids": ["..."],
  "goal_tags": ["..."],
  "load_level": "low|medium|high",
  "counts_toward_goal": true,
  "counting_goal_action_id": "...",
  "selected_reason_codes": ["..."],
  "rejection_reason_codes": [],
  "prep_required": false,
  "prep_status": "not_required|satisfied|auto_created|missing_deferred",
  "dependency_status": "none|required_satisfied|required_missing",
  "skip_reason_code": null,
  "skip_reason_text": null
}
```

---

## 2. Normalize source data

### 2.1 Activities

Flatten `activity_families` into a scheduler-facing activity table.

Each row should contain:

- family-level fields:
  - `activity_family_id`
  - `care_domain`
  - `intent`
  - `family_target`
  - `goal_action_ids`
  - `family_validation_notes`
- activity-level fields:
  - all fields from `primary_activity`
  - all fields from each `substitution_activities[]`
- derived fields:
  - `is_primary_activity`
  - `substitution_for_activity_id`
  - `counts_toward_goal_by_goal_action_id`
  - `is_support_only`
  - `is_core_target_activity`
  - `human_title`
  - `preferred_days`
  - `preferred_time_windows`
  - `duration_minutes`
  - `required_inputs`
  - `fasting_required`
  - `wfh_sensitive`

Important normalization rule:

> Do not schedule target-zero fallback families as independent weekly goals. They are candidate substitutions only unless another rule explicitly demands them.

This prevents the calendar from filling with support-only substitutions.

### 2.2 Availability

Normalize `availability_blocks` into resource calendars:

- `location_calendar[location_id]`
- `provider_calendar[provider_id]`
- `equipment_calendar[equipment_id]`
- `member_blocked_calendar`
- `member_location_overrides`
- `travel_windows`
- `scheduling_rules`

Important availability types:

- `member_location`: tells the scheduler the member is home/WFH or otherwise location-constrained.
- `member_travel` / `travel_window`: tells the scheduler to use `travel_hotel` and remote-compatible activities.
- `member_blocked`: blocks time or reduces allowable activity types.
- `scheduling_rule`: global rules such as no office-location activities on WFH days.

---

## 3. Scheduling phases

Run the scheduler in phases. Earlier phases create constraints for later phases.

### Phase 0 — Build planning horizon

Use:

```text
planning_start_date = 2026-06-01
planning_months = 3
planning_end_date = 2026-09-01
```

Generate:

- day records
- week records, Monday to Sunday
- month records
- travel-day flags
- WFH-day flags
- member-location-by-day

### Phase 1 — Generate clinical measurement obligations

Schedule clinical items first because they create dependencies.

Priority order:

1. Fasting lab draw.
2. Physician review after lab results.
3. Dietitian review / lab follow-up.
4. Physio reassessment after travel or pain events.
5. Care-team handoff / biometric summary / adherence check-ins.

For each clinical activity:

- Generate candidates from preferred windows.
- Validate provider, location, equipment, travel, WFH, dependencies, and prep.
- Schedule the highest-scoring candidate.
- If no valid candidate exists, attempt listed substitutions.
- If still impossible, create a deferred/rejected row with a clear reason code.

### Phase 2 — Apply fasting lab meal logic

After lab draw placement, enforce fasting constraints.

For every fasting lab row:

1. Confirm `fasting_required = true` or dependency type `fasting`.
2. Compute fasting window:

```text
fasting_start = lab_start - fasting_hours_required
fasting_end = lab_end
```

3. For the same calendar date:
   - reject any caloric breakfast scheduled before the lab draw.
   - reject caloric supplements before the lab draw unless explicitly non-caloric/clinician-approved.
   - create a skip row for breakfast if the breakfast target would otherwise generate a row.

Required skip row:

```json
{
  "activity_id": "act_b01_breakfast_skip_for_fasting_lab",
  "activity_type": "food",
  "status": "skipped",
  "substitution_status": "skip_row",
  "title": "Breakfast skipped for fasting lab",
  "skip_reason_code": "fasting_lab_same_morning",
  "skip_reason_text": "Breakfast skipped because metabolic lab draw requires 8 hours fasting.",
  "counts_toward_goal": false
}
```

Hard rule:

> A lab draw requiring 8 hours fasting is invalid if breakfast or another caloric intake is scheduled before it on the same day.

### Phase 3 — Generate structured meals

Generate food demands from core meal families:

- Breakfast target: 5/week.
- Lunch target: 5/week.
- Dinner target: 4/week.

Rules:

- Use human-readable titles only.
- Keep source/prep concepts in metadata:
  - `dining_source`
  - `prep_source`
  - `delivery_source`
  - `facilitator_type`
- Do not use ugly generated titles like “Member-assembled lunch” or “Structured restaurant dinner” in the UI.
- On fasting lab mornings, do not schedule breakfast before the lab. Use the explicit skipped breakfast row.
- On WFH days, do not schedule office meals. Substitute to home meal activities where available.
- During travel windows, use travel meal families if a meal row is needed.

### Phase 4 — Generate weekly fitness demands

Weekly fitness targets are:

```text
Aerobic sessions: 2/week
Strength sessions: 2/week
Recovery actions: 4/week
```

Use family targets to create these demands:

Aerobic core families:

- `b02_cardio_zone2_gym`: 1/week
- `b02_cardio_zone2_home`: 1/week

Strength core families:

- `b03_strength_trainer_gym`: 1/week
- `b03_strength_home_strength`: 1/week

Recovery core families:

- `b04_recovery_evening_mobility_home`: 2/week
- `b04_recovery_sleep_routine_support`: 2/week

Hard counting rules:

- Walking breaks never count toward strength.
- Office/home walking breaks are support-only unless an aerobic substitution explicitly says it counts toward `ga_aerobic_conditioning_weekly`.
- Do not allow a week to end with only walking-based fitness if strength/aerobic options were available.
- If a week has only walks because all real aerobic/strength options were blocked, create a weekly exception note:

```json
{
  "week_start": "YYYY-MM-DD",
  "exception_code": "fitness_walk_only_week",
  "reason": "All non-walking aerobic/strength options were blocked by travel, facility, provider, or member availability constraints.",
  "blocked_core_goal_action_ids": ["ga_aerobic_conditioning_weekly", "ga_strength_sessions_weekly"]
}
```

### Phase 5 — Schedule recovery around load

Recovery should be scheduled after load, travel, or poor sleep where possible.

Rules:

- Do not stack high-load strength and high-load recovery on the same evening.
- Prefer recovery after travel arrival fatigue blocks.
- Prefer evening recovery windows.
- Recovery actions count toward `ga_sleep_recovery_weekly` only if their `goal_contributions` explicitly count.
- Travel recovery variants do not inflate normal-week denominators unless their goal contribution explicitly counts.

### Phase 6 — Schedule support/check-in activities

Support activities are lower priority than core goals.

Examples:

- adherence check-in
- supplement protocol
- CGM log
- hydration protocol
- remote coach check-in
- biometric summary
- travel meal adherence review

Rules:

- Do not let support activities crowd out core fitness, meals, labs, or recovery.
- Support rows should not count toward core target goals unless explicitly marked as counting.
- If support activity requires prep/context, validate prep before scheduling.

---

## 4. Hard validators

Every candidate must pass these validators before scoring.

### 4.1 Member availability validator

Reject if candidate overlaps a `member_blocked` interval, except for explicitly allowed low-complexity tasks.

Allowed inside work blocks only when all are true:

- activity is low load;
- duration is short or meal-window appropriate;
- activity location matches current member location;
- activity does not require a provider who is unavailable;
- activity does not conflict with WFH/travel rules.

Recommended thresholds:

```text
low-complexity remote/check task: duration <= 15 minutes
meal during workday: only inside meal window, usually lunch
walking break: duration <= 10 minutes, office/home location must match member location
```

### 4.2 Location validator

Reject if selected location is not in `allowed_locations`.

Also reject if:

- member is traveling and the activity is not `travel_hotel` or `remote` compatible;
- member is WFH and the activity location is `office`;
- clinic/lab/gym/home activity is attempted during travel;
- office activity is attempted during travel or WFH.

### 4.3 WFH validator

On WFH days:

- office-location activities are invalid;
- office walking breaks should substitute to `act_b02_cardio_walking_office_remote_sub`;
- office lunch should substitute to `act_b01_lunch_member_assembled_home_primary` if available;
- office breakfast should substitute to `act_b01_breakfast_home_lowprep` if available;
- if no substitution exists, reject with:

```text
wfh_no_office_location_activity
```

### 4.4 Travel validator

During travel windows:

- current member location is `travel_hotel`.
- valid locations are generally `travel_hotel` or `remote`.
- home, office, clinic, lab, and gym activities are invalid unless the activity is explicitly remote-compatible and does not require in-person location resources.
- use travel-specific substitutions first, especially for meals, strength, aerobic, and recovery.

### 4.5 Provider validator

If `required_provider_ids` is non-empty:

- at least one required provider block must cover the candidate interval;
- provider location must match candidate location, unless `remote_supported = true` and the activity can be remote;
- if provider is unavailable, attempt a substitution with `provider_unavailable` reason.

### 4.6 Equipment validator

If `required_equipment_ids` is non-empty:

- required equipment must be available at the candidate location and time;
- portable/travel-compatible equipment can be used in travel windows if its availability says so;
- if unavailable, attempt a substitution with `equipment_unavailable` or `facility_unavailable`.

### 4.7 Dependency validator

For each dependency:

- `fasting`: enforce fasting window and no-caloric-intake rules.
- `prerequisite_activity`: required prior activity must be scheduled and completed/scheduled before this candidate by `offset_minutes_min`.

Example:

- Physician review after labs must occur after lab draw and after lab results are available.

### 4.8 Prep validator

If `prep_required = true` or `prep_metadata.prep_required = true`:

Check that required inputs exist before the activity.

If required inputs are missing:

- if `missing_data_policy = defer_review_until_recent_aerobic_session_data_exists`, defer the review until the required activity data exists.
- if `missing_data_policy = reschedule_lab_draw_until_fasting_confirmed`, reject/defer lab until fasting confirmation can be represented.
- if `missing_data_policy = reschedule_or_convert_to_async_review`, attempt async substitution if available; otherwise defer.

For prep-required activities, calendar rows should include:

```json
{
  "prep_required": true,
  "prep_type": "clinical_context_review",
  "prep_required_inputs": ["..."],
  "prep_due_before_minutes": 1440,
  "prep_status": "satisfied|auto_created|missing_deferred"
}
```

### 4.9 Same-day repeat validator

If `same_day_repeat_allowed = false`, do not schedule the same activity twice on the same date.

### 4.10 Goal counting validator

A row counts toward a goal only if `goal_contributions[].counts_toward_weekly_target = true` for that goal.

Do not infer counting from tags alone.

---

## 5. Substitution logic

Use substitutions as a controlled fallback chain, not as extra activities.

For each demand:

1. Try the family primary activity.
2. If invalid, inspect its `substitution_activity_ids`.
3. Try substitutions in the listed order.
4. If a substitution is selected:
   - preserve the original demand ID;
   - mark `substitution_status = "substitution"`;
   - include `substitution_for_activity_id`;
   - include `substitution_reason_codes`.
5. If all candidates fail:
   - create rejected/deferred row;
   - include all rejection reasons.

Never schedule a substitution simply because it exists.

---

## 6. Candidate scoring

Only valid candidates are scored.

Suggested scoring model:

```text
score = 0

+1000 if candidate fills an unmet core target
+500  if primary activity
+300  if valid substitution for blocked primary
+200  if preferred day matches
+150  if preferred time window matches
+150  if current location matches naturally without travel/WFH workaround
+100  if provider/equipment match exactly without remote workaround
+75   if activity preserves weekly spacing
+50   if prep is already satisfied

-100  if substitution is support-only
-150  if candidate is outside preferred day but still acceptable
-200  if candidate is late evening and not a recovery/sleep activity
-250  if candidate stacks medium/high load within 6 hours of another medium/high load
-300  if candidate uses walking fallback for aerobic when non-walking aerobic exists
-500  if candidate would exceed weekly cap
-1000 if candidate is support-only and core target is still unmet
```

Tie-breakers:

1. Earlier date within due window.
2. Primary over substitution.
3. In-person over remote for clinical/measurement if both valid.
4. Lower load after travel/fatigue.
5. Fewer downstream conflicts.

---

## 7. Weekly target reconciliation

At the end of each week, run a reconciliation pass.

For each week:

```json
{
  "week_start": "YYYY-MM-DD",
  "targets": {
    "ga_aerobic_conditioning_weekly": 2,
    "ga_strength_sessions_weekly": 2,
    "ga_sleep_recovery_weekly": 4
  },
  "actuals": {
    "ga_aerobic_conditioning_weekly": 0,
    "ga_strength_sessions_weekly": 0,
    "ga_sleep_recovery_weekly": 0
  },
  "gap_reason_codes": []
}
```

If target gaps exist:

1. Search for additional valid candidates in remaining free slots.
2. Prefer core activities over substitutions.
3. If still impossible, write a gap reason:
   - `provider_unavailable`
   - `facility_unavailable`
   - `travel_window`
   - `member_unavailable`
   - `fatigue_or_load_constraint`
   - `wfh_no_office_location_activity`
   - `dependency_missing`
   - `prep_missing`

---

## 8. Pseudocode

```ts
function runScheduler(activityFamilies, availability) {
  const activities = normalizeActivities(activityFamilies);
  const resources = normalizeAvailability(availability);
  const horizon = buildPlanningHorizon(availability.planning_start_date, availability.planning_months);

  const state = {
    calendarRows: [],
    rejectionLog: [],
    traces: [],
    weeklySummary: initWeeklySummary(horizon),
    scheduledByActivityId: new Map(),
    scheduledByGoalActionId: new Map()
  };

  scheduleClinicalMeasurements(activities, resources, horizon, state);
  applyFastingMealRules(activities, resources, horizon, state);
  scheduleStructuredMeals(activities, resources, horizon, state);
  scheduleWeeklyFitness(activities, resources, horizon, state);
  scheduleRecoveryActions(activities, resources, horizon, state);
  scheduleSupportActivities(activities, resources, horizon, state);

  reconcileWeeklyTargets(activities, resources, horizon, state);
  validateFinalCalendar(state.calendarRows, resources, state);

  return {
    calendar_rows: state.calendarRows,
    rejection_log: state.rejectionLog,
    weekly_goal_summary: state.weeklySummary,
    scheduler_trace: state.traces
  };
}

function placeDemand(demand, candidateActivities, resources, horizon, state) {
  const candidates = [];

  for (const activity of candidateActivities) {
    const candidateSlots = generateCandidateSlots(activity, demand, resources, horizon, state);

    for (const slot of candidateSlots) {
      const validation = validateCandidate(activity, slot, demand, resources, state);

      if (!validation.valid) {
        state.rejectionLog.push(toRejection(activity, slot, demand, validation));
        continue;
      }

      candidates.push({
        activity,
        slot,
        validation,
        score: scoreCandidate(activity, slot, demand, resources, state)
      });
    }
  }

  if (candidates.length === 0) {
    return createDeferredOrRejectedRow(demand, candidateActivities, state);
  }

  candidates.sort((a, b) => b.score - a.score || compareTieBreakers(a, b));
  const selected = candidates[0];
  const row = createCalendarRow(selected.activity, selected.slot, demand, selected.validation);
  state.calendarRows.push(row);
  updateGoalCounters(row, state);
  return row;
}
```

---

## 9. Recommended debug views in the app

Add these inspection panels so the calendar is debuggable:

### 9.1 “Why is this here?” panel

For each calendar row, show:

- original demand
- selected activity
- primary vs substitution
- selected reason codes
- target contribution
- provider/equipment/location match
- dependency/prep status
- rejected alternatives

### 9.2 Weekly target panel

For each week, show:

- aerobic: actual / 2
- strength: actual / 2
- recovery: actual / 4
- structured meals by slot
- exceptions and gap reasons

### 9.3 Rejection explorer

Filterable by:

- date
- activity family
- reason code
- goal action
- provider unavailable
- location mismatch
- WFH conflict
- fasting conflict
- prep missing

### 9.4 Fasting lab audit

For every lab draw:

- fasting start time
- lab time
- breakfast skipped row
- any rejected caloric intake rows
- fasting confirmation fields

---

## 10. Codex implementation prompt

Use this prompt when asking Codex to implement the scheduler:

```text
Implement a deterministic scheduler for the Elyx resource allocator using activity_families.updated.json and availability.updated.json.

Requirements:
1. Normalize activity families into scheduler-facing activity rows, including primary and substitution activities.
2. Normalize availability blocks into indexed calendars for providers, equipment, locations, member blocked times, member location overrides, travel windows, and scheduling rules.
3. Generate demands from family_target, but do not schedule target-zero fallback families as independent weekly goals.
4. Weekly targets:
   - aerobic: 2/week
   - strength: 2/week
   - recovery: 4/week
   - walking breaks must not count toward strength.
5. Schedule clinical measurement activities first, then fasting meal rules, then meals, then weekly fitness, then recovery, then support/check-ins.
6. Enforce fasting labs:
   - lab draw requires 8 hours fasting.
   - no breakfast or caloric meal before lab draw on same day.
   - create explicit skipped breakfast row with reason_code=fasting_lab_same_morning.
7. Enforce prep metadata:
   - any activity with prep_required or prep_metadata.prep_required must validate required_inputs.
   - remote coach aerobic progression review requires recent aerobic session data in lookback window.
   - clinical reviews require relevant notes/labs/supplement list as stated in prep_metadata.
8. Enforce WFH:
   - on member_location=home/WFH dates, no office-location activities.
   - office walking breaks substitute to home/remote walking break or reject with reason_code=wfh_no_office_location_activity.
9. Enforce travel:
   - during travel windows, use travel_hotel or remote-compatible activities only.
   - no clinic/lab/home/office/gym in-person activities during travel.
10. Implement hard validators before scoring: member availability, location, WFH, travel, provider, equipment, dependencies, prep, fasting, same-day repeat, goal counting.
11. Implement substitution chains only as fallback, never as extra schedule demand.
12. Score valid candidates using preferred day/time, primary vs substitution, target gap, location fit, provider/equipment fit, load spacing, prep status, and over-target penalties.
13. Return four JSON outputs:
   - calendar_rows.json
   - rejection_log.json
   - weekly_goal_summary.json
   - scheduler_trace.json
14. Every scheduled/substituted/skipped/rejected row must include trace_id and reason codes.
15. Add tests for fasting lab breakfast skip, WFH office rejection/substitution, weekly fitness target counts, walking-not-strength rule, prep gating for aerobic review, and travel-window substitution.
```
