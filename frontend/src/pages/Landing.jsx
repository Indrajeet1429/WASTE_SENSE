import { Link } from "react-router-dom";
import Logo from "../components/common/Logo";
import LineChart from "../components/charts/LineChart";
import { useAuth } from "../hooks/useAuth";
import { trends, dashboard } from "../services/mockData"; // sample data on purpose: the home page is public

const STEPS = [
  ["Detection", "The type of waste, how confident the model is, how serious it is, and whether it persists."],
  ["Evidence", "Actual against expected CPU, memory and power, with the excess shown for each."],
  ["Root cause", "Likely contributing factors ranked by the model, never presented as proof."],
  ["Replay", "A model-based counterfactual: what usage might have looked like without the waste."],
  ["Savings", "Estimated potential CPU, memory, power and cost savings."],
  ["Recommendation", "A suggested allocation change with the reason behind it."],
];
const PRINCIPLES = [
  ["Estimates stay estimates", "Savings and replay values are labelled as estimated and model-based, never as guaranteed or measured."],
  ["Sample data is labelled", "Until the live API is connected, every screen carries a visible sample data badge."],
  ["Likely, not proven", "Root cause factors are contributing factors from the model, not claims of causality."],
];

export default function Landing() {
  const { user } = useAuth();
  const t = trends("24h"), d = dashboard();
  return (
    <>
      <div className="lnav">
        <Logo />
        <nav><a href="#how">How it works</a><a href="#platform">Platform</a><a href="#honest">Our principles</a></nav>
        {user ? <Link className="btn sm" to="/dashboard">Open dashboard</Link> : <Link className="btn sm" to="/login">Sign in</Link>}
      </div>
      <header className="hero">
        <div className="hg">
          <div>
            <span className="tag">Resource waste intelligence</span>
            <h1>See the waste hiding in your machines.</h1>
            <p className="lead">WasteSense compares what your machines actually use with what they should use, explains the likely reasons, and estimates what you could save.</p>
            <div className="cta">
              {user ? <Link className="btn brass" to="/dashboard">Open dashboard</Link> : <>
                <Link className="btn brass" to="/signup">Create account</Link>
                <Link className="btn line" to="/login">Sign in</Link>
              </>}
            </div>
            <p className="fine">Estimates are labelled as estimates. Sample data is labelled as sample data.</p>
          </div>
          <div className="pv">
            <div className="row"><h3>Waste score, last 24 hours</h3><span className="pill">Sample data</span></div>
            <LineChart sets={[{ name: "Waste score", data: t.waste_score, color: "var(--em)" }]} labels={t.labels} legend={false} />
            <div className="mini">
              <div><b>{d.current_waste_events}</b><span>waste events</span></div>
              <div><b>{d.critical_alerts}</b><span>critical alerts</span></div>
              <div><b>${d.potential_savings.usd}</b><span>est. savings per month</span></div>
            </div>
          </div>
        </div>
      </header>
      <section className="blk" id="how"><div className="wrap">
        <h2>From signal to decision</h2>
        <p className="in">Every waste event opens as a case file that moves from what was seen to what to do about it.</p>
        <div className="steps">{STEPS.map((s, i) => <div key={s[0]}><b>{i + 1}</b><h3>{s[0]}</h3><p>{s[1]}</p></div>)}</div>
      </div></section>
      <section className="blk" id="platform" style={{ paddingTop: 0 }}><div className="wrap"><div className="two">
        <div className="a"><h3>Monitoring</h3><p className="q">What is happening right now?</p>
          <ul><li>Dashboard with fleet-level cards, charts and rankings</li><li>Machines with CPU, memory, power and status</li><li>Machine details with expected against actual history</li><li>Trends over 1 hour, 6 hours, 24 hours and 7 days</li><li>Alerts by severity and status</li></ul>
          <Link className="btn" to="/login">Open monitoring</Link></div>
        <div className="b"><h3>Intelligence</h3><p className="q">Why is it happening, and what can we do?</p>
          <ul><li>Waste events with fingerprint, severity and persistence</li><li>Evidence, root cause and confidence in one case file</li><li>Waste replay as a counterfactual estimate</li><li>Optimization with current and suggested allocation</li><li>Estimated potential savings</li></ul>
          <Link className="btn brass" to="/login">Open intelligence</Link></div>
      </div></div></section>
      <section className="blk hon" id="honest"><div className="wrap">
        <h2>Honest by design</h2>
        <p className="in">Decision tools earn trust by being clear about what they know.</p>
        <div className="steps">{PRINCIPLES.map((s) => <div key={s[0]}><h3>{s[0]}</h3><p>{s[1]}</p></div>)}</div>
      </div></section>
      <footer className="foot"><span>WASTESENSE 2026 All rights reserved</span></footer>
    </>
  );
}
