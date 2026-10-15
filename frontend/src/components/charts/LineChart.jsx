import ChartLegend from "./ChartLegend";

// sets = [{ name, data[], color, dash? }]. A single set also gets a soft area fill.
export default function LineChart({ sets, labels, legend = true }) {
  const W = 640, H = 230, L = 42, R = 12, T = 12, Bt = 26, n = labels.length;
  const all = sets.flatMap((s) => s.data);
  const mn = Math.floor(Math.min(...all) * 0.85), mx = Math.ceil(Math.max(...all) * 1.05);
  const x = (i) => L + (i * (W - L - R)) / (n - 1 || 1);
  const y = (v) => H - Bt - ((v - mn) / (mx - mn || 1)) * (H - Bt - T);
  const step = Math.ceil(n / 6);
  return (
    <>
      {legend && <ChartLegend items={sets} />}
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Line chart">
        {[0, 1, 2, 3].map((k) => {
          const v = mn + ((mx - mn) * k) / 3;
          return (
            <g key={k}>
              <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} style={{ stroke: "var(--line)" }} />
              <text x={L - 6} y={y(v) + 4} textAnchor="end">{Math.round(v)}</text>
            </g>
          );
        })}
        {labels.map((l, i) => i % step === 0 && <text key={i} x={x(i)} y={H - 8} textAnchor="middle">{l}</text>)}
        {sets.map((s) => {
          const d = s.data.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join("");
          return (
            <g key={s.name}>
              {sets.length === 1 && <path d={`${d}L${x(n - 1)} ${H - Bt}L${x(0)} ${H - Bt}Z`} style={{ fill: s.color, opacity: 0.13 }} />}
              <path d={d} fill="none" style={{ stroke: s.color }} strokeWidth="2.4" strokeDasharray={s.dash ? "6 5" : undefined} strokeLinejoin="round" />
            </g>
          );
        })}
      </svg>
    </>
  );
}
