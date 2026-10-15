import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import Logo from "./Logo";
import Icon from "./Icon";
import { useAuth } from "../../hooks/useAuth";
import useTheme from "../../hooks/useTheme";
import { NAV } from "../../utils/constants";
import { USE_MOCK } from "../../services/api";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [theme, toggleTheme] = useTheme();
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  useEffect(() => { setOpen(false); window.scrollTo?.(0, 0); }, [pathname]);

  return (
    <div className="app">
      <aside className={open ? "open" : ""}>
        <Logo />
        <nav className="nav">
          {NAV.map((g) => (
            <div key={g.group}>
              <div className="grp">{g.group}</div>
              {g.items.map((i) => (
                <NavLink key={i.to} to={i.to} className={({ isActive }) => (isActive ? "on" : "")}>
                  <Icon name={i.icon} />{i.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="who">
          <b>{user.name}</b>{user.role}<br />
          <button className="btn line sm" style={{ marginTop: 10, color: "var(--cream)" }} onClick={logout}>Sign out</button>
        </div>
      </aside>
      <main>
        <div className="top">
          <button className="btn line sm menu" onClick={() => setOpen(!open)} aria-label="Open menu">Menu</button>
          <span className="sp" />
          <span className="pill">{USE_MOCK ? "Sample data" : "Live API"}</span>
          <button className="btn line sm" onClick={toggleTheme}>{theme === "dark" ? "Light" : "Dark"} mode</button>
        </div>
        <div className="page"><Outlet /></div>
      </main>
    </div>
  );
}
