// JobMatch AI — Chrome Extension Side Panel Logic

const CLOUD_URL = "https://jobmatch-ai-cp3l.onrender.com";
const LOCAL_URL = "http://127.0.0.1:8000";

let currentServerUrl = CLOUD_URL;
let cachedResumeText = "";
let latestMatchData = null;
let latestTailorData = null;

// DOM Elements
const serverToggle = document.getElementById("serverToggle");
const serverDot = document.getElementById("serverDot");
const serverLabel = document.getElementById("serverLabel");
const statusAlert = document.getElementById("statusAlert");

const btnExtractTab = document.getElementById("btnExtractTab");
const txtJobDescription = document.getElementById("txtJobDescription");
const jobMetaTitle = document.getElementById("jobMetaTitle");
const jobMetaLength = document.getElementById("jobMetaLength");
const btnAnalyze = document.getElementById("btnAnalyze");

const resultsSection = document.getElementById("resultsSection");
const gaugeCircle = document.getElementById("gaugeCircle");
const scorePercentage = document.getElementById("scorePercentage");
const matchBadge = document.getElementById("matchBadge");
const skillCoverageText = document.getElementById("skillCoverageText");
const semanticText = document.getElementById("semanticText");
const matchedList = document.getElementById("matchedList");
const missingList = document.getElementById("missingList");
const matchedCount = document.getElementById("matchedCount");
const missingCount = document.getElementById("missingCount");
const btnAutoTailor = document.getElementById("btnAutoTailor");

const tailorSection = document.getElementById("tailorSection");
const projectedScoreText = document.getElementById("projectedScoreText");
const deltaBadge = document.getElementById("deltaBadge");
const injectedList = document.getElementById("injectedList");
const injectedCount = document.getElementById("injectedCount");
const btnDownloadPdf = document.getElementById("btnDownloadPdf");
const btnCopyDm = document.getElementById("btnCopyDm");
const btnCopyLatex = document.getElementById("btnCopyLatex");

// 1. Initialize
document.addEventListener("DOMContentLoaded", async () => {
  // Load saved preferences
  const stored = await chrome.storage.local.get(["serverUrl", "resumeText"]);
  if (stored.serverUrl) {
    currentServerUrl = stored.serverUrl;
  }
  updateServerUI();

  if (stored.resumeText) {
    cachedResumeText = stored.resumeText;
  } else {
    await fetchResume();
  }

  setupEventListeners();
});

function updateServerUI() {
  const isCloud = currentServerUrl === CLOUD_URL;
  serverLabel.textContent = isCloud ? "Cloud" : "Local";
  serverDot.style.background = isCloud ? "#10b981" : "#3b82f6";
  serverDot.style.boxShadow = isCloud ? "0 0 6px #10b981" : "0 0 6px #3b82f6";
}

async function fetchResume() {
  try {
    const res = await fetch(`${currentServerUrl}/api/default-resume`);
    const data = await res.json();
    if (data.success && data.text) {
      cachedResumeText = data.text;
      await chrome.storage.local.set({ resumeText: data.text });
    }
  } catch (err) {
    console.warn("Could not fetch default resume from server:", err);
  }
}

function showStatus(message, type = "success", timeout = 3500) {
  statusAlert.textContent = message;
  statusAlert.className = `status-msg status-${type}`;
  statusAlert.classList.remove("hidden");
  if (timeout > 0) {
    setTimeout(() => {
      statusAlert.classList.add("hidden");
    }, timeout);
  }
}

