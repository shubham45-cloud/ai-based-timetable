/* ═══════════════════════════════════════════════════════════════════════════
   admin_dashboard.js  –  NIET AI Timetable Dashboard
   Even Semester 2025-26  |  CSE Department
   ═══════════════════════════════════════════════════════════════════════════ */

const BASE_URL = "http://127.0.0.1:8000";

// ── Real sections from your DB ───────────────────────────────────────────────
// ── Real sections from your DB ───────────────────────────────────────────────
const SECTIONS = [
  { id: 1, label: "SEM IV-A", short: "4A", combined_dept: 7, combined_label: "4A+4B+4C COMBINED" },
  { id: 2, label: "SEM IV-B", short: "4B", combined_dept: 7, combined_label: "4A+4B+4C COMBINED" },
  { id: 3, label: "SEM IV-C", short: "4C", combined_dept: 7, combined_label: "4A+4B+4C COMBINED" },
  { id: 4, label: "SEM VI-A", short: "6A", combined_dept: 8, combined_label: "6A+6B COMBINED" },
  { id: 5, label: "SEM VI-B", short: "6B", combined_dept: 8, combined_label: "6A+6B COMBINED" },
  // We keep 7 and 8 here so the API still fetches their data, but we hide them from the UI menus
  { id: 7, label: "4ABC", short: "4ABC", hidden: true },
  { id: 8, label: "6AB",  short: "6AB",  hidden: true },
];

// Mon–Fri only (Saturday is OFF)
const DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"];
const DAY_LABELS = { MONDAY:"MON", TUESDAY:"TUE", WEDNESDAY:"WED", THURSDAY:"THU", FRIDAY:"FRI" };

// Exact period times matching your college schedule
const PERIOD_TIMES = {
  1: "9:10 – 10:00",
  2: "10:00 – 10:50",
  3: "10:50 – 11:40",
  4: "11:40 – 12:30",
  // Lunch after P4
  5: "1:30 – 2:30",
  6: "2:30 – 3:20",
  7: "3:20 – 4:10",
  8: "4:10 – 5:00",
};

const LUNCH_AFTER_PERIOD = 4;   // lunch break inserted after this period

// ── In-memory store: dept_id → array of timetable entries ───────────────────
const timetableStore = {};

// ── Currently active tab dept_id ─────────────────────────────────────────────
let activeTab = 1;

// ── DOM refs ─────────────────────────────────────────────────────────────────
const generateBtn  = document.getElementById("generateBtn");
const deleteBtn    = document.getElementById("deleteBtn");
const exportBtn    = document.getElementById("exportBtn");
const tableWrapper = document.getElementById("tableWrapper");
const loaderBar    = document.getElementById("loaderBar");
const statusPill   = document.getElementById("statusPill");
const tabsBar      = document.getElementById("tabsBar");
const toastEl      = document.getElementById("toast");

// ═══════════════════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function getToken() {
  return localStorage.getItem("accessToken") || "";
}

// Status pill
function setStatus(msg, type = "idle") {
  statusPill.textContent = msg;
  statusPill.className = `status-pill status-${type}`;
}

// Loader bar
function setLoading(on) {
  loaderBar.classList.toggle("active", on);
  generateBtn.disabled = on;
  deleteBtn.disabled   = on;
  generateBtn.innerHTML = on
    ? `<svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="animation:spin 1s linear infinite"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg> Generating…`
    : `<svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Generate Timetable`;
}

