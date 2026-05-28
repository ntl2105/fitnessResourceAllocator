const state = {
  model: null,
  weekIndex: 0,
  activeScenario: null,
  modelSignature: null,
};

const root = document.getElementById("calendar-root");
const grid = document.getElementById("calendar-grid");
const weekLabel = document.getElementById("week-label");
const chips = document.getElementById("scenario-chips");
const drawer = document.getElementById("trace-drawer");
const drawerTitle = document.getElementById("drawer-title");
const drawerContent = document.getElementById("drawer-content");
const recapRoot = document.getElementById("recap-root");
const profileRoot = document.getElementById("member-profile-root");
const activityBoardRoot = document.getElementById("activity-board-root");

function setupCalendarTabs() {
  const tabs = Array.from(document.querySelectorAll("[data-tab-target]"));
  if (!tabs.length) return;

  for (const tab of tabs) {
    tab.addEventListener("click", () => {
      for (const candidate of tabs) {
        const target = document.getElementById(candidate.dataset.tabTarget);
        const active = candidate === tab;
        candidate.className = active ? "calendar-tab active" : "calendar-tab";
        candidate.setAttribute("aria-selected", String(active));
        if (target) target.hidden = !active;
      }
    });
  }
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

function renderScenarioChips() {
  chips.innerHTML = "";
  const week = state.model.weeks[state.weekIndex];
  const counts = week ? weekScenarioCounts(week) : {};
  for (const scenario of state.model.scenarios) {
    const count = counts[scenario] || 0;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip ${state.activeScenario === scenario ? "active" : ""}`;
    button.textContent = `${scenario.replaceAll("_", " ")} (${count})`;
    button.onclick = () => {
      state.activeScenario = state.activeScenario === scenario ? null : scenario;
      render();
    };
    chips.appendChild(button);
  }
}

function render() {
  if (!state.model) return;
  const week = state.model.weeks[state.weekIndex];
  weekLabel.textContent = week ? week.label : "No scheduled weeks";
  renderScenarioChips();
  if (!week) {
    grid.innerHTML = '<div class="empty-state">No scheduled weeks found.</div>';
    return;
  }

  grid.innerHTML = `
    ${renderDataQualityWarnings()}
    ${renderCategoryTime(week)}
    ${renderLocationBands(week)}
    <p class="filter-help">Counts reflect the selected week. Filtering only affects visible activities in this week.</p>
    <div class="agenda-grid">
      ${week.days.map((day, dayIndex) => renderAgendaDay(week, day, dayIndex)).join("")}
    </div>
    ${renderGoalCoverage(week)}
    ${renderUnscheduledItems(week)}
  `;
}

function recapSignature(model) {
  return JSON.stringify({
    totals: model.three_month_recap?.totals || {},
    goals: (model.three_month_recap?.goals || []).map((goal) => ({
      goal_id: goal.goal_id,
      status: goal.status,
      actions: (goal.actions || []).map((action) => ({
        action_id: action.action_id,
        actual: action.actual,
        target: action.target,
        status: action.status,
      })),
    })),
    weekCount: model.three_month_recap?.horizon?.week_count || 0,
    rowCount: (model.weeks || []).reduce(
      (total, week) => total + (week.activities || []).length + (week.habit_blocks || []).length,
      0
    ),
  });
}

function applyCalendarModel(model) {
  const previousWeekStart = state.model?.weeks?.[state.weekIndex]?.start_date;
  const nextWeekIndex = previousWeekStart
    ? Math.max(0, (model.weeks || []).findIndex((week) => week.start_date === previousWeekStart))
    : state.weekIndex;
  const nextSignature = recapSignature(model);

  state.model = model;
  state.weekIndex = Math.min(
    Math.max(nextWeekIndex, 0),
    Math.max((model.weeks || []).length - 1, 0)
  );
  state.modelSignature = nextSignature;
  renderThreeMonthRecap(model.three_month_recap);
  renderMemberProfile(model.member_profile);
  renderActivityBoard(model.activity_board);
  render();
}

function loadCalendarInterface({silent = false} = {}) {
  return fetch(root.dataset.source, {cache: "no-store"})
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((model) => {
      const nextSignature = recapSignature(model);
      if (silent && state.modelSignature === nextSignature) return;
      applyCalendarModel(model);
    })
    .catch((error) => {
      if (!silent) {
        grid.innerHTML = `<div class="empty-state">Failed to load calendar interface: ${escapeHtml(error.message)}</div>`;
      }
    });
}

function renderMemberProfile(profile) {
  if (!profileRoot || !profile) return;
  const identity = profile.identity || {};
  const goals = (profile.goals || []).map(renderProfileGoal).join("");
  profileRoot.innerHTML = `
    <section class="profile-hero">
      <div>
        <div class="eyebrow">Member Profile</div>
        <h2>${escapeHtml(identity.name)}</h2>
        <p>${escapeHtml(identity.summary)}</p>
      </div>
      <div class="profile-stat-grid">
        ${(profile.stats || []).map((stat) => `
          <div class="profile-stat">
            <span>${escapeHtml(stat.label)}</span>
            <strong>${escapeHtml(stat.value)}</strong>
          </div>
        `).join("")}
      </div>
    </section>
    <section class="profile-band profile-band-priority">
      <div class="profile-band-header">
        <div>
          <div class="eyebrow">Planning Inputs</div>
          <h3>Goals and Scheduler Rules</h3>
        </div>
      </div>
      <div class="member-profile-grid profile-priority-grid">
        ${renderProfileSection("Goals", "profile-goal-grid", goals)}
        ${renderProfileFacts("Scheduling Rules", profile.scheduling_rules)}
      </div>
    </section>
    <section class="profile-band">
      <div class="profile-band-header">
        <div>
          <div class="eyebrow">Operating Context</div>
          <h3>Preferences, Constraints, Access</h3>
        </div>
      </div>
      <div class="member-profile-grid profile-context-grid">
        ${renderProfileFacts("Preferences", profile.preferences)}
        ${renderProfileFacts("Constraints", profile.constraints)}
        ${renderProfileFacts("Dietary Access", profile.dietary_access)}
        ${renderProfileFacts("Baseline Snapshot", profile.baseline)}
      </div>
    </section>
    <section class="profile-band">
      <div class="profile-band-header">
        <div>
          <div class="eyebrow">Resources and Timeline</div>
          <h3>Journey, Travel, Providers</h3>
        </div>
      </div>
      <div class="member-profile-grid profile-resource-grid">
        ${renderProfileTimeline(profile.journey_phases)}
        ${renderTravelWindows(profile.travel_windows)}
        ${renderProviderUniverse(profile.provider_universe)}
      </div>
    </section>
  `;
}

function renderThreeMonthRecap(recap) {
  if (!recapRoot) return;
  if (!recap || !(recap.goals || []).length) {
    recapRoot.innerHTML = '<p class="empty-state">No three-month goal recap is available.</p>';
    return;
  }
  const totals = recap.totals || {};
  const horizon = recap.horizon || {};
  const validation = recap.validation || [];
  const audit = state.model?.constraint_audit || {};
  recapRoot.innerHTML = `
    <section class="recap-hero">
      <div>
        <div class="eyebrow">Three-Month Recap</div>
        <h2>Final Scheduler Tally</h2>
        <p>Shows the scheduler's final goal report: weekly target pass rate, three-month target pass rate, validation misses, and remaining gaps.</p>
      </div>
      <div class="recap-stat-grid">
        <div class="recap-stat"><span>Horizon</span><strong>${escapeHtml(horizon.label || "n/a")}</strong></div>
        <div class="recap-stat"><span>Weekly Targets Met</span><strong>${escapeHtml(formatRatio(totals.weekly_met_count, totals.weekly_total_count))}</strong></div>
        <div class="recap-stat"><span>3-Month Targets Met</span><strong>${escapeHtml(formatRatio(totals.three_month_met_count, totals.three_month_total_count))}</strong></div>
        <div class="recap-stat"><span>Validation Misses</span><strong>${escapeHtml(`${totals.validation_failed_count || 0} of ${totals.validation_total_count || 0}`)}</strong></div>
        <div class="recap-stat"><span>Constraint Violations</span><strong>${escapeHtml(audit.violation_count || 0)}</strong></div>
        <div class="recap-stat"><span>Goal Actions</span><strong>${escapeHtml(totals.action_count || 0)}</strong></div>
        <div class="recap-stat"><span>Not Fully Met</span><strong>${escapeHtml((totals.at_risk || 0) + (totals.missed || 0))}</strong></div>
      </div>
    </section>
    ${renderRecapExplainer()}
    ${renderConstraintAudit(audit)}
    ${validation.length ? renderValidationRecap(validation) : ""}
    <section class="recap-grid">
      ${(recap.goals || []).map(renderRecapGoal).join("")}
    </section>
  `;
}

function renderConstraintAudit(audit) {
  if (!audit) return "";
  const violations = audit.violations || [];
  return `
    <section class="recap-validation">
      <header>
        <div>
          <div class="eyebrow">Final Calendar Audit</div>
          <h3>Hard Constraint Violations: ${escapeHtml(audit.violation_count || 0)}</h3>
        </div>
      </header>
      ${
        violations.length
          ? `<div class="recap-validation-grid">${violations.slice(0, 6).map((item) => `
              <article class="recap-validation-item status-at_risk">
                <strong>${escapeHtml(item.check_id)}</strong>
                <span>${escapeHtml(item.date || "")} · ${escapeHtml(item.title || "")}</span>
                <em>${escapeHtml(item.message || "")}</em>
              </article>
            `).join("")}</div>`
          : '<p class="empty-state">No hard constraint violations found in the generated calendar.</p>'
      }
    </section>
  `;
}

function formatRatio(value, total) {
  if (total == null || Number(total) === 0) return "n/a";
  return `${value || 0} / ${total}`;
}

function renderValidationRecap(validation) {
  return `
    <section class="recap-validation">
      <header>
        <div>
          <div class="eyebrow">Assignment Validation</div>
          <h3>Weekly Constraint Checks</h3>
        </div>
      </header>
      <div class="recap-validation-grid">
        ${validation.map(renderValidationItem).join("")}
      </div>
    </section>
  `;
}

function renderRecapExplainer() {
  const items = [
    ["Weekly Targets Met", "Weekly goal periods that hit their scheduled target."],
    ["3-Month Targets Met", "Longer-horizon goal actions that hit their 3-month target."],
    ["Validation Misses", "Assignment constraint checks that did not fully pass across weeks."],
    ["Not Fully Met", "Goal actions with some missing weekly or horizon coverage, not necessarily complete failure."],
    ["Periods Met", "For weekly goals, ISO weeks that met target; for 3-month goals, whether the full period met target."],
    ["Scheduled / Target", "Counted credit compared with expected units. Extra units in one weekly period do not compensate for missed periods elsewhere."],
    ["Substitutions", "Scheduled alternatives that preserved the goal intent when the primary option could not be used."],
    ["Blocked", "Task instances that the scheduler could not place after checking policy and resource constraints."],
  ];
  return `
    <section class="recap-explainer">
      <div>
        <div class="eyebrow">How To Read This</div>
        <h3>Recap Field Guide</h3>
      </div>
      <dl>
        ${items.map(([label, description]) => `
          <div>
            <dt>${escapeHtml(label)}</dt>
            <dd>${escapeHtml(description)}</dd>
          </div>
        `).join("")}
      </dl>
    </section>
  `;
}

function renderValidationItem(item) {
  const examples = (item.failed_examples || [])
    .map((example) => `${example.week}: ${example.actual_units}/${example.expected_units}`)
    .join("; ");
  return `
    <article class="recap-validation-item status-${escapeHtml(item.status)}">
      <strong>${escapeHtml(item.label)}</strong>
      <span>${escapeHtml(item.met_count || 0)} of ${escapeHtml(item.period_count || 0)} periods met</span>
      ${examples ? `<em>${escapeHtml(examples)}</em>` : ""}
    </article>
  `;
}

function renderRecapGoal(goal) {
  return `
    <section class="recap-goal status-${escapeHtml(goal.status)}">
      <header>
        <div>
          <span>${goal.priority ? `Priority ${escapeHtml(goal.priority)}` : "Goal"}</span>
          <h3>${escapeHtml(goal.label)}</h3>
          ${goal.description ? `<p>${escapeHtml(goal.description)}</p>` : ""}
        </div>
        <strong>${escapeHtml(displayStatus(goal.status))}</strong>
      </header>
      <div class="recap-action-list">
        ${(goal.actions || []).map(renderRecapAction).join("")}
      </div>
    </section>
  `;
}

function displayStatus(status) {
  const labels = {
    at_risk: "not fully met",
    missed: "missed",
    on_track: "met",
    over_target: "over target",
    support_only: "support only",
    no_activity: "no activity",
  };
  return labels[status] || String(status || "unknown").replaceAll("_", " ");
}

function renderRecapAction(action) {
  const progressLabel = action.support_only
    ? `${action.support_scheduled || 0} support scheduled`
    : `${action.scheduled} of ${action.horizon_target} counted target`;
  const completion = action.completion_percent == null ? "" : `${action.completion_percent}%`;
  const periodText = action.period_count
    ? `${action.periods_met || 0}/${action.period_count} periods met`
    : "";
  const activityText = (action.top_activities || [])
    .map((item) => `${item.title} (${item.count})`)
    .join("; ");
  return `
    <article class="recap-action status-${escapeHtml(action.status)}">
      <div class="recap-action-main">
        <strong>${escapeHtml(action.label)}</strong>
        <span>${escapeHtml(progressLabel)}${completion ? ` · ${escapeHtml(completion)}` : ""}</span>
        ${action.extra_scheduled ? `<em>${escapeHtml(action.scheduled_total)} total scheduled; extra instances do not cover missed periods.</em>` : ""}
        ${activityText ? `<em>${escapeHtml(activityText)}</em>` : ""}
      </div>
      <div class="recap-action-metrics">
        <span>${escapeHtml(periodText || `${action.weeks_with_coverage || 0} weeks covered`)}</span>
        <span>${escapeHtml(action.substitutions || 0)} substitutions</span>
        <span>${escapeHtml(action.blocked_instances || 0)} blocked</span>
        ${action.extra_scheduled ? `<span>${escapeHtml(action.extra_scheduled)} extra</span>` : ""}
      </div>
    </article>
  `;
}

function renderActivityBoard(board) {
  if (!activityBoardRoot) return;
  const sections = board || [];
  if (!sections.length) {
    activityBoardRoot.innerHTML = '<p class="empty-state">No activity-to-goal mappings found.</p>';
    return;
  }
  activityBoardRoot.innerHTML = `
    <section class="activity-board-header">
      <div>
        <div class="eyebrow">Goal Mapping First</div>
        <h2>Activity Board Review</h2>
        <p>Review how goals map to weekly actions, activity families, scheduled instances, and blocked instances.</p>
      </div>
    </section>
    ${sections.map(renderActivityBoardSection).join("")}
  `;
}

function renderActivityBoardSection(section) {
  return `
    <section class="activity-board-section">
      <header>
        <div>
          <h3>${escapeHtml(section.label)}</h3>
          <p>${escapeHtml(section.notes || "")}</p>
        </div>
        <span>${escapeHtml(section.target_per_week)} weekly target</span>
      </header>
      <div class="activity-board-table">
        <div class="activity-board-row activity-board-row-head">
          <span>Activity</span>
          <span>Cadence</span>
          <span>Delivery</span>
          <span>Metrics / Review</span>
          <span>Backup / Skip</span>
        </div>
        ${(section.activities || []).map(renderActivityBoardRow).join("")}
      </div>
    </section>
  `;
}

function renderActivityBoardRow(activity) {
  const warnings = activity.warnings || [];
  const locations = activity.locations || [];
  const providers = activity.provider_ids || [];
  const backups = activity.backup_activity_ids || [];
  const metrics = activity.metrics || [];
  const prepText = activity.prep_required
    ? `Prep required${activity.prep_source ? ` · ${activity.prep_source}` : ""}`
    : activity.prep_source
      ? `Prep source: ${activity.prep_source}`
      : "No prep required";
  const remoteText = activity.remote_allowed ? "remote ok" : "in-person only";
  const reviewText = warnings.length
    ? warnings.join(" ")
    : (activity.dependencies || []).join(", ") || "ok";
  return `
    <div class="activity-board-row ${warnings.length ? "has-warning" : ""}">
      <span>
        <strong>${escapeHtml(activity.title)}</strong>
        <em>${escapeHtml(activity.activity_type)} · ${activity.is_primary ? "primary" : "substitution"} · ${escapeHtml(activity.family_id)}</em>
        ${activity.details ? `<small>${escapeHtml(activity.details)}</small>` : ""}
      </span>
      <span>
        ${escapeHtml(activity.frequency)}
        <em>${escapeHtml(activity.contribution_role || "n/a")}${activity.counts_toward_weekly_target ? "" : " · support"} · P${escapeHtml(activity.priority)} · ${escapeHtml(activity.load_level)}</em>
        <em>${escapeHtml(activity.scheduled_count)} scheduled · ${escapeHtml(activity.unscheduled_count)} blocked</em>
      </span>
      <span>
        ${escapeHtml(activity.facilitator_type || "n/a")}
        <em>${escapeHtml(locations.join(", ") || "no location")}</em>
        <em>${escapeHtml(remoteText)}${providers.length ? ` · ${escapeHtml(providers.join(", "))}` : ""}</em>
        <em>${escapeHtml(prepText)}</em>
      </span>
      <span>
        ${escapeHtml(metrics.length ? metrics.join(", ") : "No metrics listed")}
        <em>${escapeHtml(reviewText)}</em>
      </span>
      <span>
        ${escapeHtml(backups.length ? backups.join(", ") : "No backup listed")}
        <em>${escapeHtml(activity.skip_adjustment || "Not specified")}</em>
      </span>
    </div>
  `;
}

function renderProfileSection(title, className, content) {
  if (!content) return "";
  return `
    <section class="profile-card ${className}">
      <h3>${escapeHtml(title)}</h3>
      ${content}
    </section>
  `;
}

function renderProfileGoal(goal) {
  return `
    <div class="profile-goal">
      <span>Priority ${escapeHtml(goal.priority)}</span>
      <strong>${escapeHtml(goal.label)}</strong>
      ${goal.description ? `<p>${escapeHtml(goal.description)}</p>` : ""}
      ${goal.target ? `<em>${escapeHtml(goal.target)}</em>` : ""}
    </div>
  `;
}

function renderProfileFacts(title, facts) {
  const items = facts || [];
  if (!items.length) return "";
  return renderProfileSection(
    title,
    "profile-facts",
    `<dl>${items.map((item) => `
      <div>
        <dt>${escapeHtml(item.label)}</dt>
        <dd>${escapeHtml(item.value)}</dd>
      </div>
    `).join("")}</dl>`
  );
}

function renderProfileTimeline(phases) {
  const items = phases || [];
  if (!items.length) return "";
  return renderProfileSection(
    "Journey Timeline",
    "profile-timeline",
    items.map((phase) => `
      <div class="timeline-item">
        <span>${escapeHtml(phase.date_range)}</span>
        <strong>${escapeHtml(phase.label)}</strong>
        <p>${escapeHtml((phase.goals || []).join(", "))}</p>
      </div>
    `).join("")
  );
}

function renderTravelWindows(windows) {
  const items = windows || [];
  if (!items.length) return "";
  return renderProfileSection(
    "Travel Windows",
    "profile-travel-grid",
    items.map((window) => `
      <div class="travel-card">
        <span>${escapeHtml(window.type)}</span>
        <strong>${escapeHtml(window.destination)}</strong>
        <p>${escapeHtml(window.date_range)}</p>
        ${window.notes ? `<em>${escapeHtml(window.notes)}</em>` : ""}
      </div>
    `).join("")
  );
}

function renderProviderUniverse(providers) {
  const items = providers || [];
  if (!items.length) return "";
  return renderProfileSection(
    "Provider Universe",
    "profile-provider-grid",
    items.map((provider) => `
      <div class="provider-card">
        <span>${escapeHtml(provider.type)}</span>
        <strong>${escapeHtml(provider.name)}</strong>
        <p>${escapeHtml((provider.modes || []).join(", "))}</p>
        <em>${escapeHtml((provider.locations || []).join(", "))}</em>
        ${provider.notes ? `<small>${escapeHtml(provider.notes)}</small>` : ""}
      </div>
    `).join("")
  );
}

function renderDataQualityWarnings() {
  const warnings = state.model.data_quality_warnings || [];
  if (!warnings.length) return "";
  return `
    <section class="warning-panel">
      <h2>Data Review Warnings</h2>
      <ul>${warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul>
    </section>
  `;
}

function weekScenarioCounts(week) {
  const counts = {};
  for (const scenario of state.model.scenarios) counts[scenario] = 0;
  for (const activity of week.activities) {
    for (const flag of activity.scenario_flags || []) {
      counts[flag] = (counts[flag] || 0) + 1;
    }
  }
  return counts;
}

function renderGoalCoverage(week) {
  const goals = week.goal_coverage || [];
  if (!goals.length) return "";
  return `
    <section class="goal-panel">
      <h2>Progress Report</h2>
      <p class="panel-note">After scheduling, this shows how the week is meeting goal targets and activity assignments. Support-only actions are tracked separately and excluded from core target progress.</p>
      <div class="goal-grid">
        ${goals.map(renderGoalCard).join("")}
      </div>
    </section>
  `;
}

function renderCategoryTime(week) {
  const rows = week.category_time || [];
  if (!rows.length) return "";
  const maxMinutes = Math.max(1, ...rows.map((row) => row.minutes || 0));
  return `
    <section class="category-time-panel">
      <h2>Weekly Time by Category</h2>
      <p class="panel-note">Scheduled duration for this selected week across the five activity categories.</p>
      <div class="category-time-grid">
        ${rows.map((row) => renderCategoryTimeCard(row, maxMinutes)).join("")}
      </div>
    </section>
  `;
}

function renderCategoryTimeCard(row, maxMinutes) {
  const minutes = row.minutes || 0;
  const hours = formatHours(minutes);
  const width = Math.max(3, Math.round((minutes / maxMinutes) * 100));
  return `
    <div class="category-time-card type-border-${escapeHtml(row.category)}">
      <div>
        <strong>${escapeHtml(row.category)}</strong>
        <span>${escapeHtml(row.activity_count || 0)} activities</span>
      </div>
      <b>${escapeHtml(hours)}</b>
      <div class="category-time-track">
        <span class="type-bg-${escapeHtml(row.category)}" style="width: ${width}%"></span>
      </div>
    </div>
  `;
}

function formatHours(minutes) {
  if (!minutes) return "0h";
  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  if (!hours) return `${remainder}m`;
  return remainder ? `${hours}h ${remainder}m` : `${hours}h`;
}

function renderGoalCard(goal) {
  const title = goal.label || goal.goal_tag || goal.weekly_goal_action_id;
  const target = goal.target_per_week ?? (goal.scheduled + goal.unscheduled);
  const extra = goal.extra_scheduled || 0;
  const rawUnscheduled = goal.raw_unscheduled_instances || 0;
  const supportLine = goal.support_only
    ? `${goal.support_scheduled || 0} support scheduled · ${goal.support_unscheduled || 0} support unscheduled`
    : `Still needed: ${goal.unscheduled} · blocked candidates: ${rawUnscheduled}`;
  const scheduledLine = goal.support_only
    ? "Support-only, excluded from core denominator"
    : `Total scheduled: ${goal.scheduled_total || goal.scheduled}${goal.substitutions ? ` · substitutions: ${goal.substitutions}` : ""}${extra ? ` · extra above target: ${extra}` : ""}`;
  const progressLine = goal.support_only
    ? "Support-only, excluded from core denominator"
    : `Target coverage: ${goal.scheduled} of ${target}`;
  return `
    <div class="goal-card status-${escapeHtml(goal.status)}">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(progressLine)}</span>
      <span>${escapeHtml(scheduledLine)}</span>
      <span>${escapeHtml(supportLine)}</span>
    </div>
  `;
}

function renderUnscheduledItems(week) {
  const items = week.unscheduled_items || [];
  if (!items.length) return "";
  return `
    <section class="risk-panel">
      <h2>Unscheduled / At Risk</h2>
      ${items.slice(0, 8).map((item) => `
        <div class="risk-item">
          <strong>${escapeHtml(item.title || item.activity_id)}</strong>
          <span>${escapeHtml((item.goal_tags || []).join(", "))}</span>
          <span>${escapeHtml(item.reason_summary || "No candidate slot passed.")}</span>
        </div>
      `).join("")}
    </section>
  `;
}

function renderLocationBands(week) {
  const bands = week.location_bands || [];
  if (!bands.length) return "";
  return `
    <div class="location-bands">
      ${bands.map((band) => `
        <div class="location-band" style="grid-column: ${band.start_day_index + 1} / ${band.end_day_index + 2}">
          ${escapeHtml(band.label)}
        </div>
      `).join("")}
    </div>
  `;
}

function renderAgendaDay(week, day, dayIndex) {
  const dayActivities = week.activities
    .filter((activity) => activity.day_index === dayIndex)
    .filter(
      (activity) =>
        !state.activeScenario || activity.scenario_flags.includes(state.activeScenario)
    );
  const dayBlocks = week.unavailable_blocks.filter((block) => block.day_index === dayIndex);
  const dayHabits = (week.habit_blocks || []).filter((block) => block.day_index === dayIndex);

  return `
    <section class="agenda-day">
      <header class="agenda-day-header">
        <div class="agenda-day-label">${escapeHtml(day.label)}</div>
        <div class="agenda-day-count">${dayActivities.length} activities</div>
      </header>
      ${renderDayContext(dayBlocks)}
      ${renderHabitBlocks(dayHabits)}
      <div class="agenda-activities">
        ${
          dayActivities.length
            ? dayActivities.map(renderActivity).join("")
            : '<div class="empty-day">No matching activities</div>'
        }
      </div>
    </section>
  `;
}

function renderHabitBlocks(blocks) {
  if (!blocks.length) return "";
  return `
    <div class="habit-context">
      ${blocks.map((block) => `<div>${escapeHtml(block.summary)}</div>`).join("")}
    </div>
  `;
}

function renderDayContext(blocks) {
  if (!blocks.length) return "";
  return `
    <div class="day-context">
      ${blocks.map((block) => `<div>${escapeHtml(block.label)} · ${formatHour(block.start_hour)} for ${formatDuration(block.duration_hours)}</div>`).join("")}
    </div>
  `;
}

function renderActivity(activity) {
  const badges = activity.badges
    .map((badge) => `<span class="badge">${escapeHtml(badge)}</span>`)
    .join("");
  return `
    <button
      type="button"
      class="agenda-activity type-${escapeHtml(activity.activity_type)}"
      data-trace-id="${escapeHtml(activity.trace_id)}"
      data-title="${escapeHtml(activity.title)}"
    >
      ${activity.travel_to ? `<div class="activity-travel">${escapeHtml(activity.travel_to)}</div>` : ""}
      <div class="activity-time">${escapeHtml(activity.start_time)}-${escapeHtml(activity.end_time)}</div>
      <div class="activity-title">${escapeHtml(activity.title)}</div>
      <div class="activity-meta">${escapeHtml(activity.activity_type)} · ${escapeHtml(activity.location_id || activity.mode)} · ${escapeHtml(activity.load_level)}</div>
      ${activity.facilitator_summary ? `<div class="activity-provider" data-provider-summary="${escapeHtml(activity.provider_summary || "")}">${escapeHtml(activity.facilitator_summary)}</div>` : ""}
      ${activity.meal_summary ? `<div class="activity-value">${escapeHtml(activity.meal_summary)}</div>` : ""}
      ${activity.prep_summary ? `<div class="activity-prep">${escapeHtml(activity.prep_summary)}</div>` : ""}
      ${activity.reason_summary ? `<div class="activity-reason">${escapeHtml(activity.reason_summary)}</div>` : ""}
      <div class="badges">${badges}</div>
    </button>
  `;
}

function formatHour(hour) {
  const whole = Math.floor(hour);
  const minutes = Math.round((hour - whole) * 60);
  const suffix = whole >= 12 ? "pm" : "am";
  const displayHour = whole === 0 ? 12 : whole > 12 ? whole - 12 : whole;
  return `${displayHour}:${String(minutes).padStart(2, "0")}${suffix}`;
}

function formatDuration(hours) {
  if (hours >= 1 && Number.isInteger(hours)) return `${hours}h`;
  if (hours >= 1) return `${hours.toFixed(1)}h`;
  return `${Math.round(hours * 60)}m`;
}

function renderCheckList(checks) {
  if (!checks.length) return "<p>No failed checks on selected slot.</p>";
  return `<ul>${checks.map((check) => `<li><strong>${escapeHtml(check.name)}:</strong> ${escapeHtml(check.reason)}</li>`).join("")}</ul>`;
}

function renderRejectedCandidates(candidates) {
  if (!candidates.length) {
    return "<p>No earlier candidate slots were rejected for this activity.</p>";
  }
  return `
    <div class="trace-cards">
      ${candidates.slice(0, 5).map((candidate) => `
        <section class="trace-card">
          <div class="trace-card-title">${escapeHtml(candidate.slot_summary)}</div>
          <ul>
            ${(candidate.human_reasons || []).map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}
          </ul>
        </section>
      `).join("")}
    </div>
  `;
}

function renderReasonList(reasons, emptyText) {
  if (!reasons || !reasons.length) return `<p>${escapeHtml(emptyText)}</p>`;
  return `<ul>${reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}</ul>`;
}

async function openTrace(traceId, title) {
  if (!traceId) return;
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  drawerTitle.textContent = title || traceId;
  drawerContent.innerHTML = "<p>Loading trace...</p>";
  const response = await fetch(`/api/traces/${traceId}`);
  const trace = await response.json();
  const failedChecks = (trace.constraint_checks || []).filter(
    (check) => check.passed === false
  );
  drawerContent.innerHTML = `
    <p><strong>Status:</strong> ${escapeHtml(trace.final_status)}</p>
    <h3>Why This Activity Exists</h3>
    ${renderReasonList(trace.planning_rationale || [], "No planning rationale available.")}
    <h3>Scheduled Slot</h3>
    <p>${escapeHtml(trace.selected_slot_summary || "No selected slot.")}</p>
    <h3>${trace.final_status === "scheduled" ? "Why This Was Scheduled" : "Why This Was Not Scheduled"}</h3>
    ${trace.final_status === "scheduled"
      ? renderReasonList(trace.why_scheduled || [], "No scheduling explanation available.")
      : renderReasonList(trace.why_not_scheduled || [], "No blocking explanation available.")}
    <p><strong>Policy:</strong> ${escapeHtml(trace.policy_fit_summary)}</p>
    <p><strong>Resources:</strong> ${escapeHtml(trace.resource_fit_summary)}</p>
    <p><strong>Handoff:</strong> ${escapeHtml(trace.provider_handoff_summary || "None")}</p>
    <h3>Failed Checks</h3>
    ${renderCheckList(failedChecks)}
    <h3>Earlier Rejected Attempts</h3>
    <p class="trace-note">These were attempted slots for this same activity before the scheduler found the scheduled slot above.</p>
    ${renderRejectedCandidates(trace.rejected_candidate_summaries || [])}
    <h3>Source Artifacts</h3>
    <ul>${(trace.source_artifact_paths || []).map((path) => `<li>${escapeHtml(path)}</li>`).join("")}</ul>
  `;
}

document.getElementById("previous-week").onclick = () => {
  state.weekIndex = Math.max(0, state.weekIndex - 1);
  render();
};

document.getElementById("next-week").onclick = () => {
  state.weekIndex = Math.min(state.model.weeks.length - 1, state.weekIndex + 1);
  render();
};

document.getElementById("close-drawer").onclick = () => {
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
};

grid.addEventListener("click", (event) => {
  const activity = event.target.closest(".agenda-activity");
  if (!activity) return;
  openTrace(activity.dataset.traceId, activity.dataset.title);
});

loadCalendarInterface();
setInterval(() => loadCalendarInterface({silent: true}), 10000);

setupCalendarTabs();
