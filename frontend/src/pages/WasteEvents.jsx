// Member 4 (intelligence)
import { useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import DataTable from "../components/tables/DataTable";
import Badge from "../components/common/Badge";
import useApi from "../hooks/useApi";
import { getWasteEvents } from "../services/wastesenseService";
import { formatDateTime } from "../utils/format";
import { SEVERITY_OPTIONS } from "../utils/constants";

const SORTS = { score: (a, b) => b.waste_score - a.waste_score, time: (a, b) => b.timestamp.localeCompare(a.timestamp), conf: (a, b) => b.confidence - a.confidence };

export default function WasteEvents() {
  const [sev, setSev] = useState("all");
  const [sort, setSort] = useState("score");
  const state = useApi(getWasteEvents, []);
  return (
    <>
      <PageHeader title="Waste events" question="Where is waste being detected?">
        <select value={sev} onChange={(e) => setSev(e.target.value)} aria-label="Severity">
          {SEVERITY_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort">
          <option value="score">Sort by waste score</option><option value="time">Sort by newest</option><option value="conf">Sort by confidence</option>
        </select>
      </PageHeader>
      <DataState state={state}>{(all) => (
        <Panel title="Detected events" subtitle="Open an event for evidence, replay and recommendations">
          <DataTable rowKey="waste_id" rows={all.filter((e) => sev === "all" || e.severity === sev).sort(SORTS[sort])} columns={[
            { header: "Waste ID", cell: (e) => <Link to={`/waste-events/${e.waste_id}`}><b>{e.waste_id}</b></Link> },
            { header: "Machine", cell: (e) => e.machine_id },
            { header: "Time", cell: (e) => formatDateTime(e.timestamp) },
            { header: "Score", cell: (e) => e.waste_score },
            { header: "Severity", cell: (e) => <Badge value={e.severity} /> },
            { header: "Waste type", cell: (e) => e.waste_type },
            { header: "Persistent", cell: (e) => (e.persistence ? "Yes" : "No") },
          ]} />
        </Panel>
      )}</DataState>
    </>
  );
}
