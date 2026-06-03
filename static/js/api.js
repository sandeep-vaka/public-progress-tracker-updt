
const API_BASE = "/api";

function getToken() { return localStorage.getItem("token"); }
function setToken(t) { localStorage.setItem("token", t); }
function clearToken() { localStorage.removeItem("token"); localStorage.removeItem("user"); }
function getUser() { return JSON.parse(localStorage.getItem("user") || "null"); }
function setUser(u) { localStorage.setItem("user", JSON.stringify(u)); }


/**
 * api.js
 * ──────
 * Thin client-side wrapper around the Progress Tracker REST API.
 *
 * Phase 1 changes
 * ───────────────
 * 1. ApiError class — extends Error with a `status` property so individual
 *    pages can branch on HTTP status code (e.g. 403 vs 401 in login).
 *
 * 2. request() now throws:
 *      new ApiError(data.message || data.error || "Request failed", res.status)
 *    Previously it only read data.error, so the 403 "Please verify your email"
 *    message (which the server puts in data.message) was silently swallowed
 *    and the UI showed the generic "Request failed" text.
 */

const API_BASE = "/api";

// ── Local-storage helpers (unchanged) ────────────────────────────────────────
function getToken() { return localStorage.getItem("token"); }
function setToken(t) { localStorage.setItem("token", t); }
function clearToken() { localStorage.removeItem("token"); localStorage.removeItem("user"); }
function getUser()  { return JSON.parse(localStorage.getItem("user") || "null"); }
function setUser(u) { localStorage.setItem("user", JSON.stringify(u)); }

// ── Phase 1: error class that carries the HTTP status code ────────────────────
class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name   = "ApiError";
    this.status = status;   // lets callers do: if (e.status === 403) { … }
  }
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;


  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

const api = {
  signup: (body) => request("/auth/signup", { method: "POST", body: JSON.stringify(body) }),
  login:  (body) => request("/auth/login",  { method: "POST", body: JSON.stringify(body) }),

  getMyProgress:    ()     => request("/progress/"),
  createProgress:   (body) => request("/progress/",    { method: "POST",   body: JSON.stringify(body) }),
  updateProgress:   (id, body) => request(`/progress/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteProgress:   (id)   => request(`/progress/${id}`, { method: "DELETE" }),
  getPublicProgress: ()    => request("/progress/public"),

  const res  = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json();

  // Phase 1: read data.message first (used by 403 verify-email barrier),
  // then data.error (used by all other error responses), then a fallback.
  if (!res.ok) throw new ApiError(data.message || data.error || "Request failed", res.status);
  return data;
}

// ── API surface (all existing methods unchanged) ──────────────────────────────
const api = {
  signup: (body)      => request("/auth/signup", { method: "POST", body: JSON.stringify(body) }),
  login:  (body)      => request("/auth/login",  { method: "POST", body: JSON.stringify(body) }),

  getMyProgress:     ()         => request("/progress/"),
  createProgress:    (body)     => request("/progress/",       { method: "POST",   body: JSON.stringify(body) }),
  updateProgress:    (id, body) => request(`/progress/${id}`,  { method: "PUT",    body: JSON.stringify(body) }),
  deleteProgress:    (id)       => request(`/progress/${id}`,  { method: "DELETE" }),
  getPublicProgress: ()         => request("/progress/public"),

};
