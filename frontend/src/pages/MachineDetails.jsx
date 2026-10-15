// Member 3 (monitoring)
import { Link, useNavigate, useParams } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import StatCard from "../components/cards/StatCard";
import LineChart from "../components/charts/LineChart";
import DataTable from "../components/tables/DataTable";
import Badge from "../components/common/Badge";
import useApi from "../hooks/useApi";
import { getMachine, getMachines } from "../services/wastesenseService";
import { formatDateTime } from "../utils/format";

export default function MachineDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const state = useApi(async () => ({ m: await getMachine(id), all: await getMachines() }), [id]);
  return (
    <DataState state={state}>{({ m, all }) => {
      if (!m) return <PageHeader title="Machine not found" question="That machine ID does not exist."><Link className="btn sm" to="/machines">Back to machines</Link></PageHeader>;
      const chart = (title, h, unit) => (
        <Panel title={title} subtitle={`Measured, latest readings (${unit})`}>
          <LineChart labels={m.labels} sets={[{ name: "Actual", data: h.actual, color: "var(--em)" }, ...(h.expected.length ? [{ name: "Expected", data: h.expected, color: "var(--hatch)", dash: true }] : [])]} />
        </Panel>
      );
      return (
        <>
          <PageHeader title={`${m.machine_id} ${m.name}`} question="Current load, history and recent waste">
            <select value={m.machine_id} onChange={(e) => navigate(`/machines/${e.target.value}`)} aria-label="Switch machine">
              {all.map((x) => <option key={x.machine_id} value={x.machine_id}>{x.machine_id} {x.name}</option>)}
            </select>
            <Link className="btn sm" to="/machines">All machines</Link>
          </PageHeader>
          <div className="cards">
            <StatCard label="Status" value={<Badge value={m.status} />} />
            <StatCard label="CPU" value={`${m.cpu_usage}%`} />
            <StatCard label="Memory" value={`${m.memory_usage}%`} />
            <StatCard label="Power" value={`${m.power_watts} W`} />
            <StatCard label="Waste score" value={m.waste_score} tone={m.waste_score >= 70 ? "r" : "g"} />
          </div>
          <div className="g2">{chart("CPU history", m.cpu_history, "%")}{chart("Memory history", m.memory_history, "%")}</div>
          {chart("Power history", m.power_history, "W")}
          <Panel title="Recent waste events" subtitle="Open an event for evidence and recommendations">
            <DataTable rowKey="waste_id" rows={m.recent_events} columns={[
              { header: "ID", cell: (e) => <Link to={`/waste-events/${e.waste_id}`}><b>{e.waste_id}</b></Link> },
              { header: "Time", cell: (e) => formatDateTime(e.timestamp) },
              { header: "Type", cell: (e) => e.waste_type },
              { header: "Score", cell: (e) => e.waste_score },
              { header: "Severity", cell: (e) => <Badge value={e.severity} /> },
            ]} />
          </Panel>
        </>
      );
    }}</DataState>
  );
}
