// ==========================================================================
// SpamShield AI — Frontend Controller & Visualization Engine
// Author: Kalp Shah
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const form = document.getElementById("spam-form");
  const subjectInput = document.getElementById("subject-input");
  const emailInput = document.getElementById("email-input");
  const charCount = document.getElementById("char-count");
  const btnClear = document.getElementById("btn-clear");
  const btnPaste = document.getElementById("btn-paste");
  const sampleChips = document.getElementById("sample-chips");
  const btnCopyReport = document.getElementById("btn-copy-report");
  const copyBtnText = document.getElementById("copy-btn-text");

  // Assessment Result Elements
  const resultPlaceholder = document.getElementById("result-placeholder");
  const resultContent = document.getElementById("result-content");
  const statusTag = document.getElementById("status-tag");
  const verdictBanner = document.getElementById("verdict-banner");
  const verdictTitle = document.getElementById("verdict-title");
  const threatBadge = document.getElementById("threat-badge");
  const modelNameText = document.getElementById("model-name-text");
  const riskScore = document.getElementById("risk-score");
  const gaugeCircle = document.getElementById("gauge-circle");
  const spamProbText = document.getElementById("spam-prob-text");
  const spamBar = document.getElementById("spam-bar");
  const hamProbText = document.getElementById("ham-prob-text");
  const hamBar = document.getElementById("ham-bar");
  const triggersList = document.getElementById("triggers-list");
  const reasonsList = document.getElementById("reasons-list");

  let currentAnalysisData = null;
  let samplesData = [];
  let scanHistory = JSON.parse(localStorage.getItem("spamshield_history") || "[]");

  // Fallback Real-World Samples
  const defaultSamples = [
    {
      id: 1,
      type: "spam",
      subject: "CONGRATULATIONS! Claim your 2.5 Bitcoin (BTC) Reward",
      body: "Congratulations! You have been selected as the grand winner of the 2026 Crypto Sweepstakes. You won 2.5 Bitcoin (BTC) valued at $165,000. Connect your wallet or reply with your bank routing details immediately to claim your funds before deadline!"
    },
    {
      id: 2,
      type: "spam",
      subject: "URGENT: Your account has been temporarily locked",
      body: "Security Alert: Unauthorized login attempt detected on your bank account. Your access has been restricted. Click here to verify your password and identity immediately to avoid permanent account suspension."
    },
    {
      id: 3,
      type: "spam",
      subject: "Earn $500 to $800 Daily Working Online from Home",
      body: "Immediate hiring for online review assistants. Work from home just 2 hours a day and make thousands of dollars weekly. No experience needed. WhatsApp us right now to start earning cash instantly!"
    },
    {
      id: 4,
      type: "ham",
      subject: "E-Ticket Confirmation: Indigo Flight 6E-284 from AMD to BOM",
      body: "Dear Kalp, your flight booking reference PNR #X8K92P has been confirmed. Departure is scheduled for Friday at 07:15 AM from Terminal 1, Ahmedabad (AMD) arriving at Mumbai (BOM) at 08:30 AM. Web check-in opens 24 hours prior to departure. Have a pleasant journey."
    },
    {
      id: 5,
      type: "ham",
      subject: "Monthly Payment Receipt: Invoice #INV-2026-089",
      body: "Hello Kalp, thank you for your payment. Your cloud hosting and database cluster subscription for the period of August 2026 has been successfully processed. Total Amount: $49.00 charged to your card ending in 4128. Download your full PDF tax invoice from your account billing portal."
    },
    {
      id: 6,
      type: "ham",
      subject: "Engineering Team: Weekly Sprint Review & Architecture Notes",
      body: "Hi team, here is the summary from our weekly technical sync. We completed the core model inference pipeline, optimized database queries, and updated the frontend dashboard. Next sprint will focus on caching and latency benchmarks. Please review the updated documentation."
    }
  ];

  // Update Word Counter
  function updateWordCount() {
    const text = emailInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    charCount.textContent = `${words} word${words === 1 ? "" : "s"}`;
  }

  emailInput.addEventListener("input", updateWordCount);

  // Load Model Stats from Backend
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      if (res.ok) {
        const data = await res.json();
        if (data.metadata && data.metadata.metrics) {
          const m = data.metadata.metrics;
          // Update navbar pills
          const navAcc = document.getElementById("nav-acc-val");
          const navPrec = document.getElementById("nav-prec-val");
          if (navAcc) navAcc.textContent = `${m.accuracy}%`;
          if (navPrec) navPrec.textContent = `${m.precision}%`;
        }
      }
    } catch (err) {
      console.log("Stats running in standalone mode");
    }
  }

  // Load Samples
  async function loadSamples() {
    try {
      const res = await fetch("/api/samples");
      if (res.ok) {
        const data = await res.json();
        samplesData = (data.samples && data.samples.length) ? data.samples : defaultSamples;
      } else {
        samplesData = defaultSamples;
      }
    } catch (err) {
      samplesData = defaultSamples;
    }
  }

  // Client-side fallback rule engine for offline testing
  function localInference(subject, text) {
    const full = `${subject} ${text}`.toLowerCase();
    const spamTriggers = [
      "urgent", "winner", "won", "prize", "lottery", "congratulations", "claim",
      "password", "suspended", "unauthorized", "locked", "funds", "frozen", "verify",
      "bitcoin", "crypto", "free", "cash", "loan", "earn", "money", "offer", "discount",
      "viagra", "keto", "pharmacy", "replica", "airdrop", "deposit", "payout", "risk",
      "guaranteed", "wire", "transfer", "dispute", "redelivery", "wallet", "credit", "irs"
    ];

    let foundTriggers = [];
    let score = 4;

    spamTriggers.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, "i");
      if (regex.test(full)) {
        foundTriggers.push(word);
        score += 18;
      }
    });

    if (/[$€£₹]\s*\d+/.test(full)) {
      foundTriggers.push("currency_amount");
      score += 20;
    }
    if (/https?:\/\/|www\./.test(full)) {
      foundTriggers.push("external_url");
      score += 15;
    }

    score = Math.min(Math.max(score, 2), 99);
    const isSpam = score >= 50;

    let reasons = [];
    if (isSpam) {
      reasons.push("Urgent security verification or financial claim phrasing detected.");
      if (foundTriggers.length > 0) {
        reasons.push(`High correlation with spam trigger vocabulary: ${foundTriggers.slice(0, 5).join(", ")}.`);
      }
    } else {
      reasons.push("Standard transactional / academic / professional email pattern.");
      reasons.push("No deceptive credential harvesting or fraudulent tokens detected.");
    }

    return {
      status: "success",
      is_spam: isSpam,
      label: isSpam ? "SPAM" : "HAM (Legitimate)",
      risk_score: score,
      confidence: isSpam ? score : (100 - score),
      threat_level: score >= 80 ? "Critical Threat" : (score >= 50 ? "Suspicious / Spam" : "Safe / Legitimate"),
      spam_probability: score,
      ham_probability: (100 - score),
      detected_triggers: foundTriggers,
      reasons: reasons,
      model_used: "NLP Classifier Pipeline"
    };
  }

  // Sample Click Handler
  sampleChips.addEventListener("click", (e) => {
    const chip = e.target.closest(".sample-chip");
    if (!chip) return;
    const sampleId = parseInt(chip.getAttribute("data-sample"));
    const sample = samplesData.find(s => s.id === sampleId);
    if (sample) {
      subjectInput.value = sample.subject;
      emailInput.value = sample.body;
      updateWordCount();
      form.dispatchEvent(new Event("submit"));
    }
  });

  // Paste from Clipboard
  btnPaste.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        emailInput.value = text;
        updateWordCount();
      }
    } catch (err) {
      emailInput.focus();
    }
  });

  // Clear Form
  btnClear.addEventListener("click", () => {
    subjectInput.value = "";
    emailInput.value = "";
    updateWordCount();
    resultContent.classList.add("hidden");
    resultPlaceholder.classList.remove("hidden");
    statusTag.textContent = "Awaiting Message";
    statusTag.style.color = "var(--text-secondary)";
    statusTag.style.borderColor = "var(--panel-border)";
  });

  // Handle Form Submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = subjectInput.value.trim();
    const text = emailInput.value.trim();

    if (!text) {
      alert("Please enter message content to scan.");
      return;
    }

    statusTag.textContent = "Analyzing with NLP...";
    statusTag.style.color = "var(--accent-cyan)";
    statusTag.style.borderColor = "var(--accent-cyan)";

    let data = null;
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, text })
      });
      if (res.ok) {
        data = await res.json();
      } else {
        data = localInference(subject, text);
      }
    } catch (err) {
      data = localInference(subject, text);
    }

    currentAnalysisData = { ...data, subject, text };
    renderAssessment(data, subject || text);
  });

  // Render Assessment
  function renderAssessment(data, originalText) {
    resultPlaceholder.classList.add("hidden");
    resultContent.classList.remove("hidden");

    const isSpam = data.is_spam;
    verdictBanner.className = `verdict-banner ${isSpam ? "verdict-spam" : "verdict-ham"}`;
    verdictTitle.textContent = isSpam ? "SPAM DETECTED" : "LEGITIMATE EMAIL (HAM)";
    verdictTitle.style.color = isSpam ? "#f87171" : "#34d399";

    threatBadge.textContent = data.threat_level;
    threatBadge.style.background = isSpam ? "rgba(239, 68, 68, 0.25)" : "rgba(16, 185, 129, 0.25)";
    threatBadge.style.color = isSpam ? "#fca5a5" : "#6ee7b7";

    modelNameText.textContent = data.model_used || "Trained NLP Pipeline";

    // Animated Gauge Circle
    const score = Math.round(data.risk_score);
    riskScore.textContent = score;
    riskScore.style.color = isSpam ? "#f87171" : "#34d399";

    // Circumference = 2 * PI * 42 = 263.89
    const circumference = 264;
    const offset = circumference - (score / 100) * circumference;
    gaugeCircle.style.strokeDashoffset = offset;
    gaugeCircle.style.stroke = isSpam ? "#ef4444" : "#10b981";

    statusTag.textContent = isSpam ? "Threat Detected" : "Verified Clean";
    statusTag.style.color = isSpam ? "#f87171" : "#34d399";
    statusTag.style.borderColor = isSpam ? "rgba(239, 68, 68, 0.4)" : "rgba(16, 185, 129, 0.4)";

    // Progress Bars
    spamProbText.textContent = `${data.spam_probability}%`;
    spamBar.style.width = `${data.spam_probability}%`;

    hamProbText.textContent = `${data.ham_probability}%`;
    hamBar.style.width = `${data.ham_probability}%`;

    // Trigger Keywords
    triggersList.innerHTML = "";
    if (data.detected_triggers && data.detected_triggers.length > 0) {
      data.detected_triggers.forEach(word => {
        const badge = document.createElement("span");
        badge.className = "trigger-badge";
        badge.textContent = word;
        triggersList.appendChild(badge);
      });
    } else {
      triggersList.innerHTML = '<span class="clean-badge">Clean message — No high-risk phishing/spam keywords detected.</span>';
    }

    // Reasons List
    reasonsList.innerHTML = "";
    if (data.reasons && data.reasons.length > 0) {
      data.reasons.forEach(r => {
        const li = document.createElement("li");
        li.textContent = r;
        reasonsList.appendChild(li);
      });
    }

    // Add to Local Scan History
    addToHistory({
      id: Date.now(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      snippet: originalText.length > 45 ? originalText.substring(0, 45) + "..." : originalText,
      fullSubject: subjectInput.value.trim(),
      fullBody: emailInput.value.trim(),
      isSpam: isSpam,
      riskScore: score,
      confidence: `${data.confidence}%`
    });
  }

  // Copy Security Report
  btnCopyReport.addEventListener("click", () => {
    if (!currentAnalysisData) return;
    const d = currentAnalysisData;
    const report = `================================================
SPAMSHIELD AI - EMAIL SECURITY ASSESSMENT REPORT
================================================
Timestamp: ${new Date().toLocaleString()}
Verdict: ${d.label}
Risk Score: ${d.risk_score}/100
Threat Level: ${d.threat_level}
Spam Probability: ${d.spam_probability}%
Legitimate Probability: ${d.ham_probability}%
Triggers Detected: ${d.detected_triggers.join(", ") || "None"}
Insights:
${d.reasons.map(r => "- " + r).join("\n")}
================================================`;

    navigator.clipboard.writeText(report).then(() => {
      copyBtnText.textContent = "Report Copied to Clipboard!";
      setTimeout(() => {
        copyBtnText.textContent = "Copy Full Security Report";
      }, 2500);
    });
  });

  // Add To History Storage
  function addToHistory(entry) {
    scanHistory.unshift(entry);
    if (scanHistory.length > 30) scanHistory.pop();
    localStorage.setItem("spamshield_history", JSON.stringify(scanHistory));
  }

  // Check for Retest parameters from History Page
  function checkRetestParams() {
    const retestSub = localStorage.getItem("spamshield_retest_subject");
    const retestBody = localStorage.getItem("spamshield_retest_body");
    if (retestBody) {
      subjectInput.value = retestSub || "";
      emailInput.value = retestBody;
      updateWordCount();
      localStorage.removeItem("spamshield_retest_subject");
      localStorage.removeItem("spamshield_retest_body");
      // Auto analyze
      setTimeout(() => {
        form.dispatchEvent(new Event("submit"));
      }, 100);
    }
  }

  // Init
  loadStats();
  loadSamples();
  checkRetestParams();
});
