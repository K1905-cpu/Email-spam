// ==========================================================================
// SpamShield AI — Scan History Page Controller
// Author: Kalp Shah
// ==========================================================================

// Check if page was reloaded / refreshed by user, redirect to Email Detector
try {
  const navEntries = performance.getEntriesByType("navigation");
  if (navEntries.length > 0 && navEntries[0].type === "reload") {
    window.location.replace("index.html");
  }
} catch (e) {}

document.addEventListener("DOMContentLoaded", () => {
  const historyBody = document.getElementById("history-body");
  const filterBtns = document.querySelectorAll(".filter-btn");
  const btnClearHistory = document.getElementById("btn-clear-history");
  const btnExportJson = document.getElementById("btn-export-json");

  const statTotal = document.getElementById("hist-stat-total");
  const statSpam = document.getElementById("hist-stat-spam");
  const statHam = document.getElementById("hist-stat-ham");
  const statRatio = document.getElementById("hist-stat-ratio");

  let scanHistory = JSON.parse(localStorage.getItem("spamshield_history") || "[]");
  let currentFilter = "all";

  // Load Model Stats for Navbar
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      if (res.ok) {
        const data = await res.json();
        if (data.metadata && data.metadata.metrics) {
          const m = data.metadata.metrics;
          const navAcc = document.getElementById("nav-acc-val");
          const navPrec = document.getElementById("nav-prec-val");
          if (navAcc) navAcc.textContent = `${m.accuracy}%`;
          if (navPrec) navPrec.textContent = `${m.precision}%`;
        }
      }
    } catch (err) {
      console.log("Running in offline mode");
    }
  }

  // Update Summary Stats
  function updateSummaryStats() {
    const total = scanHistory.length;
    const spamCount = scanHistory.filter(i => i.isSpam).length;
    const hamCount = total - spamCount;
    const cleanRatio = total > 0 ? Math.round((hamCount / total) * 100) : 100;

    if (statTotal) statTotal.textContent = total;
    if (statSpam) statSpam.textContent = spamCount;
    if (statHam) statHam.textContent = hamCount;
    if (statRatio) statRatio.textContent = `${cleanRatio}%`;
  }

  // Render Table
  function renderHistory() {
    updateSummaryStats();

    let filtered = scanHistory;
    if (currentFilter === "spam") filtered = scanHistory.filter(i => i.isSpam);
    if (currentFilter === "ham") filtered = scanHistory.filter(i => !i.isSpam);

    if (filtered.length === 0) {
      historyBody.innerHTML = `
        <tr>
          <td colspan="6" class="table-empty">
            No ${currentFilter === "all" ? "scanned emails" : currentFilter + " items"} found. 
            <a href="index.html" style="color: var(--accent-cyan); text-decoration: underline; margin-left: 6px;">Open Detector &rarr;</a>
          </td>
        </tr>`;
      return;
    }

    historyBody.innerHTML = filtered.map(item => `
      <tr>
        <td style="color: var(--text-muted); font-family: var(--font-mono); font-size: 12px; white-space: nowrap;">
          ${item.time}
        </td>
        <td style="font-weight: 500; max-width: 380px;">
          <div style="color: var(--text-primary); font-weight: 600; font-size: 13.5px; margin-bottom: 2px;">
            ${escapeHtml(item.fullSubject || "No Subject Line")}
          </div>
          <div style="color: var(--text-secondary); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${escapeHtml(item.snippet || item.fullBody || "")}
          </div>
        </td>
        <td>
          <span class="table-badge ${item.isSpam ? 'table-badge-spam' : 'table-badge-ham'}">
            ${item.isSpam ? 'SPAM' : 'CLEAN (HAM)'}
          </span>
        </td>
        <td style="font-weight: 700; font-family: var(--font-mono); color: ${item.isSpam ? '#f87171' : '#34d399'};">
          ${item.riskScore}/100
        </td>
        <td style="color: var(--text-secondary); font-family: var(--font-mono); font-size: 12.5px;">
          ${item.confidence || '95%'}
        </td>
        <td style="white-space: nowrap;">
          <button type="button" class="btn-table-retest" data-id="${item.id}" title="Load this email back into the Detector">
            Retest
          </button>
          <button type="button" class="btn-table-delete" data-id="${item.id}" title="Remove this record" style="margin-left: 6px; background: transparent; border: 1px solid var(--panel-border); color: var(--text-muted); padding: 4px 8px; border-radius: var(--radius-sm); font-size: 11px; cursor: pointer;">
            Delete
          </button>
        </td>
      </tr>
    `).join("");
  }

  function escapeHtml(text) {
    return (text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Handle Retest & Delete clicks
  historyBody.addEventListener("click", (e) => {
    // Retest
    const retestBtn = e.target.closest(".btn-table-retest");
    if (retestBtn) {
      const itemId = parseInt(retestBtn.getAttribute("data-id"));
      const found = scanHistory.find(i => i.id === itemId);
      if (found) {
        localStorage.setItem("spamshield_retest_subject", found.fullSubject || "");
        localStorage.setItem("spamshield_retest_body", found.fullBody || found.snippet || "");
        window.location.href = "index.html";
      }
      return;
    }

    // Delete single
    const deleteBtn = e.target.closest(".btn-table-delete");
    if (deleteBtn) {
      const itemId = parseInt(deleteBtn.getAttribute("data-id"));
      scanHistory = scanHistory.filter(i => i.id !== itemId);
      localStorage.setItem("spamshield_history", JSON.stringify(scanHistory));
      renderHistory();
    }
  });

  // Filter Buttons
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.getAttribute("data-filter");
      renderHistory();
    });
  });

  // Clear All
  btnClearHistory.addEventListener("click", () => {
    if (confirm("Are you sure you want to clear all scan history logs?")) {
      scanHistory = [];
      localStorage.removeItem("spamshield_history");
      renderHistory();
    }
  });

  // Export JSON
  btnExportJson.addEventListener("click", () => {
    if (scanHistory.length === 0) {
      alert("No inspection logs available to export.");
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(scanHistory, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `spamshield_history_${new Date().toISOString().slice(0, 10)}.json`);
    dlAnchor.click();
  });

  // Initial Load
  loadStats();
  renderHistory();
});
