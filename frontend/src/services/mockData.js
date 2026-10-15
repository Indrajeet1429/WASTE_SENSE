// MOCK DATA ONLY. Shapes follow docs/interfaces.md. Never present this as real production data.
const rng = (s) => () => (s = (s * 16807) % 2147483647) / 2147483647;
const ser = (seed, base, amp, n) => {
  const r = rng(seed * 97 + 13);
  return Array.from({ length: n }, (_, i) => +(base + Math.sin(i / 3 + seed) * amp + (r() - 0.5) * amp).toFixed(1));
};
export const MACHINES = [
  ["M-01", "NODE-PRD-A", 78, 71, 342, 18, 22, "healthy"], ["M-02", "NODE-PRD-B", 81, 58, 365, 6, 74, "critical"],
  ["M-03", "NODE-DB2", 64, 83, 288, 12, 31, "healthy"], ["M-04", "NODE-BATCH", 92, 66, 401, 4, 68, "warning"],
  ["M-05", "NODE-DEV", 38, 44, 190, 9, 55, "warning"], ["M-06", "NODE-ANALYTICS", 55, 49, 240, 7, 47, "healthy"],
  ["M-07", "NODE-TEST", 22, 31, 150, 2, 61, "warning"], ["M-08", "NODE-DR", 0, 0, 0, 0, 0, "offline"],
].map((a) => ({ machine_id: a[0], name: a[1], cpu_usage: a[2], memory_usage: a[3], power_watts: a[4], active_workloads: a[5], waste_score: a[6], status: a[7] }));
const FACTORS = {
  "CPU Inefficiency": ["High CPU per task", "Low active task count", "Sustained workload duration"],
  "Batch Over-Allocation": ["Allocated cores exceed demand", "Job window shorter than reservation", "Idle threads after batch completes"],
  "Idle Memory Retention": ["Memory held with no active tasks", "Long-lived cached pages", "Low request rate"],
  "Power Overdraw": ["Power draw above expected for load", "Frequency scaling not engaged", "Low utilisation at high wattage"],
  "Transient Spike": ["Short-lived load burst", "No persistence across windows", "Within normal variance"],
};
const ev = (id, m, ts, sc, sev, type, per, conf, c, me, p, sv) => ({
  waste_id: id, machine_id: m, timestamp: ts, waste_score: sc, severity: sev, waste_type: type, persistence: per, confidence: conf,
  actual_cpu: c[0], expected_cpu: c[1], cpu_excess: c[0] - c[1], actual_memory: me[0], expected_memory: me[1], memory_excess: me[0] - me[1],
  actual_power: p[0], expected_power: p[1], power_excess: p[0] - p[1], contributing_factors: FACTORS[type],
  savings: { cpu_cores: sv[0], memory_gb: sv[1], power_w: sv[2], cost_usd_month: sv[3] },
});
export const EVENTS = [
  ev("W-1001", "M-02", "2026-10-13T09:42:00Z", 74, "critical", "CPU Inefficiency", true, 91, [81, 38], [58, 45], [365, 290], [3, 12, 75, 54]),
  ev("W-1002", "M-04", "2026-10-13T09:10:00Z", 68, "high", "Batch Over-Allocation", true, 86, [92, 55], [66, 50], [401, 330], [4, 16, 71, 51]),
  ev("W-1003", "M-07", "2026-10-13T08:35:00Z", 61, "high", "Idle Memory Retention", true, 79, [22, 18], [31, 12], [150, 120], [1, 19, 30, 22]),
  ev("W-1004", "M-05", "2026-10-13T07:50:00Z", 55, "medium", "Power Overdraw", false, 72, [38, 30], [44, 36], [190, 150], [1, 8, 40, 29]),
  ev("W-1005", "M-06", "2026-10-13T06:20:00Z", 47, "medium", "CPU Inefficiency", false, 68, [55, 42], [49, 40], [240, 205], [2, 9, 35, 25]),
  ev("W-1006", "M-01", "2026-10-12T22:05:00Z", 22, "low", "Transient Spike", false, 64, [78, 70], [71, 66], [342, 330], [0, 5, 12, 9]),
];
export const ALERTS = [
  ["A-301", "M-02", "2026-10-13T09:43:00Z", "critical", "Sustained CPU waste above expected baseline", "open"],
  ["A-300", "M-04", "2026-10-13T09:12:00Z", "high", "Batch machine over-allocated against observed demand", "open"],
  ["A-299", "M-07", "2026-10-13T08:36:00Z", "high", "Memory retained with no active workloads", "acknowledged"],
  ["A-298", "M-05", "2026-10-13T07:52:00Z", "medium", "Power draw 26% above expected", "open"],
  ["A-297", "M-06", "2026-10-13T06:21:00Z", "medium", "CPU waste persisted for 2 windows", "acknowledged"],
  ["A-296", "M-01", "2026-10-12T22:06:00Z", "low", "Short CPU spike, within tolerance", "resolved"],
  ["A-295", "M-08", "2026-10-12T18:00:00Z", "medium", "Machine offline, telemetry missing", "open"],
  ["A-294", "M-02", "2026-10-12T14:20:00Z", "critical", "Power overdraw during low load", "resolved"],
].map((a) => ({ alert_id: a[0], machine_id: a[1], timestamp: a[2], severity: a[3], message: a[4], status: a[5] }));
export const OPTIMIZATION = [
  ["M-02", "CPU cores", 8, 5, "about 75 W", "Workload demand has stayed below allocated capacity."],
  ["M-04", "CPU cores", 16, 10, "about 71 W", "Batch window uses under 60% of reserved cores."],
  ["M-07", "Memory GB", 32, 13, "about 19 GB freed", "Memory is held with very few active tasks."],
  ["M-05", "Power cap W", 220, 185, "about 40 W", "Draw is above the level expected for current load."],
  ["M-06", "CPU cores", 8, 6, "about 35 W", "Moderate, persistent over-provisioning."],
].map((a) => ({ machine_id: a[0], resource: a[1], current: a[2], suggested: a[3], estimated_benefit: a[4], reason: a[5] }));
const RANGES = { "1h": [12, "5m"], "6h": [12, "30m"], "24h": [24, "1h"], "7d": [7, "1d"] };

