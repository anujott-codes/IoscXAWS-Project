const API = "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}
async function checkApiStatus() {
  const el = document.getElementById("apiStatus");
  try {
    await fetch(API + "/");
    el.className = "api-status online";
    el.querySelector(".status-text").textContent = "API Online";
  } catch {
    el.className = "api-status offline";
    el.querySelector(".status-text").textContent = "API Offline";
  }
}

checkApiStatus();

function showAlert(containerId, message, type = "success") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { el.innerHTML = ""; }, 4000);
}

function boolDisplay(val) {
  return val
    ? '<span class="bool-yes">✓ Yes</span>'
    : '<span class="bool-no">— No</span>';
}