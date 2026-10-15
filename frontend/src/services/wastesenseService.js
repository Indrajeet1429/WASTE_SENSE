// The only file pages use to get data. Mock vs FastAPI is decided here (VITE_USE_MOCK), so pages stay unchanged.
import { USE_MOCK } from "../api/apiClient";
import { machinesApi } from "../api/machines";
import { workloadsApi } from "../api/workloads";
import { measurementsApi } from "../api/measurements";
import { wasteEventsApi } from "../api/wasteEvents";
import { alertsApi } from "../api/alerts";
import { savingsApi } from "../api/savings";
import { replayResultsApi } from "../api/replayResults";
import { recommendationsApi } from "../api/recommendations";
import * as mock from "./mockData";
import { toMachine, toEvent, toAlert, toSavings, toOptimization, toTrends, latestBy, num } from "./adapters";

const mk = (v) => Promise.resolve(v());
const byWaste = (rows) => Object.fromEntries(rows.map((r) => [String(r.waste_id), r]));

// Loads every machine-level source once and returns the page-shaped machines.
async function loadMachines() {
  const [ms, meas, wl, ev] = await Promise.all([machinesApi.list(), measurementsApi.list(), workloadsApi.list(), wasteEventsApi.list()]);
  return { raw: ms, list: ms.map((m) => toMachine(m, { measurements: meas, workloads: wl, events: ev })), meas, wl, ev };
}
async function loadEvents() {
  const [ev, rp, sv, rc] = await Promise.all([wasteEventsApi.list(), replayResultsApi.list(), savingsApi.list(), recommendationsApi.list()]);
  const R = byWaste(rp), S = byWaste(sv), C = byWaste(rc);
  return { list: ev.map((e) => toEvent(e, { replay: R[e.waste_id], saving: S[e.waste_id], recommendation: C[e.waste_id] })), replays: rp, savings: sv, recs: rc };
}
const eventsById = (list) => Object.fromEntries(list.map((e) => [e.waste_id, e]));
const sortNew = (a, b) => new Date(b.timestamp) - new Date(a.timestamp);

export const getMachines = () => (USE_MOCK ? mk(() => mock.MACHINES) : loadMachines().then((d) => d.list));

export const getMachine = async (id) => {
  if (USE_MOCK) return mk(() => mock.machine(id));
  const raw = await machinesApi.get(id);
  const [meas, wl, ev] = await Promise.all([measurementsApi.list({ machine_id: id }), workloadsApi.list({ machine_id: id }), wasteEventsApi.list({ machine_id: id })]);
  const m = toMachine(raw, { measurements: meas, workloads: wl, events: ev });
  const h = [...meas].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)).slice(-24);
  const series = (k) => ({ actual: h.map((x) => num(x[k]) ?? 0), expected: [] });
  return {
    ...m, labels: h.map((x) => new Date(x.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })),
    cpu_history: series("actual_cpu"), memory_history: series("actual_memory"), power_history: series("actual_power"),
    recent_events: ev.map((e) => toEvent(e)).sort(sortNew),
  };
};

export const getAlerts = async () => {
  if (USE_MOCK) return mk(() => mock.ALERTS);
  const [al, ev] = await Promise.all([alertsApi.list(), wasteEventsApi.list()]);
  const E = eventsById(ev.map((e) => toEvent(e)));
  return al.map((a) => toAlert(a, E)).sort(sortNew);
};
export const updateAlertStatus = async (id, status) => {
  if (USE_MOCK) { const a = mock.ALERTS.find((x) => x.alert_id === id); if (a) a.status = status; return a; }
  return alertsApi.updateStatus(id, status);
};

export const getWasteEvents = () => (USE_MOCK ? mk(() => mock.EVENTS) : loadEvents().then((d) => d.list));
export const getWasteEvent = async (id) => {
  if (USE_MOCK) return mk(() => mock.wasteEvent(id));
  const [e, rp, sv, rc] = await Promise.all([wasteEventsApi.get(id), replayResultsApi.list({ waste_id: id }), savingsApi.list({ waste_id: id }), recommendationsApi.list({ waste_id: id })]);
  return toEvent(e, { replay: rp[0], saving: sv[0], recommendation: rc[0] });
};

export const getSavings = async () => {
  if (USE_MOCK) return mk(mock.savings);
  const [sv, ev] = await Promise.all([savingsApi.list(), wasteEventsApi.list()]);
  return toSavings(sv, eventsById(ev.map((e) => toEvent(e))));
};
export const getOptimization = async () => {
  if (USE_MOCK) return mk(() => mock.OPTIMIZATION);
  const [rc, ev] = await Promise.all([recommendationsApi.list(), wasteEventsApi.list()]);
  return toOptimization(rc, eventsById(ev.map((e) => toEvent(e))));
};

export const getTrends = async (range) => {
  if (USE_MOCK) return mk(() => mock.trends(range));
  const [ev, rp] = await Promise.all([wasteEventsApi.list(), replayResultsApi.list()]);
  return toTrends(range, ev, rp);
};

export const getDashboard = async () => {
  if (USE_MOCK) return mk(mock.dashboard);
  const [m, al, sv, ev] = await Promise.all([loadMachines(), alertsApi.list(), savingsApi.list(), wasteEventsApi.list()]);
  const on = m.list.filter((x) => x.status !== "offline");
  const dayAgo = Date.now() - 864e5;
  const recent = ev.filter((e) => new Date(e.timestamp).getTime() >= dayAgo);
  const t = toSavings(sv, {}).totals;
  return {
    total_machines: m.list.length, offline_machines: m.list.length - on.length,
    active_workloads: on.reduce((a, x) => a + x.active_workloads, 0), current_waste_events: recent.length,
    critical_alerts: al.filter((a) => a.severity === "critical" && a.status === "open").length,
    avg_waste_score: on.length ? Math.round((on.reduce((a, x) => a + x.waste_score, 0) / on.length) * 10) / 10 : 0, potential_savings: t,
  };
};
