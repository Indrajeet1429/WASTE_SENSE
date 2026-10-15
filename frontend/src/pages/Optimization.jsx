// Member 4 (intelligence)
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Panel from "../components/common/Panel";
import Note from "../components/common/Note";
import DataState from "../components/common/DataState";
import DataTable from "../components/tables/DataTable";
import useApi from "../hooks/useApi";
import { getOptimization } from "../services/wastesenseService";

export default function Optimization() {
  const state = useApi(getOptimization, []);
  return (
    <>
      <PageHeader title="Optimization" question="What should be changed?" />
      <Note>Suggestions come from the model. Validate them before changing production allocations.</Note>
      <DataState state={state}>{(rows) => (
        <Panel title="Suggested allocations" subtitle="Current against suggested, with the reason">
          <DataTable rows={rows} rowKey="machine_id" columns={[
            { header: "Machine", cell: (x) => <Link to={`/machines/${x.machine_id}`}><b>{x.machine_id}</b></Link> },
            { header: "Resource", cell: (x) => x.resource },
            { header: "Current", cell: (x) => x.current },
            { header: "Suggested", cell: (x) => <b style={{ color: "var(--em)" }}>{x.suggested}</b> },
            { header: "Estimated benefit", cell: (x) => x.estimated_benefit },
            { header: "Reason", cell: (x) => x.reason },
          ]} />
        </Panel>
      )}</DataState>
    </>
  );
}
