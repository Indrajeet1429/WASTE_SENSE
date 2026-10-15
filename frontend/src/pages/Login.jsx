import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import Logo from "../components/common/Logo";
import { useAuth } from "../hooks/useAuth";

export default function Login({ mode = "login" }) {
  const signup = mode === "signup";
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const [f, setF] = useState({ name: "", email: "", role: "Operator", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;

  const on = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const run = async (fn) => {
    setError(""); setBusy(true);
    try { await fn(); navigate("/dashboard"); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const submit = (e) => { e.preventDefault(); run(() => (signup ? register(f) : login(f.email, f.password))); };

  return (
    <div className="auth">
      <div className="ap">
        <Logo />
        <h2>Know what your machines are wasting, and why.</h2>
        <ul><li>Monitoring and intelligence in one place</li><li>Every estimate clearly labelled</li><li>Built to cut CPU, memory and power waste</li></ul>
      </div>
      <div className="fw">
        <form className="form" onSubmit={submit}>
          <h2>{signup ? "Create your account" : "Welcome back"}</h2>
          <div className="tabs">
            <button type="button" className={signup ? "" : "on"} onClick={() => navigate("/login")}>Sign in</button>
            <button type="button" className={signup ? "on" : ""} onClick={() => navigate("/signup")}>Create account</button>
          </div>
          {signup && <label>Full name<input required value={f.name} onChange={on("name")} autoComplete="name" /></label>}
          <label>Email<input type="email" required value={f.email} onChange={on("email")} autoComplete="email" /></label>
          {signup && <label>Role<select value={f.role} onChange={on("role")}><option>Operator</option><option>Analyst</option><option>Admin</option></select></label>}
          <label>Password<input type="password" required value={f.password} onChange={on("password")} autoComplete={signup ? "new-password" : "current-password"} /></label>
          {signup && <label>Confirm password<input type="password" required value={f.confirm} onChange={on("confirm")} autoComplete="new-password" /></label>}
          <div className="err" role="alert">{error}</div>
          <button className="btn" style={{ justifyContent: "center" }} disabled={busy}>{signup ? "Create account" : "Sign in"}</button>
          {signup && <p className="hint">Use 8 or more characters with a letter and a number.</p>}
          <p className="hint">Accounts are stored in this browser only until the FastAPI auth endpoints are connected.</p>
        </form>
      </div>
    </div>
  );
}
