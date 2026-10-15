import StatCard from "../cards/StatCard";

const TONES = { critical: "r", high: "a", medium: "", low: "" };
export default function AlertSummary({ alerts }) {
  return (
    <div className="cards">
      {Object.keys(TONES).map((s) => (
        <StatCard key={s} label={s[0].toUpperCase() + s.slice(1)} value={alerts.filter((a) => a.severity === s).length} hint="alerts" tone={TONES[s]} />
      ))}
    </div>
  );
}
