// color can be one CSS colour or an array with one colour per bar.
export default function BarChart({ data, labels, color }) {
  const W = 640, H = 210, L = 34, Bt = 26, T = 10, n = data.length, mx = Math.max(...data, 1), bw = (W - L - 10) / n;
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Bar chart">
      {[0, 1, 2].map((k) => {
        const v = (mx * k) / 2, yy = H - Bt - (v / mx) * (H - Bt - T);
        return (
          <g key={k}>
            <line x1={L} x2={W - 10} y1={yy} y2={yy} style={{ stroke: "var(--line)" }} />
            <text x={L - 6} y={yy + 4} textAnchor="end">{Math.round(v)}</text>
          </g>
        );
      })}
      {data.map((v, i) => {
        const h = (v / mx) * (H - Bt - T);
        return (
          <g key={i}>
            <rect x={L + i * bw + bw * 0.18} y={H - Bt - h} width={bw * 0.64} height={h} rx="3" style={{ fill: Array.isArray(color) ? color[i] : color }} />
            <text x={L + i * bw + bw / 2} y={H - 8} textAnchor="middle">{labels[i]}</text>
          </g>
        );
      })}
    </svg>
  );
}
