// Shared API client (per WASTESENSE Frontend Integration Specification).
// Paths include the /api/v1 prefix. Leave VITE_API_BASE_URL empty to use the Vite dev proxy,
// or set it to e.g. http://127.0.0.1:8000 to call FastAPI directly (backend CORS must allow it).
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
let token = null;
export const setToken = (t) => { token = t; };

export class ApiError extends Error {
  constructor(status, message, detail) { super(message); this.status = status; this.detail = detail; }
}

// Turns a FastAPI 422 `detail` array into { field: message } for forms.
export const fieldErrors = (err) =>
  Array.isArray(err?.detail) ? Object.fromEntries(err.detail.map((d) => [String(d.loc?.slice(-1)[0]), d.msg])) : {};

export const toQuery = (params = {}) => {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== "") q.set(k, String(v)); });
  const s = q.toString();
  return s ? `?${s}` : "";
};

export async function apiRequest(path, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (res.status === 204) return null;
  const isJson = (res.headers.get("content-type") || "").includes("application/json");
  const data = isJson ? await res.json() : await res.text();
  if (!res.ok) {
    const detail = typeof data === "object" && data !== null ? data.detail ?? data.message : data;
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join("; ") : detail;
    throw new ApiError(res.status, `API ${res.status}: ${msg || res.statusText}`, detail);
  }
  return data;
}
