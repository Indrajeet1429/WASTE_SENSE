// Waste fingerprint: type, confidence, persistence, severity. Values come from the API, never invented here.
export default function Fingerprint({ event }) {
  return (
    <div className="fp">
      <h2>{event.waste_type.toUpperCase()}</h2>
      <div><span>Confidence</span><b>{event.confidence}%</b></div>
      <div><span>Persistence</span><b>{event.persistence ? "YES" : "NO"}</b></div>
      <div><span>Severity</span><b className={event.severity}>{event.severity.toUpperCase()}</b></div>
      <div><span>Waste score</span><b>{event.waste_score}</b></div>
    </div>
  );
}