export const savings = () => {
  const totals = EVENTS.reduce((a, e) => ({ cpu: a.cpu + e.savings.cpu_cores, mem: a.mem + e.savings.memory_gb, pw: a.pw + e.savings.power_w, usd: a.usd + e.savings.cost_usd_month }), { cpu: 0, mem: 0, pw: 0, usd: 0 });
  return { totals, by_event: EVENTS.map((e) => ({ waste_id: e.waste_id, machine_id: e.machine_id, ...e.savings })) };
};
export const dashboard = () => {
  const on = MACHINES.filter((m) => m.status !== "offline");
  return {
    total_machines: MACHINES.length, active_workloads: MACHINES.reduce((a, m) => a + m.active_workloads, 0),
    current_waste_events: EVENTS.length, critical_alerts: ALERTS.filter((a) => a.severity === "critical" && a.status === "open").length,
    avg_waste_score: +(on.reduce((a, m) => a + m.waste_score, 0) / on.length).toFixed(1), potential_savings: savings().totals,
  };
};
export const machine = (id) => {
  const m = MACHINES.find((x) => x.machine_id === id);
  if (!m) return null;
  const i = MACHINES.indexOf(m) + 1, n = 24;
  return {
    ...m, labels: Array.from({ length: n }, (_, k) => `${k}:00`),
    cpu_history: { actual: ser(i, m.cpu_usage, 8, n), expected: ser(i + 50, m.cpu_usage * 0.55, 3, n) },
    memory_history: { actual: ser(i + 1, m.memory_usage, 5, n), expected: ser(i + 51, m.memory_usage * 0.8, 2, n) },
    power_history: { actual: ser(i + 2, m.power_watts, 14, n), expected: ser(i + 52, m.power_watts * 0.82, 5, n) },
    recent_events: EVENTS.filter((e) => e.machine_id === id),
  };
};
export const trends = (range = "24h") => {
  const [n, u] = RANGES[range], s = range.length + n;
  return {
    range, labels: Array.from({ length: n }, (_, k) => (range === "7d" ? `Day ${k + 1}` : u === "1h" ? `${k}:00` : `${k + 1}/${n}`)),
    waste_score: ser(s, 48, 10, n), cpu_waste: ser(s + 1, 30, 8, n), memory_waste: ser(s + 2, 18, 6, n), power_waste: ser(s + 3, 24, 7, n),
    waste_event_count: ser(s + 4, 4, 3, n).map((v) => Math.max(0, Math.round(v))),
  };
};
export const wasteEvent = (id) => EVENTS.find((e) => e.waste_id === id) || null;
