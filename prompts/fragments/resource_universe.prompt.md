# Resource Universe Rules

The resource universe defines every concrete provider, equipment item, location,
travel window, and local transition-buffer rule that later files may reference.

After this stage, later generation stages must only reference IDs present in `resource_universe.json` or the member profile's travel windows.

## Required top-level collections

The output must include:

- `providers`
- `equipment`
- `locations`
- `travel_windows`
- `travel_time_rules`

## Required provider coverage

Include at least one provider for each role:

- trainer
- physiotherapist
- dietitian
- physician
- phlebotomist or lab provider
- chef/cook

A health coach, recovery therapist, or remote provider pool may also be included if useful.

## Required location coverage

Include at least these locations:

- home
- office
- gym
- clinic
- lab
- travel hotel
- remote

Use stable location IDs such as:

- `home`
- `office`
- `gym`
- `clinic`
- `lab`
- `travel_hotel`
- `remote`

## Transition And Travel-State Rules

Use `travel_time_rules` for practical same-day transition buffers between
relevant local locations. These buffers let the scheduler reject impossible
back-to-back rows in different places.

Example:

```json
{
  "from_location_id": "office",
  "to_location_id": "gym",
  "minutes": 30
}
```

Include coarse rules for common local moves such as home, office, gym,
restaurant, clinic, and lab. Do not model airport transfers as member-facing
calendar tasks. Exact travel windows should still define when the member is in
travel state, and travel over 3 hours should bias the plan toward lower-load or
recovery activities.

## Provider rules

Each provider should include:

- `provider_id`
- `provider_type`
- `display_name`
- `modalities_supported`
- `location_ids`
- `remote_supported`
- `travel_compatible`
- `care_context_supported`
- `notes`

Provider availability is not defined here. Availability is generated in the availability stage. Do not make provider availability match member preferences here.

## Equipment rules

Each equipment item should include:

- `equipment_id`
- `equipment_type`
- `display_name`
- `location_ids`
- `travel_compatible`
- `availability_required`
- `notes`

Equipment should include both fixed and portable resources when useful.

## Location rules

Each location should include:

- `location_id`
- `location_type`
- `display_name`
- `timezone`
- `travel_compatible`
- `available_equipment_ids`
- `notes`

## Travel window rules

Travel windows should align with the member profile.

Each travel window should include:

- `travel_window_id`
- `start`
- `end`
- `travel_type`
- `origin_location_id`
- `destination_label`
- `estimated_travel_duration_hours`
- `arrival_fatigue_risk`
- `available_location_ids`
- `member_location_override`
- `notes`

Include both planned travel and last-minute travel.