// 2. Setup Event Listeners
function setupEventListeners() {
  // Toggle Cloud / Localhost
  serverToggle.addEventListener("click", async () => {
    currentServerUrl = currentServerUrl === CLOUD_URL ? LOCAL_URL : CLOUD_URL;
    await chrome.storage.local.set({ serverUrl: currentServerUrl });
    updateServerUI();
    showStatus(`Switched backend to ${serverLabel.textContent}`);
    await fetchResume();
  });

  // Extract from active tab
  btnExtractTab.addEventListener("click", extractFromActiveTab);

  // Analyze Match
  btnAnalyze.addEventListener("click", runMatchAnalysis);

  // Auto-Tailor
  btnAutoTailor.addEventListener("click", runAutoTailor);

  // Download PDF
  btnDownloadPdf.addEventListener("click", downloadTailoredPdf);

  // Copy Recruiter DM
  btnCopyDm.addEventListener("click", () => {
    const dm = (latestTailorData && latestTailorData.recruiter_dm) || (latestMatchData && latestMatchData.recruiter_dm);
    if (!dm) {
      showStatus("Please run analysis first to generate DM", "error");
      return;
    }
    navigator.clipboard.writeText(dm);
    showStatus("📋 Recruiter DM copied to clipboard!");
  });

  // Copy Overleaf LaTeX
  btnCopyLatex.addEventListener("click", () => {
    if (!latestTailorData || !latestTailorData.tailored_latex) {
      showStatus("Please click Auto-Tailor first to get LaTeX", "error");
      return;
    }
    navigator.clipboard.writeText(latestTailorData.tailored_latex);
    showStatus("📋 Tailored LaTeX copied for Overleaf!");
  });

  // Word count update
  txtJobDescription.addEventListener("input", () => {
    const words = txtJobDescription.value.trim().split(/\s+/).filter(Boolean).length;
    jobMetaLength.textContent = `${words} words`;
  });
}

// 3. Extract Job Description from Active Tab
async function extractFromActiveTab() {
  btnExtractTab.disabled = true;
  btnExtractTab.innerHTML = "<span>⏳ Extracting from Tab...</span>";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) {
      throw new Error("No active tab detected");
    }

    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content-scraper.js"]
    });

    if (results && results[0] && results[0].result) {
      const data = results[0].result;
      if (data.text && data.text.length > 30) {
        txtJobDescription.value = data.text;
        const words = data.text.split(/\s+/).filter(Boolean).length;
        jobMetaLength.textContent = `${words} words`;

        const titleDisplay = [data.title, data.company].filter(Boolean).join(" • ");
        jobMetaTitle.textContent = titleDisplay.slice(0, 38) || "Extracted Job Description";

        showStatus(`✨ Extracted ${words} words from ${data.source}`);
        // Scroll to analyze button
        btnAnalyze.scrollIntoView({ behavior: "smooth" });
      } else {
        showStatus("Could not find job text. You can paste it manually.", "error");
      }
    } else {
      showStatus("Could not access page content. Please paste manually.", "error");
    }
  } catch (err) {
    showStatus(`Extraction failed: ${err.message}`, "error");
  } finally {
    btnExtractTab.disabled = false;
    btnExtractTab.innerHTML = "<span>⚡ 1-Click Extract from Active Tab</span>";
  }
}

