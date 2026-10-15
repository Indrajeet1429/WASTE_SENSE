// Member 4 (intelligence): Detection, Evidence, Root cause, Replay, Savings, Recommendation
import { Link, useParams } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import CaseSection from "../components/cards/CaseSection";
import Fingerprint from "../components/cards/Fingerprint";
import BigNumbers from "../components/cards/BigNumbers";
import ExpectedActual from "../components/charts/ExpectedActual";
import DataTable from "../components/tables/DataTable";
import Note from "../components/common/Note";
import useApi from "../hooks/useApi";
import { getWasteEvent } from "../services/wastesenseService";
import { formatDateTime } from "../utils/format";

export default function WasteDetails() {
  const { id } = useParams();
  const state = useApi(() => getWasteEvent(id), [id]);
  return (
    <DataState state={state}>{(e) => {
      if (!e) return <PageHeader title="Event not found" question="That waste ID does not exist."><Link className="btn sm" to="/waste-events">All events</Link></PageHeader>;
      const known = (v) => v !== null && v !== undefined;
      const rows = [
        { label: "CPU", actual: e.actual_cpu, expected: e.expected_cpu, unit: "%" },
        { label: "Memory", actual: e.actual_memory, expected: e.expected_memory, unit: "%" },
        { label: "Power", actual: e.actual_power, expected: e.expected_power, unit: " W" },
      ].filter((r) => known(r.actual) && known(r.expected));
      return (
      <>
        <PageHeader title={`${e.waste_id} on ${e.machine_id}`} question={formatDateTime(e.timestamp)}>
          <Link className="btn sm" to="/waste-events">All events</Link>
          <Link className="btn sm" to={`/replay/${e.waste_id}`}>Open replay</Link>
        </PageHeader>
        <Panel className="file">
          <CaseSection n={1} title="Detection"><Fingerprint event={e} /></CaseSection>
          <CaseSection n={2} title="Evidence">
            {rows.length === 0 && <p className="sub">No replay result is recorded for this event yet.</p>}
            {rows.length > 0 && <ExpectedActual rows={rows} />}
            <DataTable rows={rows.map((r) => ({ r: r.label, a: `${r.actual}${r.unit}`, x: `${r.expected}${r.unit}`, d: `${r.actual - r.expected}${r.unit}` }))} rowKey="r" columns={[
              { header: "Resource", cell: (r) => r.r }, { header: "Actual", cell: (r) => r.a },
              { header: "Expected", cell: (r) => r.x }, { header: "Excess", cell: (r) => r.d },
            ]} />
          </CaseSection>
          <CaseSection n={3} title="Root cause">
            <p className="sub">Likely contributing factors</p>
            {e.contributing_factors.length ? <ol className="cf">{e.contributing_factors.map((f) => <li key={f}>{f}</li>)}</ol> : <p>No contributing factors are provided by the API for this event.</p>}
            <p className="sub" style={{ marginTop: 12 }}>These factors come from the model. They do not prove causality.</p>
          </CaseSection>
          <CaseSection n={4} title="Replay">
            <Note style={{ marginBottom: 12 }}>Model-based counterfactual estimate. Not measured real-world savings.</Note>
            {e.has_replay ? <BigNumbers items={[
              { label: "Current", value: [`${e.actual_cpu}% CPU`, `${e.actual_power} W`] },
              { label: "Replay", value: [`${e.expected_cpu}% CPU`, `${e.expected_power} W`] },
              { label: "Potential difference", value: `${e.power_excess} W` },
            ]} /> : <p className="sub">No replay result is recorded for this event yet.</p>}
          </CaseSection>
          <CaseSection n={5} title="Savings">
            {e.savings ? <>
              <BigNumbers items={[
                { label: "CPU cores", value: e.savings.cpu_cores }, { label: "Memory", value: `${e.savings.memory_gb} GB` }, { label: "Power", value: `${e.savings.power_w} W` },
              ]} />
              <p className="sub" style={{ marginTop: 10 }}>Estimated potential savings: about ${e.savings.cost_usd_month} per month. Not guaranteed.</p>
            </> : <p className="sub">No savings record exists for this event yet.</p>}
          </CaseSection>
          <CaseSection n={6} title="Recommendation">
            <p style={{ marginTop: 0 }}>{e.recommendation ? e.recommendation.recommendation : `Review the allocation on ${e.machine_id} and reduce reserved capacity toward the expected level. Check the waste score again after one full workload cycle.`}</p>
            <Link className="btn sm" to="/optimization">See optimization</Link>
          </CaseSection>
        </Panel>
      </>
      );
    }}</DataState>
  );
}
