# WasteSense API contract (frontend draft)

This is the shape the frontend mock data uses (`js/data/mock.js`). It is a DRAFT: reconcile it with the team's
agreed `docs/interfaces.md` before connecting. Do not rename fields in the UI; change the contract with team approval.
All routes are under `/api/v1` and return JSON. Send `Authorization: Bearer <token>` once auth exists.

| Route | Returns |
|---|---|
| `GET /dashboard` | `total_machines, active_workloads, current_waste_events, critical_alerts, avg_waste_score, potential_savings{cpu, mem, pw, usd}` |
| `GET /machines` | list of `machine_id, name, cpu_usage, memory_usage, power_watts, active_workloads, waste_score, status` (healthy, warning, critical, offline) |
| `GET /machines/{id}` | machine fields plus `labels[]`, `cpu_history{actual[], expected[]}`, `memory_history`, `power_history`, `recent_events[]` |
| `GET /trends?range=1h\|6h\|24h\|7d` | `labels[], waste_score[], cpu_waste[], memory_waste[], power_waste[], waste_event_count[]` |
| `GET /alerts` | list of `alert_id, machine_id, timestamp, severity (critical, high, medium, low), message, status (open, acknowledged, resolved)` |
| `GET /waste-events` | list of waste events (below) |
| `GET /waste-events/{id}` | one waste event |
| `GET /optimization` | list of `machine_id, resource, current, suggested, estimated_benefit, reason` |
| `GET /savings` | `totals{cpu, mem, pw, usd}`, `by_event[]{waste_id, machine_id, cpu_cores, memory_gb, power_w, cost_usd_month}` |

Waste event: `waste_id, machine_id, timestamp (ISO 8601), waste_score, severity, waste_type, persistence (bool), confidence (0-100),
actual_cpu, expected_cpu, cpu_excess, actual_memory, expected_memory, memory_excess, actual_power, expected_power, power_excess,
contributing_factors[], savings{cpu_cores, memory_gb, power_w, cost_usd_month}`.

Rules: the UI never computes waste intelligence (scores, excess, savings, confidence); it only displays what the API returns.
Replay and savings are model-based estimates and are labelled that way.
