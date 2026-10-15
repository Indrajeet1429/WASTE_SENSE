// Row of up to three headline figures: items = [{ value, label, extra }]
export default function BigNumbers({ items, columns = 3 }) {
  return (
    <div className="big" style={{ gridTemplateColumns: `repeat(${columns},1fr)` }}>
      {items.map((i) => (
        <div key={i.label}>
          <span>{i.label}</span>
          {[].concat(i.value).map((v) => <b key={v}>{v}</b>)}
          {i.extra && <span>{i.extra}</span>}
        </div>
      ))}
    </div>
  );
}
