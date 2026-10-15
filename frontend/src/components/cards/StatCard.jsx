// tone: "" | "g" (green) | "r" (red) | "a" (brass)
export default function StatCard({ label, value, hint, tone = "" }) {
  return (
    <div className={`card ${tone}`}>
      <div className="l">{label}</div>
      <div className="v">{value}</div>
      <div className="s">{hint}</div>
    </div>
  );
}
