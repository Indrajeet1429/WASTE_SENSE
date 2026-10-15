export default function PageHeader({ title, question, children }) {
  return (
    <div className="ph">
      <div><h2>{title}</h2><p>{question}</p></div>
      <div className="bar">{children}</div>
    </div>
  );
}
