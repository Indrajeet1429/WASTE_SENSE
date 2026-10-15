// Member 3 (monitoring): "What is happening right now?"
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import StatCard from "../components/cards/StatCard";
import LineChart from "../components/charts/LineChart";
import BarChart from "../components/charts/BarChart";
import Meter from "../components/charts/Meter";
import DataTable from "../components/tables/DataTable";
import Badge from "../components/common/Badge";
import useApi from "../hooks/useApi";
import { getDashboard, getMachines, getTrends, getAlerts, getWasteEvents } from "../services/wastesenseService";
import { scoreColor } from "../utils/format";

const SEVS = ["critical", "high", "medium", "low"];

export default function Dashboard() {
  const state = useApi(async () => {
    const [d, m, t, a, e] = await Promise.all([getDashboard(), getMachines(), getTrends("24h"), getAlerts(), getWasteEvents()]);
    return { d, m, t, a, e };
  }, []);
  return (
    <>
      <PageHeader title="Dashboard" question="What is happening right now?" />
      <DataState state={state}>{({ d, m, t, a, e }) => {
        const on = m.filter((x) => x.status !== "offline");
        const avg = (k) => on.length ? Math.round(on.reduce((s, x) => s + x[k], 0) / on.length) : 0;
        return (
          <>
            <div className="cards">
              <StatCard label="Total machines" value={d.total_machines} hint={`${d.offline_machines ?? 1} offline`} />
              <StatCard label="Active workloads" value={d.active_workloads} hint="on online machines" />
              <StatCard label="Current waste events" value={d.current_waste_events} hint="detected in the last day" tone="a" />
              <StatCard label="Critical alerts" value={d.critical_alerts} hint="open now" tone="r" />
              <StatCard label="Average waste score" value={d.avg_waste_score} hint="online machines, 0 to 100" />
              <StatCard label="Estimated potential savings" value={`$${d.potential_savings.usd}`} hint="per month, not guaranteed" tone="g" />
            </div>
            <div className="g2">
              <Panel title="Waste score, last 24 hours" subtitle="Model output per hour">
                <LineChart sets={[{ name: "Waste score", data: t.waste_score, color: "var(--em)" }]} labels={t.labels} legend={false} />
              </Panel>
              <Panel title="Waste events by severity" subtitle="Current detections">
                <BarChart data={SEVS.map((s) => e.filter((x) => x.severity === s).length)} labels={["Critical", "High", "Medium", "Low"]}
                  color={["var(--crit)", "var(--high)", "var(--med)", "var(--low)"]} />
              </Panel>
            </div>
            <div className="g2">
              <Panel title="Resource usage" subtitle="Average across online machines">
                <div className="ea" style={{ gridTemplateColumns: "90px 1fr 60px" }}>
                  <span>CPU</span><div className="tr"><i className="ac" style={{ width: `${avg("cpu_usage")}%` }} /></div><b>{avg("cpu_usage")}%</b>
                  <span>Memory</span><div className="tr"><i className="ac" style={{ width: `${avg("memory_usage")}%` }} /></div><b>{avg("memory_usage")}%</b>
                  <span>Power</span><div className="tr"><i className="ac" style={{ width: `${Math.min(100, avg("power_watts") / 5)}%` }} /></div><b>{avg("power_watts")} W</b>
                </div>
              </Panel>
              <Panel title="Highest waste machines" subtitle="Ranked by waste score">
                <DataTable rowKey="machine_id" rows={[...m].sort((x, y) => y.waste_score - x.waste_score).slice(0, 5)} columns={[
                  { header: "Machine", cell: (x) => <Link to={`/machines/${x.machine_id}`}><b>{x.machine_id}</b> {x.name}</Link> },
                  { header: "Waste score", cell: (x) => <Meter value={x.waste_score} color={scoreColor(x.waste_score)} /> },
                  { header: "Status", cell: (x) => <Badge value={x.status} /> },
                ]} />
              </Panel>
            </div>
            <Panel title="Open alerts" subtitle="Most recent first">
              <DataTable rowKey="alert_id" rows={a.filter((x) => x.status === "open").slice(0, 5)} columns={[
                { header: "Machine", cell: (x) => x.machine_id },
                { header: "Severity", cell: (x) => <Badge value={x.severity} /> },
                { header: "Message", cell: (x) => x.message },
              ]} />
            </Panel>
          </>
        );
      }}</DataState>
    </>
  );
}