// 4. Run Match Analysis
async function runMatchAnalysis() {
  const jdText = txtJobDescription.value.trim();
  if (!jdText) {
    showStatus("Please extract or paste a job description first.", "error");
    return;
  }

  if (!cachedResumeText) {
    await fetchResume();
  }

  btnAnalyze.disabled = true;
  btnAnalyze.innerHTML = "<span>⏳ Calculating ATS Score...</span>";

  try {
    const res = await fetch(`${currentServerUrl}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: cachedResumeText,
        jd_text: jdText
      })
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    latestMatchData = data;
    renderMatchResults(data);
  } catch (err) {
    showStatus(`Analysis failed: ${err.message}`, "error");
  } finally {
    btnAnalyze.disabled = false;
    btnAnalyze.innerHTML = "<span>🔍 Run ATS Match Analysis</span>";
  }
}

// 5. Render Match Results
function renderMatchResults(data) {
  resultsSection.classList.remove("hidden");

  // Score Gauge
  const score = Math.round(data.ats_score);
  scorePercentage.textContent = `${score}%`;

  const circumference = 2 * Math.PI * 36; // 226.19
  const offset = circumference - (score / 100) * circumference;
  gaugeCircle.style.strokeDashoffset = offset;

  if (score >= 85) {
    gaugeCircle.style.stroke = "#10b981"; // Emerald
  } else if (score >= 70) {
    gaugeCircle.style.stroke = "#3b82f6"; // Blue
  } else {
    gaugeCircle.style.stroke = "#f59e0b"; // Amber
  }

  matchBadge.textContent = data.rating || "Score Calculated";
  skillCoverageText.textContent = `${Math.round(data.skill_coverage_score)}%`;
  semanticText.textContent = `${Math.round(data.semantic_score)}%`;

  // Matched Skills
  matchedCount.textContent = data.matched_skills.length;
  matchedList.innerHTML = data.matched_skills.length > 0
    ? data.matched_skills.map(s => `<span class="tag tag-matched">${s}</span>`).join("")
    : `<span style="color:#64748b; font-size:10px;">None detected</span>`;

  // Missing Skills
  missingCount.textContent = data.missing_skills.length;
  missingList.innerHTML = data.missing_skills.length > 0
    ? data.missing_skills.map(s => `<span class="tag tag-missing">${s}</span>`).join("")
    : `<span style="color:#34d399; font-size:10px;">✨ Zero critical gaps!</span>`;

  resultsSection.scrollIntoView({ behavior: "smooth" });
}

// 6. Run Auto-Tailor
async function runAutoTailor() {
  const jdText = txtJobDescription.value.trim();
  if (!jdText) return;

  btnAutoTailor.disabled = true;
  btnAutoTailor.innerHTML = "<span>⏳ Tailoring Resume...</span>";

  try {
    const res = await fetch(`${currentServerUrl}/api/tailor`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: cachedResumeText,
        jd_text: jdText
      })
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    latestTailorData = data;
    renderTailorResults(data);
  } catch (err) {
    showStatus(`Tailoring failed: ${err.message}`, "error");
  } finally {
    btnAutoTailor.disabled = false;
    btnAutoTailor.innerHTML = "<span>✨ Auto-Tailor Master Resume</span>";
  }
}

// 7. Render Tailor Results
function renderTailorResults(data) {
  tailorSection.classList.remove("hidden");

  const proj = Math.round(data.projected_score);
  projectedScoreText.textContent = `${proj}% ATS Match`;

  const delta = data.score_delta;
  if (!data.injected_skills || data.injected_skills.length === 0 || delta === 0) {
    deltaBadge.textContent = "Already Fully Optimized";
    deltaBadge.style.background = "rgba(16, 185, 129, 0.15)";
    deltaBadge.style.color = "#34d399";
  } else {
    deltaBadge.textContent = `+${delta}% Boost`;
    deltaBadge.style.background = "rgba(59, 130, 246, 0.2)";
    deltaBadge.style.color = "#60a5fa";
  }

  injectedCount.textContent = `${data.injected_skills ? data.injected_skills.length : 0} keywords added`;
  if (data.injected_skills && data.injected_skills.length > 0) {
    injectedList.innerHTML = data.injected_skills
      .map(item => `<span class="tag tag-injected">+ ${item.skill || item}</span>`)
      .join("");
  } else {
    injectedList.innerHTML = `<span style="color:#34d399; font-size:10px;">✨ Master resume already contains all required technical skills.</span>`;
  }

  tailorSection.scrollIntoView({ behavior: "smooth" });
}

// 8. Download PDF Directly
async function downloadTailoredPdf() {
  btnDownloadPdf.disabled = true;
  btnDownloadPdf.innerHTML = "<span>⏳ Downloading PDF...</span>";

  try {
    const downloadUrl = `${currentServerUrl}/api/download-tailored-pdf`;
    
    // Use Chrome Downloads API if available
    if (chrome.downloads && chrome.downloads.download) {
      await chrome.downloads.download({
        url: downloadUrl,
        filename: "VenuGopalReddy_Tailored_Resume.pdf",
        saveAs: false
      });
      showStatus("📥 Downloaded tailored PDF to Downloads folder!");
    } else {
      // Fallback anchor download
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "VenuGopalReddy_Tailored_Resume.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showStatus("📥 Downloading PDF...");
    }
  } catch (err) {
    showStatus(`Download failed: ${err.message}`, "error");
  } finally {
    btnDownloadPdf.disabled = false;
    btnDownloadPdf.innerHTML = "<span>📥 Download Tailored 1-Page PDF</span>";
  }
}