// Add spin keyframe once
const spinStyle = document.createElement("style");
spinStyle.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`;
document.head.appendChild(spinStyle);

// Toast notification
let toastTimer;
function showToast(msg, duration = 3500) {
  clearTimeout(toastTimer);
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), duration);
}

// Auth headers
function authHeaders() {
  return { "Authorization": `Bearer ${getToken()}` };
}

// ═══════════════════════════════════════════════════════════════════════════
//  RENDER TIMETABLE
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Build a lookup:  dataMap[day][period] = entry
 * Also flags which periods are the SECOND half of a lab
 * (same subject+teacher+room in consecutive periods → merged into one cell)
 */
function buildDataMap(entries) {
  const map = {};
  entries.forEach(e => {
    if (!map[e.day_of_week]) map[e.day_of_week] = {};
    map[e.day_of_week][e.period_no] = e;
  });
  return map;
}

/**
 * Returns a Set of "day:period" strings that are the SECOND row of a lab
 * (they will be skipped when rendering — first row uses rowspan=2)
 */
function findLabContinuations(dataMap) {
  const skip = new Set();
  const periods = Object.keys(PERIOD_TIMES).map(Number);

  DAYS.forEach(day => {
    const dayData = dataMap[day] || {};
    for (let i = 0; i < periods.length - 1; i++) {
      const p  = periods[i];
      const p2 = periods[i + 1];
      const e1 = dayData[p];
      const e2 = dayData[p2];
      if (
        e1 && e2 &&
        e1.subject?.subject_id === e2.subject?.subject_id &&
        e1.teacher?.teacher_id === e2.teacher?.teacher_id &&
        e1.room?.room_id       === e2.room?.room_id
      ) {
        skip.add(`${day}:${p2}`);
      }
    }
  });
  return skip;
}

/** Decide CSS class for a cell */
function cellClass(entry) {
  if (entry._is_merged_combined) return "cell-combined";
  const roomName = entry.room?.room_name ?? "";
  if (roomName.toUpperCase().includes("LAB")) return "cell-lab";
  return "cell-theory";
}

/** Room badge class */
function roomBadgeClass(entry) {
  if (entry._is_merged_combined) return "room-badge-combined";
  const roomName = entry.room?.room_name ?? "";
  if (roomName.toUpperCase().includes("LAB")) return "room-badge-lab";
  return "room-badge-classroom";
}

/**
 * Main render function.
 * Draws the timetable for `deptId` into #tableWrapper.
 */
function renderTimetable(deptId) {
  const section = SECTIONS.find(s => s.id === deptId);
  
  // 1. Get main section entries
  let entries = [...(timetableStore[deptId] || [])];

  // 2. If this section shares combined classes, merge them in!
  if (section && section.combined_dept) {
    const combinedEntries = timetableStore[section.combined_dept] || [];
    // Mark these entries so they get the purple "Combined" styling
    const markedCombined = combinedEntries.map(e => ({
      ...e,
      _is_merged_combined: true,
      _combined_label: section.combined_label
    }));
    entries = entries.concat(markedCombined);
  }

  if (entries.length === 0) {
    tableWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <p>No timetable entries found for <strong>${section?.label ?? deptId}</strong>.</p>
        <p style="margin-top:6px;font-size:12px;color:var(--muted2)">
          Click <strong>Generate Timetable</strong> to populate.
        </p>
      </div>`;
    return;
  }

  const dataMap  = buildDataMap(entries);
  const skipSet  = findLabContinuations(dataMap);
  const periods  = Object.keys(PERIOD_TIMES).map(Number);

  // ── Build table HTML ─────────────────────────────────────────────────────
  let html = `
    <table>
      <colgroup>
        <col style="width:90px">
        ${DAYS.map(() => `<col>`).join("")}
      </colgroup>
      <thead>
        <tr>
          <th>SLOT</th>
          ${DAYS.map(d => `<th>${DAY_LABELS[d]}</th>`).join("")}
        </tr>
      </thead>
      <tbody>`;

  html += `<tr class="time-row">
    <td class="time-cell">TIME</td>
    ${DAYS.map(() => `<td style="background:#f0f3f8;border:1px solid var(--border2);"></td>`).join("")}
  </tr>`;

  periods.forEach((p, idx) => {
    if (p === LUNCH_AFTER_PERIOD + 1) {
      html += `<tr class="lunch-row">
        <td colspan="${DAYS.length + 1}">🍽️ &nbsp; LUNCH BREAK &nbsp; 12:30 pm – 1:30 pm</td>
      </tr>`;
    }

    html += `<tr>`;

    html += `<td>
      <div class="slot-label">
        P${p}<br>
        <span style="font-size:9px;font-weight:400;color:var(--muted2);letter-spacing:0">${PERIOD_TIMES[p]}</span>
      </div>
    </td>`;

    DAYS.forEach(day => {
      const key = `${day}:${p}`;
      if (skipSet.has(key)) return;

      const entry = dataMap[day]?.[p];

      if (!entry) {
        html += `<td class="cell-empty">
          <div style="height:100%;min-height:52px;display:flex;align-items:center;justify-content:center">—</div>
        </td>`;
        return;
      }

      const nextPeriod = periods[idx + 1];
      const nextKey    = `${day}:${nextPeriod}`;
      const isLabFirst = nextPeriod && skipSet.has(nextKey);
      const rowspan    = isLabFirst ? ` rowspan="2"` : "";

      const cls        = cellClass(entry);
      const badgeCls   = roomBadgeClass(entry);
      const subjectName = entry.subject?.subject_name ?? "—";
      const teacherName = entry.teacher?.teacher_name ?? "—";
      const roomName    = entry.room?.room_name ?? "—";

      // Show LAB tag or COMBINED tag
      const typeTag = isLabFirst
        ? `<span class="type-tag">LAB · 2 hrs</span>`
        : entry._is_merged_combined
          ? `<span class="type-tag">${entry._combined_label}</span>`
          : "";

      html += `<td${rowspan} class="${cls}">
        <div class="cell-inner">
          ${typeTag}
          <div class="subj-name">${subjectName}</div>
          <div class="teacher-name">${teacherName}</div>
          <span class="room-badge ${badgeCls}">${roomName}</span>
        </div>
      </td>`;
    });

    html += `</tr>`;
  });

  html += `</tbody></table>`;
  tableWrapper.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════════════════
