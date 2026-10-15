export const NAV = [
  { group: "Monitoring", items: [
    { to: "/dashboard", label: "Dashboard", icon: "dashboard" },
    { to: "/machines", label: "Machines", icon: "machines" },
    { to: "/trends", label: "Trends", icon: "trends" },
    { to: "/alerts", label: "Alerts", icon: "alerts" },
  ] },
  { group: "Intelligence", items: [
    { to: "/waste-events", label: "Waste events", icon: "waste" },
    { to: "/replay", label: "Replay", icon: "replay" },
    { to: "/optimization", label: "Optimization", icon: "optimization" },
    { to: "/savings", label: "Savings", icon: "savings" },
  ] },
];
export const TIME_RANGES = [
  { value: "1h", label: "1 hour" }, { value: "6h", label: "6 hours" },
  { value: "24h", label: "24 hours" }, { value: "7d", label: "7 days" },
];
export const SEVERITY_OPTIONS = [["all", "All severities"], ["critical", "Critical"], ["high", "High"], ["medium", "Medium"], ["low", "Low"]];
