const state = {
  model: null,
  weekIndex: 0,
  activeScenario: null,
};

const root = document.getElementById("calendar-root");
const grid = document.getElementById("calendar-grid");
const weekLabel = document.getElementById("week-label");
const chips = document.getElementById("scenario-chips");
const drawer = document.getElementById("trace-drawer");
const drawerTitle = document.getElementById("drawer-title");
const drawerContent = document.getElementById("drawer-content");

function topFor(hour) {
  return (hour - state.model.display_hours.start) * 64;
}

function heightFor(duration) {
  return Math.max(duration * 64, 24);
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
  for (const scenario of state.model.scenarios) {
    const count = state.model.scenario_counts[scenario] || 0;
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
  const week = state.model.weeks[state.weekIndex];
  weekLabel.textContent = week ? week.label : "No scheduled weeks";
  renderScenarioChips();
  if (!week) {
    grid.innerHTML = '<div class="empty-state">No scheduled weeks found.</div>';
    return;
  }

  const hours = [];
  for (
    let hour = state.model.display_hours.start;
    hour < state.model.display_hours.end;
    hour += 1
  ) {
    hours.push(hour);
  }

  grid.innerHTML = `
    <div class="calendar-header">
      <div></div>
      ${week.days.map((day) => `<div>${escapeHtml(day.label)}</div>`).join("")}
    </div>
    <div class="calendar-body">
      <div class="time-column">
        ${hours.map((hour) => `<div class="time-cell">${formatHour(hour)}</div>`).join("")}
      </div>
      ${week.days.map((day, dayIndex) => renderDayColumn(week, dayIndex, hours)).join("")}
    </div>
  `;
}

function renderDayColumn(week, dayIndex, hours) {
  const unavailable = week.unavailable_blocks
    .filter((block) => block.day_index === dayIndex)
    .map(
      (block) =>
        `<div class="unavailable" style="top:${topFor(block.start_hour)}px;height:${heightFor(block.duration_hours)}px">${escapeHtml(block.label)}</div>`
    )
    .join("");

  const activities = week.activities
    .filter((activity) => activity.day_index === dayIndex)
    .map(renderActivity)
    .join("");

  return `
    <div class="day-column">
      ${hours.map(() => '<div class="hour-line"></div>').join("")}
      ${unavailable}
      ${activities}
    </div>
  `;
}

function renderActivity(activity) {
  const hidden =
    state.activeScenario && !activity.scenario_flags.includes(state.activeScenario);
  const badges = activity.badges
    .map((badge) => `<span class="badge">${escapeHtml(badge)}</span>`)
    .join("");
  return `
    <button
      type="button"
      class="activity type-${escapeHtml(activity.activity_type)} ${hidden ? "hidden" : ""}"
      style="top:${topFor(activity.start_hour)}px;height:${heightFor(activity.duration_hours)}px"
      data-trace-id="${escapeHtml(activity.trace_id)}"
      data-title="${escapeHtml(activity.title)}"
    >
      <div class="activity-title">${escapeHtml(activity.title)}</div>
      <div class="activity-meta">${escapeHtml(activity.start_time)}-${escapeHtml(activity.end_time)} · ${escapeHtml(activity.location_id || activity.mode)}</div>
      <div class="badges">${badges}</div>
    </button>
  `;
}

function formatHour(hour) {
  if (hour === 12) return "12pm";
  if (hour > 12) return `${hour - 12}pm`;
  return `${hour}am`;
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
    <p><strong>Policy:</strong> ${escapeHtml(trace.policy_fit_summary)}</p>
    <p><strong>Resources:</strong> ${escapeHtml(trace.resource_fit_summary)}</p>
    <p><strong>Handoff:</strong> ${escapeHtml(trace.provider_handoff_summary || "None")}</p>
    <h3>Failed Checks</h3>
    ${
      failedChecks.length
        ? `<ul>${failedChecks.map((check) => `<li><strong>${escapeHtml(check.name)}:</strong> ${escapeHtml(check.reason)}</li>`).join("")}</ul>`
        : "<p>No failed checks on selected slot.</p>"
    }
    <h3>Rejected Candidates</h3>
    <pre>${escapeHtml(JSON.stringify((trace.rejected_candidates || []).slice(0, 5), null, 2))}</pre>
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
  const activity = event.target.closest(".activity");
  if (!activity) return;
  openTrace(activity.dataset.traceId, activity.dataset.title);
});

fetch(root.dataset.source)
  .then((response) => response.json())
  .then((model) => {
    state.model = model;
    render();
  })
  .catch((error) => {
    grid.innerHTML = `<div class="empty-state">Failed to load calendar interface: ${escapeHtml(error.message)}</div>`;
  });
