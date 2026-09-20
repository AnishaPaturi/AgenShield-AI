import React from 'react'

export default function SecurityCommandCenter({ onNavigate, workspaces = [] }) {
  const latestWs = workspaces[0] || null
  const summary = latestWs?.report?.summary || {
    total_vulnerabilities: 32,
    critical_count: 7,
    high_count: 14,
    medium_count: 8,
    low_count: 3,
    risk_score: 91,
    human_review_count: 3,
  }

  const recentFindings = [
    {
      id: 'f-101',
      severity: 'CRITICAL',
      title: 'Public S3 Bucket Allows World Read/Write',
      provider: 'AWS',
      iac: 'Terraform',
      score: 98,
    },
    {
      id: 'f-102',
      severity: 'HIGH',
      title: 'Open Security Group Ingress (0.0.0.0/0 on Port 22)',
      provider: 'AWS',
      iac: 'CloudFormation',
      score: 91,
    },
    {
      id: 'f-103',
      severity: 'HIGH',
      title: 'Hardcoded Plaintext AWS Secret in ConfigMap',
      provider: 'K8s',
      iac: 'Helm',
      score: 89,
    },
    {
      id: 'f-104',
      severity: 'MEDIUM',
      title: 'Missing KMS Customer Managed Key Encryption for EBS',
      provider: 'AWS',
      iac: 'Terraform',
      score: 74,
    },
  ]

  return (
    <div className="scc-view">
      {/* Top Header Row */}
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Security Command Center</h2>
          <p className="scc-subtitle">
            Autonomous multi-cloud IaC defense monitoring & LangGraph agent telemetry.
          </p>
        </div>
        <button
          className="btn-start-analysis"
          style={{ padding: '10px 20px', fontSize: '13px' }}
          onClick={() => onNavigate('new-scan')}
        >
          ⚡ New Security Scan
        </button>
      </div>

      {/* Top 4 Metrics Cards */}
      <div className="scc-metrics-grid">
        <div className="scc-metric-card scans" onClick={() => onNavigate('workspaces')} style={{ cursor: 'pointer' }}>
          <div className="scc-metric-num">{workspaces.length > 0 ? workspaces.length : 24}</div>
          <div className="scc-metric-label">Total Scans Executed</div>
        </div>

        <div className="scc-metric-card critical" onClick={() => onNavigate('findings')} style={{ cursor: 'pointer' }}>
          <div className="scc-metric-num">{summary.critical_count || 7}</div>
          <div className="scc-metric-label">Critical Findings</div>
        </div>

        <div className="scc-metric-card score">
          <div className="scc-metric-num">91%</div>
          <div className="scc-metric-label">Secure Posture Score</div>
        </div>

        <div className="scc-metric-card queue" onClick={() => onNavigate('audit')} style={{ cursor: 'pointer' }}>
          <div className="scc-metric-num">{summary.human_review_count || 3}</div>
          <div className="scc-metric-label">Review Queue Pending</div>
        </div>
      </div>

      {/* Centerpiece Grid: Agent Activity + Risk Distribution */}
      <div className="scc-mid-grid">
        {/* Left: Agent Activity (8-agent LangGraph workflow centerpiece) */}
        <div className="scc-panel-card">
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span className="flow-node-dot"></span>
              AGENT ACTIVITY · LangGraph 8-Agent Execution
            </div>
            <button
              className="soc-back-home-btn"
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => onNavigate('pipeline')}
            >
              View Full Pipeline →
            </button>
          </div>

          <div className="agent-activity-flow">
            {/* UPLOAD */}
            <div className="flow-node" onClick={() => onNavigate('new-scan')}>
              <span>⬆</span>
              <span>UPLOAD</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* MANAGER */}
            <div className="flow-node active-gold" onClick={() => onNavigate('pipeline')}>
              <span className="flow-node-dot"></span>
              <span>MANAGER AGENT</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* AST + SECRETS PARALLEL */}
            <div className="agent-flow-row">
              <div className="flow-node" onClick={() => onNavigate('pipeline')}>
                <span>AST PARSER</span>
              </div>
              <div style={{ color: '#D6A84F', fontSize: '11px', fontFamily: 'JetBrains Mono' }}>──────</div>
              <div className="flow-node" onClick={() => onNavigate('pipeline')}>
                <span>SECRETS SCANNER</span>
              </div>
            </div>

            <div className="agent-flow-row" style={{ gap: '160px' }}>
              <div className="flow-arrow-down">↓</div>
              <div className="flow-arrow-down">↓</div>
            </div>

            {/* RAG + ANALYST */}
            <div className="agent-flow-row">
              <div className="flow-node" onClick={() => onNavigate('pipeline')}>
                <span>RAG QUERY</span>
              </div>
              <div style={{ color: '#64748B', fontSize: '11px' }}>→</div>
              <div className="flow-node active-gold" onClick={() => onNavigate('consensus')}>
                <span>ANALYST (Claude + GPT)</span>
              </div>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* CONSENSUS */}
            <div className="flow-node" onClick={() => onNavigate('consensus')}>
              <span>CONSENSUS (C_ens 0.94)</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* REMEDIATION */}
            <div className="flow-node" onClick={() => onNavigate('remediation')}>
              <span>REMEDIATION SYNTHESIZER</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* VALIDATION */}
            <div className="flow-node" onClick={() => onNavigate('pipeline')}>
              <span>VALIDATION (LocalStack)</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* REPORT */}
            <div className="flow-node" onClick={() => onNavigate('findings')}>
              <span>REPORT GENERATOR</span>
            </div>
          </div>
        </div>

        {/* Right: Risk Distribution */}
        <div className="scc-panel-card">
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span>Risk Distribution</span>
            </div>
            <span style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
              32 TOTAL FINDINGS
            </span>
          </div>

          <div className="risk-dist-list">
            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#EF4444' }}>● CRITICAL</span>
                <span>7 (22%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div className="risk-dist-bar-fill crit" style={{ width: '22%' }}></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#F97316' }}>● HIGH</span>
                <span>14 (44%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div className="risk-dist-bar-fill high" style={{ width: '44%' }}></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#F59E0B' }}>● MEDIUM</span>
                <span>8 (25%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div className="risk-dist-bar-fill med" style={{ width: '25%' }}></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#64748B' }}>● LOW</span>
                <span>3 (9%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div className="risk-dist-bar-fill low" style={{ width: '9%' }}></div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '24px', padding: '14px', background: 'rgba(18, 24, 33, 0.6)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8', marginBottom: '8px' }}>
              <span>Auto-Patch Eligibility</span>
              <b style={{ color: '#22C55E' }}>84.4%</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8' }}>
              <span>Human Review Escalations</span>
              <b style={{ color: '#F97316' }}>3 items</b>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Table: Recent Security Findings */}
      <div className="scc-panel-card">
        <div className="scc-panel-head">
          <div className="scc-panel-title">
            <span>Recent Security Findings</span>
          </div>
          <button
            className="soc-back-home-btn"
            style={{ fontSize: '11px', padding: '4px 10px' }}
            onClick={() => onNavigate('findings')}
          >
            View All Findings ({recentFindings.length}) →
          </button>
        </div>

        <table className="scc-findings-table">
          <thead>
            <tr>
              <th>SEVERITY</th>
              <th>FINDING TITLE</th>
              <th>CLOUD / IAC</th>
              <th>PRIORITY</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {recentFindings.map((f) => (
              <tr key={f.id}>
                <td>
                  <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                </td>
                <td style={{ fontWeight: 600, color: '#FFFFFF' }}>{f.title}</td>
                <td>
                  <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11.5px' }}>
                    {f.provider} · {f.iac}
                  </span>
                </td>
                <td>
                  <span className="priority-score-badge">{f.score}</span>
                </td>
                <td>
                  <button
                    className="scc-row-arrow-btn"
                    onClick={() => onNavigate('findings')}
                    title="Investigate finding"
                  >
                    Investigate →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
