# Realism Rules

The goal is realistic synthetic data, not maximum variety.

The final dataset should feel like one coherent member journey over 3 months.

## General realism

- Activities should be tied to member goals.
- Activities should reflect member preferences and constraints.
- Frequencies should be plausible.
- Durations should be plausible.
- Consultations and labs should not occur unrealistically often.
- High-load activities should not dominate the plan.
- Medication and supplement activities should be low-load and dependency-aware.
- Food activities should include real breakfast, lunch, and dinner prescriptions where they matter to the member journey. Supplements do not count as meals.
- Food activities may be frequent, but avoid creating dozens of duplicate meal rows.
- Therapy should be occasional or recovery-driven unless the profile clearly justifies more.
- Travel should cause realistic adaptation, not just labels.
- Weekly goal coverage should be interpretable. Low-complexity daily habits should not inflate the apparent progress toward major goals.

## Frequency realism

Plausible patterns:

- medication/supplement: daily, weekly, or protocol-based
- food: daily or several times per week
- fitness: 2-5 times per week depending on load
- high-load fitness: not daily
- therapy: occasional, weekly, or recovery-triggered
- consultation: once, monthly, weekly for coaching, or milestone-based
- labs: once, monthly, or quarterly, not daily

## Load realism

- High-load activities should be limited.
- High-load lower-body training should respect knee and travel constraints.
- Recovery and mobility should appear after travel or high-load weeks.
- Poor sleep, pain escalation, and long flights should bias toward lower-load alternatives.
- Travel over 3 hours should create arrival-day or next-day fatigue logic. Do not treat a new-location day like an ordinary day.

## Travel realism

Planned travel may have:

- hotel gym
- hotel pool
- remote consultations
- limited local provider continuity
- limited lab access

Last-minute travel may have:

- hotel room only
- unreliable gym access
- restaurant meals
- higher work stress
- reduced sleep
- remote support only
- post-arrival fatigue after travel over 3 hours

## Resource realism

- Provider calendars should be independent from member preferences.
- Equipment may have maintenance or location constraints.
- Chef/cook availability should be limited.
- Lab availability should be constrained and usually morning-based.
- Locations should obey travel compatibility.

## Substitution realism

A substitution should not be random. It should preserve intent.

Good examples:

- in-person trainer strength session -> remote hotel-gym strength session
- high-load lower-body session after knee discomfort -> low-load mobility or cycling
- prepared breakfast when chef unavailable -> no-prep high-protein breakfast
- sauna unavailable -> breathwork or mobility recovery

Bad examples:

- lab test -> sauna
- medication -> cardio
- physician review -> protein shake
- strength training -> unrelated journaling

## Metrics realism

Metrics should fit the activity type.

Examples:

- fitness: RPE, heart rate, sets/reps, knee discomfort, completion
- food: meal completion, protein servings, fiber servings, post-meal energy, CGM note
- medication: completion, miss reason, side-effect flag
- therapy: recovery score, sleep quality next day, completion
- consultation: provider notes, next actions, completion
