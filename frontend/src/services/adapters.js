// Maps FastAPI responses (docs: WASTESENSE Frontend Integration Specification) to the shapes the pages use.
// Read responses may carry numbers as strings, so everything numeric goes through num().
export const num = (v) => { const n = Number(v); return Number.isFinite(n) ? n : null; };
const r1 = (v) => (v === null ? null : Math.round(v * 10) / 10);
const sid = (v) => String(v);
export const latestBy = (rows, key, ts = "timestamp") =>
  rows.reduce((m, r) => { const k = sid(r[key]); if (!m[k] || new Date(r[ts]) > new Date(m[k][ts])) m[k] = r; return m; }, {});

const scoreStatus = (s) => (s >= 70 ? "critical" : s >= 40 ? "warning" : "healthy");

// Machine status: inactive/maintenance show as offline, otherwise derived from the latest waste score.
export function toMachine(m, { measurements = [], workloads = [], events = [] } = {}) {
  const id = sid(m.machine_id);
  const meas = latestBy(measurements.filter((x) => sid(x.machine_id) === id), "machine_id")[id];
  const ev = latestBy(events.filter((x) => sid(x.machine_id) === id), "machine_id")[id];
  const score = ev ? num(ev.waste_score) ?? 0 : 0;
  return {
    machine_id: id, name: m.machine_name, cpu_usage: meas ? num(meas.actual_cpu) ?? 0 : 0,
    memory_usage: meas ? num(meas.actual_memory) ?? 0 : 0, power_watts: meas ? num(meas.actual_power) ?? 0 : 0,
    active_workloads: workloads.filter((w) => sid(w.machine_id) === id && !w.end_time).length,
    waste_score: score, status: m.status === "active" ? scoreStatus(score) : "offline", raw_status: m.status,
  };
}

// Waste event merged with its replay result, savings record and recommendation (all optional).
export function toEvent(e, { replay, saving, recommendation } = {}) {
  const a = { cpu: num(replay?.actual_cpu), pw: num(replay?.actual_power) };
  const x = { cpu: num(replay?.expected_cpu), pw: num(replay?.expected_power) };
  const diff = (p, q) => (p !== null && q !== null ? r1(p - q) : null);
  return {
    waste_id: sid(e.waste_id), machine_id: sid(e.machine_id), workload_id: sid(e.workload_id), timestamp: e.timestamp,
    waste_score: num(e.waste_score) ?? 0, severity: e.severity, waste_type: e.waste_type, persistence: !!e.persistent,
    confidence: Math.round((num(e.confidence) ?? 0) * 100),
    actual_cpu: a.cpu, expected_cpu: x.cpu, cpu_excess: diff(a.cpu, x.cpu),
    actual_memory: null, expected_memory: null, memory_excess: null,
    actual_power: a.pw, expected_power: x.pw, power_excess: diff(a.pw, x.pw),
    contributing_factors: [], has_replay: !!replay, estimated_saving: num(replay?.estimated_saving),
    savings: saving ? { cpu_cores: num(saving.cpu_saving), memory_gb: num(saving.memory_saving), power_w: num(saving.power_saving), cost_usd_month: num(saving.cost_saving) } : null,
    recommendation: recommendation || null,
  };
}

export const toAlert = (a, eventsById) => ({
  alert_id: sid(a.alert_id), waste_id: sid(a.waste_id), machine_id: eventsById[sid(a.waste_id)]?.machine_id ?? "-",
  timestamp: a.created_at || a.timestamp || eventsById[sid(a.waste_id)]?.timestamp, severity: a.severity, message: a.message, status: a.status,
});

const sum = (rows, k) => r1(rows.reduce((t, r) => t + (num(r[k]) ?? 0), 0));
export const toSavings = (rows, eventsById) => ({
  totals: { cpu: sum(rows, "cpu_saving"), mem: sum(rows, "memory_saving"), pw: sum(rows, "power_saving"), usd: sum(rows, "cost_saving") },
  by_event: rows.map((s) => ({
    waste_id: sid(s.waste_id), machine_id: eventsById[sid(s.waste_id)]?.machine_id ?? "-",
    cpu_cores: num(s.cpu_saving), memory_gb: num(s.memory_saving), power_w: num(s.power_saving), cost_usd_month: num(s.cost_saving),
  })),
});

export const toOptimization = (rows, eventsById) => rows.map((r) => ({
  machine_id: eventsById[sid(r.waste_id)]?.machine_id ?? "-", waste_id: sid(r.waste_id), resource: r.resource,
  current: num(r.current_value), suggested: num(r.suggested_value), estimated_benefit: num(r.estimated_benefit), reason: r.recommendation,
}));

const RANGES = { "1h": [12, 3600e3], "6h": [12, 6 * 3600e3], "24h": [24, 24 * 3600e3], "7d": [7, 7 * 24 * 3600e3] };
// Buckets waste events (and replay results, for CPU/power waste) over the selected range, ending now.
export function toTrends(range, events, replays) {
  const [n, span] = RANGES[range], end = Date.now(), step = span / n;
  const buckets = Array.from({ length: n }, () => ({ s: [], c: [], p: [] }));
  const rp = Object.fromEntries(replays.map((r) => [sid(r.waste_id), r]));
  events.forEach((e) => {
    const i = Math.floor((new Date(e.timestamp).getTime() - (end - span)) / step);
    if (i < 0 || i >= n) return;
    buckets[i].s.push(num(e.waste_score) ?? 0);
    const r = rp[sid(e.waste_id)], ac = num(r?.actual_cpu), ec = num(r?.expected_cpu), ap = num(r?.actual_power), ep = num(r?.expected_power);
    if (ac) buckets[i].c.push(Math.max(0, ((ac - ec) / ac) * 100));
    if (ap) buckets[i].p.push(Math.max(0, ((ap - ep) / ap) * 100));
  });
  const avg = (a) => (a.length ? r1(a.reduce((t, v) => t + v, 0) / a.length) : 0);
  return {
    range, labels: buckets.map((_, i) => { const d = new Date(end - span + step * (i + 1)); return range === "7d" ? d.toLocaleDateString([], { month: "short", day: "numeric" }) : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }),
    waste_score: buckets.map((b) => avg(b.s)), waste_event_count: buckets.map((b) => b.s.length),
    cpu_waste: buckets.map((b) => avg(b.c)), power_waste: buckets.map((b) => avg(b.p)), memory_waste: null,
  };
}
