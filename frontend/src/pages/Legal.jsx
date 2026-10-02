import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Shield, ArrowLeft, Lock, FileText, CheckCircle2, AlertCircle } from 'lucide-react'
import CopyButton from '../components/common/CopyButton.jsx'
import BackToTop from '../components/common/BackToTop.jsx'
import ScrollProgressBar from '../components/common/ScrollProgressBar.jsx'

export default function Legal({ initialTab = 'privacy' }) {
  const location = useLocation()
  const [tab, setTab] = useState(
    location.pathname.includes('terms') ? 'terms' : initialTab
  )

  useEffect(() => {
    if (location.pathname.includes('terms')) {
      setTab('terms')
    } else if (location.pathname.includes('privacy')) {
      setTab('privacy')
    }
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <div className="legal-page-root" style={{ minHeight: '100vh', background: 'var(--bg, #060812)', color: 'var(--text, #F8FAFC)' }}>
      <ScrollProgressBar />

      {/* Header bar */}
      <header className="legal-header" style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(16px)',
        background: 'var(--surface-glass, rgba(14, 19, 34, 0.85))',
        borderBottom: '1px solid var(--border, rgba(167, 139, 250, 0.14))',
        padding: '16px 24px'
      }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '13px', textDecoration: 'none' }}>
              <ArrowLeft size={16} /> Return to Home
            </Link>
            <div style={{ width: '1px', height: '16px', background: 'var(--border)' }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={18} color="var(--primary, #A78BFA)" />
              <span style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.01em' }}>AgentShield Legal & Compliance</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className={`tab-btn ${tab === 'privacy' ? 'active' : ''}`}
              onClick={() => setTab('privacy')}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                border: tab === 'privacy' ? '1px solid var(--primary)' : '1px solid transparent',
                background: tab === 'privacy' ? 'var(--primary-dim)' : 'transparent',
                color: tab === 'privacy' ? 'var(--primary)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              Privacy Policy
            </button>
            <button
              type="button"
              className={`tab-btn ${tab === 'terms' ? 'active' : ''}`}
              onClick={() => setTab('terms')}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                border: tab === 'terms' ? '1px solid var(--primary)' : '1px solid transparent',
                background: tab === 'terms' ? 'var(--primary-dim)' : 'transparent',
                color: tab === 'terms' ? 'var(--primary)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              Terms of Service
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main id="main-content" style={{ maxWidth: '840px', margin: '0 auto', padding: '48px 24px 80px' }}>
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            fontFamily: 'var(--mono)',
            color: 'var(--primary)',
            background: 'var(--primary-dim)',
            padding: '4px 10px',
            borderRadius: '4px',
            marginBottom: '12px',
            border: '1px solid var(--primary-border)'
          }}>
            <Lock size={12} /> ENTERPRISE ASSURANCE SPECIFICATION V2.4
          </div>
          <h1 style={{ fontSize: '32px', fontWeight: 800, letterSpacing: '-0.02em', margin: 0 }}>
            {tab === 'privacy' ? 'Privacy & Data Governance Policy' : 'Terms of Service & Usage Protocol'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginTop: '8px' }}>
            Effective Date: September 2026 • Governing Entity: AgentShield AI Security Operations
          </p>
        </div>

        {tab === 'privacy' ? (
          <div className="legal-article" style={{ display: 'flex', flexDirection: 'column', gap: '32px', lineHeight: 1.7, fontSize: '14.5px' }}>
            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--primary)" /> 1. Zero Model-Training Guarantee
              </h2>
              <p>
                AgentShield AI is built specifically for autonomous security auditing of multi-cloud Infrastructure-as-Code (IaC) environments.
                Under no circumstances are customer-uploaded IaC templates (including Terraform, AWS CloudFormation, Kubernetes Manifests, Azure ARM, and Bicep)
                ever used to train, fine-tune, or calibrate public AI foundation models. All inference pipelines operate with strict data retention zero-persistence guarantees.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--primary)" /> 2. Data Ingestion & Ephemeral Sandbox Execution
              </h2>
              <p>
                When a scan is initiated, your IaC definitions are parsed into abstract syntax trees (AST) and directed acyclic graphs (DAG).
                Dynamic simulations, such as blast-radius validation and multi-agent consensus verification, occur inside ephemeral, isolated sandboxes.
                Once the security graph, findings, and remediation proposals are generated, temporary analysis containers are immediately purged.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--primary)" /> 3. Data Retention & Workspace Lifecycle
              </h2>
              <p>
                - <strong>IaC Uploads:</strong> Saved within your isolated workspace partition for historical re-scans and audit compliance until you choose to delete the workspace.
                <br />
                - <strong>Vulnerability Findings & Remediations:</strong> Retained per your workspace retention schedule to power compliance reporting (CIS, SOC 2, HIPAA).
                <br />
                - <strong>Audit Logs:</strong> Immutable record of security scans, agent decisions, and human verification actions. Retained for 90 days by default.
                <br />
                - <strong>Workspace Deletion:</strong> Triggering a workspace deletion immediately truncates all associated scans, findings, remediation proposals, and cached graphs.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--primary)" /> 4. Authentication, Sessions & Telemetry
              </h2>
              <p>
                We use cryptographically signed JSON Web Tokens (JWT) stored securely in client storage. For third-party OAuth (Google, GitHub),
                AgentShield stores only the authenticated email address, unique provider ID, and display name. Passwords hashed with bcrypt (minimum work factor 12)
                are never stored in plaintext. We collect minimal operational metrics (scan durations, graph node counts) solely for platform stability.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--primary)" /> 5. Security Inquiries & Point of Contact
              </h2>
              <p>
                For security disclosure, GDPR/CCPA data export requests, or enterprise compliance attestations:
              </p>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginTop: '8px', background: 'var(--surface-glass)', padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: '13px' }}>security@agentshield.ai</span>
                <CopyButton text="security@agentshield.ai" ariaLabel="Copy security email" />
              </div>
            </section>
          </div>
        ) : (
          <div className="legal-article" style={{ display: 'flex', flexDirection: 'column', gap: '32px', lineHeight: 1.7, fontSize: '14.5px' }}>
            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="var(--primary)" /> 1. Operational Framework & Scope
              </h2>
              <p>
                AgentShield AI provides automated vulnerability analysis, attack-path modeling, and remediation synthesis for Infrastructure-as-Code.
                By accessing or connecting cloud credentials to the platform, you represent that you possess authorized operational mandate over the evaluated infrastructure.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="var(--primary)" /> 2. Human-in-the-Loop Remediation Standard
              </h2>
              <p>
                While AgentShield autonomous agents synthesize Terraform, CloudFormation, and Kubernetes remediation patches with deterministic sandbox validation,
                all proposed patches route through a human audit queue before being merged or applied to production clusters.
                The final authorization and deployment of infrastructure mutations rests with your designated DevOps/SecOps personnel.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={18} color="var(--primary)" /> 3. Service Level & Cloud API Disclosures
              </h2>
              <p>
                AgentShield queries cloud control planes (AWS IAM/EC2, Azure Graph, Google Cloud Resource Manager) using strict read-only least-privilege tokens.
                AgentShield will never alter production resources outside designated deployment targets or without verified cryptographic consent.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="var(--primary)" /> 4. Intellectual Property & Export
              </h2>
              <p>
                You retain complete ownership of all IaC assets, configuration files, and custom compliance policies uploaded to AgentShield.
                Generated SARIF, PDF, and JSON audit deliverables are licensed to your organization for internal and external regulatory attestation.
              </p>
            </section>
          </div>
        )}
      </main>

      <BackToTop />
    </div>
  )
}
