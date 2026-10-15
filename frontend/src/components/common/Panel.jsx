export default function Panel({ title, subtitle, className = "", children }) {
  return (
    <section className={`panel ${className}`}>
      {title && <h3>{title}</h3>}
      {subtitle && <p className="sub">{subtitle}</p>}
      {children}
    </section>
  );
}
