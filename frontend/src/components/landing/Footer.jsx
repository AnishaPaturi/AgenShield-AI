import { Link } from 'react-router-dom'
import { Shield, ArrowUp, ExternalLink, Terminal } from 'lucide-react'
import GithubIcon from './GithubIcon'

export default function Footer({ onOpenFeedback }) {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <footer className="landing-footer" aria-label="Site Footer">
      <div className="section-container">
        <div className="footer-top-grid">
          {/* Brand Info Column */}
          <div className="footer-brand-column">
            <div className="footer-brand-header">
              <div className="brand-icon-shield">
                <Shield size={18} strokeWidth={2.4} />
              </div>
              <span className="footer-brand-name">AgentShield <span className="brand-badge">AI</span></span>
            </div>
            <p className="footer-brand-desc">
              Autonomous multi-agent cybersecurity framework for securing multi-cloud
              Infrastructure-as-Code through AST parsing, ensemble consensus, attack-path modeling,
              and sandbox-validated remediation.
            </p>
            <div className="footer-engine-status">
              <span className="footer-dot-pulse" />
              <span>SECURITY ENGINE ACTIVE • MIT OPEN SOURCE</span>
            </div>
          </div>

          {/* Navigation Column */}
          <div className="footer-nav-col">
            <span className="footer-nav-heading">Platform</span>
            <ul className="footer-nav-list">
              <li><Link to="/">Overview</Link></li>
              <li><Link to="/architecture">Platform Architecture</Link></li>
              <li><Link to="/security">Security Intelligence</Link></li>
              <li><a href="/#metrics">Empirical Metrics</a></li>
              <li><a href="/#faq">Architecture FAQ</a></li>
            </ul>
          </div>

          {/* Research & Tech Column */}
          <div className="footer-nav-col">
            <span className="footer-nav-heading">Research &amp; Specs</span>
            <ul className="footer-nav-list">
              <li><a href="#research">Peer-Reviewed Rigor</a></li>
              <li>
                <a
                  href="https://github.com/AnishaPaturi/AgenShield-AI#readme"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Architecture Guide <ExternalLink size={11} className="inline-ext" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AnishaPaturi/AgenShield-AI/tree/main/docs/paper"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Research Publication <ExternalLink size={11} className="inline-ext" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AnishaPaturi/AgenShield-AI"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub Repository <ExternalLink size={11} className="inline-ext" />
                </a>
              </li>
            </ul>
          </div>

          {/* Governance & Console Column */}
          <div className="footer-nav-col">
            <span className="footer-nav-heading">Console &amp; Governance</span>
            <ul className="footer-nav-list">
              <li><Link to="/dashboard">Security Dashboard</Link></li>
              <li><Link to="/scan">Interactive IaC Scanner</Link></li>
              <li><Link to="/agents">Autonomous Agent Pipeline</Link></li>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
              {onOpenFeedback && (
                <li>
                  <button
                    type="button"
                    onClick={onOpenFeedback}
                    style={{ background: 'none', border: 'none', padding: 0, color: 'var(--text-muted)', fontSize: 'inherit', cursor: 'pointer', fontFamily: 'inherit' }}
                  >
                    Report Security Issue
                  </button>
                </li>
              )}
            </ul>
          </div>
        </div>

        {/* Footer Bottom Row */}
        <div className="footer-bottom-row">
          <div className="footer-copyright">
            © {new Date().getFullYear()} AgentShield AI. Research Team: Anisha Paturi, Parinamika Bhanu, Vahini Venkata, Sravani Janak. Released under the MIT License.
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Link to="/privacy" style={{ color: 'var(--text-muted)', fontSize: '12px', textDecoration: 'none' }}>Privacy</Link>
            <span style={{ color: 'var(--border)' }}>•</span>
            <Link to="/terms" style={{ color: 'var(--text-muted)', fontSize: '12px', textDecoration: 'none' }}>Terms</Link>
            <span style={{ color: 'var(--border)' }}>•</span>
            {onOpenFeedback && (
              <button
                type="button"
                onClick={onOpenFeedback}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '12px', cursor: 'pointer' }}
              >
                Feedback
              </button>
            )}
            <button
              type="button"
              onClick={scrollToTop}
              className="footer-scroll-top-btn"
              aria-label="Scroll back to top"
            >
              <span>Back to Top</span>
              <ArrowUp size={14} />
            </button>
          </div>
        </div>
      </div>
    </footer>
  )
}
