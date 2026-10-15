import { useState } from "react";

export const applyStoredTheme = () => {
  try { const t = localStorage.getItem("ws_theme"); if (t) document.documentElement.dataset.theme = t; } catch { /* ignore */ }
};
export default function useTheme() {
  const [theme, setTheme] = useState(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("ws_theme", next); } catch { /* ignore */ }
    setTheme(next);
  };
  return [theme, toggle];
}
