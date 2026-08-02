import { Link } from 'react-router-dom'
import ScanDemo from '../components/ScanDemo.jsx'
import Pipeline from '../components/Pipeline.jsx'
import ComplianceStrip from '../components/ComplianceStrip.jsx'
import '../landing.css'

export default function Landing() {
  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="brand">
          <div className="mark">AS</div>
          <span className="brand-name">AgentShield AI</span>
        </div>
        <Link to="/console" className="nav-cta">Launch Console →</Link>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">autonomous infrastructure security</span>
          <h1>
            Infrastructure that<br />
            patches <em>itself</em><br />
            before you hit apply.
          </h1>
          <p className="hero-sub">
            Eight coordinated AI agents parse your Terraform, CloudFormation, Kubernetes,
            and Helm — then detect, prove, and patch vulnerabilities before a single
            resource goes live.
          </p>
          <div className="hero-actions">
            <Link to="/console" className="btn-primary">Launch Console</Link>
            <a href="#pipeline" className="btn-secondary">See how it works ↓</a>
          </div>
          <div className="stat-strip">
            <div><b>8</b><span>agents</span></div>
            <div><b>4</b><span>IaC formats</span></div>
            <div><b>3</b><span>clouds</span></div>
            <div><b>4</b><span>compliance frameworks</span></div>
          </div>
        </div>
        <div className="hero-visual">
          <ScanDemo />
        </div>
      </section>

      <div id="pipeline">
        <Pipeline />
      </div>

      <section className="cta-band">
        <h2>Ship the infrastructure you don't have to double-check.</h2>
        <Link to="/console" className="btn-primary large">Launch Console →</Link>
        <ComplianceStrip />
      </section>

      <footer className="landing-footer">
        <span>AgentShield AI — built for the ET AI Hackathon 2026</span>
      </footer>
    </div>
  )
}
