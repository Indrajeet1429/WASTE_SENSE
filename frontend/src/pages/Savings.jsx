// Member 4 (intelligence): always "estimated potential savings", never guaranteed
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import DataState from "../components/common/DataState";
import StatCard from "../components/cards/StatCard";
import DataTable from "../components/tables/DataTable";
import useApi from "../hooks/useApi";
import { getSavings } from "../services/wastesenseService";

export default function Savings() {
  const state = useApi(getSavings, []);
  return (
    <>
      <PageHeader title="Savings" question="What might be saved?" />
      <DataState state={state}>{({ totals: t, by_event: rows }) => (
        <>
          <div className="cards">
            <StatCard label="Potential CPU saving" value={`${t.cpu} cores`} hint="estimated potential" />
            <StatCard label="Potential memory saving" value={`${t.mem} GB`} hint="estimated potential" />
            <StatCard label="Potential power saving" value={`${t.pw} W`} hint="estimated potential" />
            <StatCard label="Potential cost saving" value={`$${t.usd}`} hint="per month" tone="g" />
          </div>
          <Panel title="Estimated potential savings" subtitle="Per waste event. These are estimates, not guaranteed savings.">
            <DataTable rows={rows} rowKey="waste_id" columns={[
              { header: "Event", cell: (x) => <Link to={`/waste-events/${x.waste_id}`}><b>{x.waste_id}</b></Link> },
              { header: "Machine", cell: (x) => x.machine_id },
              { header: "CPU cores", cell: (x) => x.cpu_cores }, { header: "Memory GB", cell: (x) => x.memory_gb },
              { header: "Power W", cell: (x) => x.power_w }, { header: "Cost $/month", cell: (x) => x.cost_usd_month },
            ]} />
          </Panel>
        </>
      )}</DataState>
    </>
  );
}
