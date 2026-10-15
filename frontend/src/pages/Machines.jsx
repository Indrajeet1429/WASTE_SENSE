// Member 3 (monitoring)
import { useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import Badge from "../components/common/Badge";
import Meter from "../components/charts/Meter";
import BarChart from "../components/charts/BarChart";
import DataTable from "../components/tables/DataTable";
import useApi from "../hooks/useApi";
import { getMachines } from "../services/wastesenseService";
import { scoreColor } from "../utils/format";

const SORTS = { score: (a, b) => b.waste_score - a.waste_score, power: (a, b) => b.power_watts - a.power_watts, id: (a, b) => String(a.machine_id).localeCompare(String(b.machine_id), undefined, { numeric: true }) };

export default function Machines() {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("score");
  const state = useApi(getMachines, []);
  return (
    <>
      <PageHeader title="Machines" question="Which machines are working, and which are wasting?">
        <input placeholder="Search machines" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search machines" />
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort">
          <option value="score">Sort by waste score</option><option value="power">Sort by power</option><option value="id">Sort by machine ID</option>
        </select>
      </PageHeader>
      <DataState state={state}>{(all) => {
        const m = all.filter((x) => (x.machine_id + x.name).toLowerCase().includes(q.toLowerCase())).sort(SORTS[sort]);
        return (
          <>
            <Panel title="Machine list" subtitle="Select a machine for CPU, memory and power history">
              <DataTable rowKey="machine_id" rows={m} columns={[
                { header: "Machine", cell: (x) => <><b>{x.machine_id}</b><br /><span className="sub">{x.name}</span></> },
                { header: "CPU", cell: (x) => <Meter value={x.cpu_usage} /> },
                { header: "Memory", cell: (x) => <Meter value={x.memory_usage} color="var(--low)" /> },
                { header: "Power", cell: (x) => `${x.power_watts} W` },
                { header: "Workloads", cell: (x) => x.active_workloads },
                { header: "Waste score", cell: (x) => <Meter value={x.waste_score} color={scoreColor(x.waste_score)} /> },
                { header: "Status", cell: (x) => <Badge value={x.status} /> },
                { header: "Details", cell: (x) => <Link className="btn sm" to={`/machines/${x.machine_id}`}>Open</Link> },
              ]} />
            </Panel>
            <Panel title="Machine comparison" subtitle="Waste score by machine">
              <BarChart data={m.map((x) => x.waste_score)} labels={m.map((x) => x.machine_id.replace(/^M-/, ""))} color={m.map((x) => scoreColor(x.waste_score))} />
            </Panel>
          </>
        );
      }}</DataState>
    </>
  );
}
