export default function ChartLegend({ items }) {
  return (
    <div className="lgd">
      {items.map((s) => (
        <span key={s.name}><i style={{ borderTopColor: s.color, borderTopStyle: s.dash ? "dashed" : "solid" }} />{s.name}</span>
      ))}
    </div>
  );
}
