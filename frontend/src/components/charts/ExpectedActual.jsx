// rows = [{ label, actual, expected, unit }]. Expected is hatched, actual is solid, so they never look alike.
export default function ExpectedActual({ rows }) {
  return (
    <>
      {rows.map((r) => {
        const m = Math.max(r.actual, r.expected) * 1.1 || 1;
        return (
          <div className="ea" key={r.label}>
            <span>{r.label}, expected</span><div className="tr"><i className="ex" style={{ width: `${(r.expected / m) * 100}%` }} /></div><b>{r.expected}{r.unit}</b>
            <span>{r.label}, actual</span><div className="tr"><i className="ac" style={{ width: `${(r.actual / m) * 100}%` }} /></div><b>{r.actual}{r.unit}</b>
          </div>
        );
      })}
      <div className="lgd">
        <span><i style={{ borderTopColor: "var(--hatch)", borderTopStyle: "dashed" }} />Expected (model)</span>
        <span><i style={{ borderTopColor: "var(--em)" }} />Actual (measured)</span>
      </div>
    </>
  );
}
