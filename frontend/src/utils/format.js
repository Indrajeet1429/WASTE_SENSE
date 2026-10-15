export const formatDateTime = (t) =>
  new Date(t).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
export const scoreColor = (v) => (v >= 70 ? "var(--crit)" : v >= 50 ? "var(--med)" : "var(--em)");
export const money = (v) => `$${v}`;
