// Listed under both Member 3 and Member 4 in the brief: agree on one owner before editing.
import { useState } from "react";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import AlertSummary from "../components/alerts/AlertSummary";
import AlertTable from "../components/alerts/AlertTable";
import useApi from "../hooks/useApi";
import { getAlerts, updateAlertStatus } from "../services/wastesenseService";
import { SEVERITY_OPTIONS } from "../utils/constants";

export default function Alerts() {
  const [sev, setSev] = useState("all");
  const [status, setStatus] = useState("all");
  const [tick, setTick] = useState(0);
  const [err, setErr] = useState(null);
  const state = useApi(getAlerts, [tick]);
  const onStatus = (id, s) => updateAlertStatus(id, s).then(() => { setErr(null); setTick((t) => t + 1); }).catch((e) => setErr(e.message));
  return (
    <>
      <PageHeader title="Alerts" question="Which problems need attention first?">
        <select value={sev} onChange={(e) => setSev(e.target.value)} aria-label="Severity">
          {SEVERITY_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Status">
          <option value="all">All statuses</option><option value="open">Open</option><option value="acknowledged">Acknowledged</option><option value="resolved">Resolved</option>
        </select>
      </PageHeader>
      <DataState state={state}>{(all) => (
        <>
          {err && <p className="sub">Could not update alert: {err}</p>}
          <AlertSummary alerts={all} />
          <Panel title="Alert log" subtitle="Newest first">
            <AlertTable alerts={all.filter((a) => (sev === "all" || a.severity === sev) && (status === "all" || a.status === status))} onStatus={onStatus} />
          </Panel>
        </>
      )}</DataState>
    </>
  );
}
