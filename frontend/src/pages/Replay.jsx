// Member 4 (intelligence)
import { useNavigate, useParams } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import Note from "../components/common/Note";
import DataState from "../components/common/DataState";
import BigNumbers from "../components/cards/BigNumbers";
import ExpectedActual from "../components/charts/ExpectedActual";
import useApi from "../hooks/useApi";
import { getWasteEvents } from "../services/wastesenseService";
import { formatDateTime } from "../utils/format";

export default function Replay() {
  const { id } = useParams();
  const navigate = useNavigate();
  const state = useApi(getWasteEvents, []);
  return (
    <DataState state={state}>{(list) => {
      const e = id ? list.find((x) => String(x.waste_id) === id) : list[0];
      if (!e) return <PageHeader title="No waste events" question="Nothing to replay yet." />;
      const ok = e.has_replay !== false;
      return (
        <>
          <PageHeader title="Waste replay" question="What would usage look like without the waste?">
            <select value={e.waste_id} onChange={(ev) => navigate(`/replay/${ev.target.value}`)} aria-label="Choose event">
              {list.map((x) => <option key={x.waste_id} value={x.waste_id}>{x.waste_id} on {x.machine_id}, {x.waste_type}</option>)}
            </select>
          </PageHeader>
          <Note>Model-based counterfactual estimate. This is not measured real-world savings.</Note>
          <Panel title={`Replay of ${e.waste_id}`} subtitle={`${e.machine_id}, ${formatDateTime(e.timestamp)}`}>
            {!ok ? <p className="sub">No replay result is recorded for this event yet.</p> : <>
            <BigNumbers items={[
              { label: "Current", value: [`${e.actual_cpu}% CPU`, `${e.actual_power} W`] },
              { label: "Replay (expected)", value: [`${e.expected_cpu}% CPU`, `${e.expected_power} W`] },
              { label: "Potential difference", value: `${e.power_excess} W`, extra: `${e.cpu_excess}% CPU` },
            ]} />
            <div style={{ marginTop: 18 }}>
              <ExpectedActual rows={[{ label: "CPU", actual: e.actual_cpu, expected: e.expected_cpu, unit: "%" }, { label: "Power", actual: e.actual_power, expected: e.expected_power, unit: " W" }]} />
            </div>
            </>}
          </Panel>
        </>
      );
    }}</DataState>
  );
}
