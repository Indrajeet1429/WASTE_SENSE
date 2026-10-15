// Member 3 (monitoring)
import { useState } from "react";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import LineChart from "../components/charts/LineChart";
import BarChart from "../components/charts/BarChart";
import useApi from "../hooks/useApi";
import { getTrends } from "../services/wastesenseService";
import { TIME_RANGES } from "../utils/constants";

export default function Trends() {
  const [range, setRange] = useState("24h");
  const state = useApi(() => getTrends(range), [range]);
  return (
    <>
      <PageHeader title="Trends" question="How is waste changing over time?">
        {TIME_RANGES.map((r) => (
          <button key={r.value} className={`btn sm ${range === r.value ? "on" : "line"}`} onClick={() => setRange(r.value)}>{r.label}</button>
        ))}
      </PageHeader>
      <DataState state={state}>{(t) => (
        <>
          <div className="g2">
            <Panel title="Waste score over time" subtitle="Scale 0 to 100">
              <LineChart sets={[{ name: "Waste score", data: t.waste_score, color: "var(--em)" }]} labels={t.labels} legend={false} />
            </Panel>
            <Panel title="Waste event count" subtitle="Detections per interval">
              <BarChart data={t.waste_event_count} labels={t.labels} color="var(--brass2)" />
            </Panel>
          </div>
          <Panel title="CPU, memory and power waste" subtitle="Share of resource use above expected, %">
            <LineChart labels={t.labels} sets={[
              { name: "CPU waste", data: t.cpu_waste, color: "var(--em)" },
              { name: "Memory waste", data: t.memory_waste, color: "var(--low)" },
              { name: "Power waste", data: t.power_waste, color: "var(--brass)" },
            ].filter((s) => s.data)} />
          </Panel>
        </>
      )}</DataState>
    </>
  );
}
