// Severity or status pill. The value doubles as the colour class (critical, high, open, healthy...).
export default function Badge({ value }) {
  return <span className={`badge ${value}`}>{value}</span>;
}
