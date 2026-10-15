// One numbered step of a waste case file (Detection, Evidence, Root cause, ...).
export default function CaseSection({ n, title, children }) {
  return (
    <div className="case">
      <div><span className="n">{n}</span><h3>{title}</h3></div>
      <div>{children}</div>
    </div>
  );
}
