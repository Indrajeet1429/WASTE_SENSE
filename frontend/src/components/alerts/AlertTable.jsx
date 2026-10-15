import { Link } from "react-router-dom";
import DataTable from "../tables/DataTable";
import Badge from "../common/Badge";
import { formatDateTime } from "../../utils/format";

const STATUSES = ["open", "acknowledged", "resolved"];
export default function AlertTable({ alerts, onStatus }) {
  return (
    <DataTable rowKey="alert_id" rows={alerts} columns={[
      { header: "Machine", cell: (a) => <Link to={`/machines/${a.machine_id}`}><b>{a.machine_id}</b></Link> },
      { header: "Time", cell: (a) => formatDateTime(a.timestamp) },
      { header: "Severity", cell: (a) => <Badge value={a.severity} /> },
      { header: "Message", cell: (a) => a.message },
      { header: "Status", cell: (a) => <Badge value={a.status} /> },
      ...(onStatus ? [{ header: "Update", cell: (a) => (
        <select value={a.status} onChange={(e) => onStatus(a.alert_id, e.target.value)} aria-label={`Status for alert ${a.alert_id}`}>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      ) }] : []),
    ]} />
  );
}