//  TAB MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

function initTabs() {
  tabsBar.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      tabsBar.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeTab = parseInt(btn.dataset.dept);
      renderTimetable(activeTab);
    });
  });
}

// Sidebar section quick-links
// ═══════════════════════════════════════════════════════════════════════════
//  SIDEBAR MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

function buildSidebarSections() {
  const container = document.getElementById("sidebarSections");
  container.innerHTML = ""; // Clear out any existing buttons

  SECTIONS.forEach(s => {
    // Skip hidden combined sections (e.g., 4ABC and 6AB)
    if (s.hidden) return; 

    const btn = document.createElement("button");
    btn.className = "nav-btn";
    
    // Make the first item active by default
    if (s.id === activeTab) {
      btn.classList.add("active");
    }

    // Add a nice hexagon icon next to the section names
    btn.innerHTML = `
      <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M12 2l9 4.9V17L12 22l-9-4.9V6.9z"/>
      </svg>
      ${s.label}
    `;

    btn.addEventListener("click", () => {
      // 1. Update sidebar active styling
      container.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      // 2. Sync with the horizontal top tabs
      tabsBar.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", parseInt(b.dataset.dept) === s.id);
      });

      // 3. Update the active tab state and render
      activeTab = s.id;
      renderTimetable(activeTab);

      // 4. Smooth scroll to the timetable (helpful on smaller screens)
      document.querySelector(".timetable-card").scrollIntoView({ behavior: "smooth" });
    });

    container.appendChild(btn);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
//  API: FETCH TIMETABLE FOR ONE SECTION
// ═══════════════════════════════════════════════════════════════════════════

async function fetchSection(deptId) {
  // ✅ Changed to /branch/ to match your FastAPI endpoints!
  const res = await fetch(`${BASE_URL}/timetable/branch/${deptId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Section ${deptId} → HTTP ${res.status}`);
  return res.json(); 
}

async function fetchAllSections() {
  let totalEntries = 0;
  let loadedCount  = 0;

  for (const sec of SECTIONS) {
    try {
      const data = await fetchSection(sec.id);
      timetableStore[sec.id] = data;
      totalEntries += data.length;
      loadedCount++;
    } catch (err) {
      console.warn(`Could not load section ${sec.label}:`, err.message);
      timetableStore[sec.id] = [];
    }
  }

  return { totalEntries, loadedCount };
}

// ═══════════════════════════════════════════════════════════════════════════
//  GENERATE BUTTON
// ═══════════════════════════════════════════════════════════════════════════

generateBtn.addEventListener("click", async () => {
  setLoading(true);
  setStatus("AI solving constraints…", "loading");

  try {
    // 1. Call generate endpoint
    const genRes = await fetch(`${BASE_URL}/admin/timetable/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
    });

    const genData = await genRes.json();

    if (!genRes.ok) {
      const msg = typeof genData.detail === "string"
        ? genData.detail
        : JSON.stringify(genData.detail ?? genData);
      throw new Error(msg);
    }

    setStatus("Fetching section data…", "loading");

    // 2. Fetch all sections
    const { totalEntries, loadedCount } = await fetchAllSections();

    if (totalEntries === 0) {
      throw new Error("Timetable generated but no entries returned from API.");
    }

    // 3. Render active tab
    renderTimetable(activeTab);

    setStatus(`✓ ${totalEntries} slots · ${loadedCount} sections`, "success");
    showToast(`✅ Timetable generated — ${totalEntries} period-slots across ${loadedCount} sections`);

    // Update subjects stat dynamically
    const allSubjIds = new Set(
      Object.values(timetableStore).flat().map(e => e.subject?.subject_id)
    );
    document.getElementById("statSubjects").textContent = allSubjIds.size;

  } catch (err) {
    setStatus(`Error`, "error");
    showToast(`❌ ${err.message}`, 5000);
    console.error("Generate error:", err);
  } finally {
    setLoading(false);
  }
});

// ═══════════════════════════════════════════════════════════════════════════
//  DELETE BUTTON
// ═══════════════════════════════════════════════════════════════════════════

deleteBtn.addEventListener("click", async () => {
  const confirmed = confirm(
    "⚠️  Delete the entire timetable?\n\nThis removes it for ALL sections immediately."
  );
  if (!confirmed) return;

  setLoading(true);
  setStatus("Deleting…", "loading");

  try {
    const res = await fetch(`${BASE_URL}/timetable/delete`, {
      method: "DELETE",
      headers: authHeaders(),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Delete failed");
    }

    // Clear store and re-render empty
    SECTIONS.forEach(s => { timetableStore[s.id] = []; });
    renderTimetable(activeTab);

    setStatus("Deleted", "error");
    showToast("🗑️  Timetable deleted successfully");
    document.getElementById("statSubjects").textContent = "—";

  } catch (err) {
    setStatus("Error", "error");
    showToast(`❌ ${err.message}`, 5000);
  } finally {
    setLoading(false);
  }
});

// ═══════════════════════════════════════════════════════════════════════════
//  EXPORT BUTTON  (downloads visible section as CSV)
// ═══════════════════════════════════════════════════════════════════════════

exportBtn.addEventListener("click", () => {
  const entries = timetableStore[activeTab] || [];
  if (entries.length === 0) {
    showToast("⚠️  Nothing to export — generate or load a timetable first.");
    return;
  }

  const section = SECTIONS.find(s => s.id === activeTab);
  const rows = [["Day", "Period", "Time", "Subject", "Teacher", "Room"]];

  entries
    .slice()
    .sort((a, b) => {
      const dayOrder = DAYS.indexOf(a.day_of_week) - DAYS.indexOf(b.day_of_week);
      return dayOrder !== 0 ? dayOrder : a.period_no - b.period_no;
    })
    .forEach(e => {
      rows.push([
        e.day_of_week,
        `P${e.period_no}`,
        PERIOD_TIMES[e.period_no] ?? "",
        e.subject?.subject_name ?? "",
        e.teacher?.teacher_name ?? "",
        e.room?.room_name ?? "",
      ]);
    });

  const csv     = rows.map(r => r.map(v => `"${v}"`).join(",")).join("\n");
  const blob    = new Blob([csv], { type: "text/csv" });
  const url     = URL.createObjectURL(blob);
  const a       = document.createElement("a");
  a.href        = url;
  a.download    = `timetable_${section?.short ?? activeTab}_even2025.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showToast(`📥 Exported ${section?.label} as CSV`);
});

// ═══════════════════════════════════════════════════════════════════════════
//  ON PAGE LOAD — try to fetch existing timetable from the server
// ═══════════════════════════════════════════════════════════════════════════
async function loadStats() {
  try {
    const faculty = await fetch(`${BASE_URL}/admin/faculty`, {
      headers: authHeaders()
    }).then(r => r.json());

    const subjects = await fetch(`${BASE_URL}/admin/subjects`, {
      headers: authHeaders()
    }).then(r => r.json());

    const rooms = await fetch(`${BASE_URL}/admin/rooms`, {
      headers: authHeaders()
    }).then(r => r.json());

    document.getElementById("statFaculty").textContent = faculty.length;
    document.getElementById("statSubjects").textContent = subjects.length;
    document.getElementById("statRooms").textContent = rooms.length;
  } catch (err) {
    console.error("Stats error:", err);
  }
}
(async () => {
  const token = getToken();

  if (!token) {
    setStatus("Not logged in", "error");
    tableWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔒</div>
        <p>Please <strong>log in</strong> first to view or generate timetables.</p>
      </div>`;
    return;
  }

initTabs();
buildSidebarSections();

await loadStats();

setStatus("Loading…", "loading");
setLoading(true);

  try {
    const { totalEntries, loadedCount } = await fetchAllSections();

    if (totalEntries > 0) {
      renderTimetable(activeTab);
      setStatus(`✓ ${totalEntries} slots loaded`, "success");

      const allSubjIds = new Set(
        Object.values(timetableStore).flat().map(e => e.subject?.subject_id)
      );
      document.getElementById("statSubjects").textContent = allSubjIds.size;

    } else {
      setStatus("Ready", "idle");
      tableWrapper.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📅</div>
          <p>No timetable found — click <strong>Generate Timetable</strong> to create one.</p>
        </div>`;
    }

  } catch (err) {
    setStatus("Ready", "idle");
    console.warn("Page-load fetch failed:", err.message);
  } finally {
    setLoading(false);
  }
})();
document.getElementById("facultyBtn")
?.addEventListener("click", () => {
    window.location.href = "faculty.html";
});

document.getElementById("roomsBtn")
?.addEventListener("click", () => {
    window.location.href = "rooms.html";
});

document.getElementById("subjectsBtn")
?.addEventListener("click", () => {
    window.location.href = "subjects.html";
});
