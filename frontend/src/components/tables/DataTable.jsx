// columns = [{ header, cell: (row) => node }]
export default function DataTable({ columns, rows, rowKey }) {
  return (
    <div className="tw">
      <table>
        <thead><tr>{columns.map((c) => <th key={c.header}>{c.header}</th>)}</tr></thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={columns.length}>Nothing matches these filters. Clear a filter to see more.</td></tr>
          ) : rows.map((r, i) => (
            <tr key={rowKey ? r[rowKey] : i}>{columns.map((c) => <td key={c.header}>{c.cell(r)}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
