export default function Meter({ value, color = "var(--em)" }) {
  return (
    <>
      <span className="mt"><i style={{ width: `${Math.min(value, 100)}%`, background: color }} /></span>{value}%
    </>
  );
}
