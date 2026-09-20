import React from 'react'

export default function SecurityCommandCenter({ onNavigate, workspaces = [] }) {
  const latestWs = workspaces[0] || null
  const summary = latestWs?.report?.summary || {
    total_vulnerabilities: 0,
    critical_count: 0,
    high_count: 0,
    medium_count: 0,
    low_count: 0,
    risk_score: 0,
    human_review_count: 0,
    auto_patchable_count: 0,
  }

  const recentFindings = latestWs?.report?.findings?.slice(0, 5) || []
  const totalFindings = summary.total_vulnerabilities || 0
  const calcPct = (cnt) => (totalFindings > 0 ? Math.round((cnt / totalFindings) * 100) : 0)

  const postureScore = totalFindings > 0
    ? Math.max(0, Math.min(100, Math.round(100 - (summary.risk_score || 0))))
    : 100

  const autoPatchPct = totalFindings > 0
    ? ((summary.auto_patchable_count || 0) / totalFindings * 100).toFixed(1)
    : '0.0'

  return (
    <div className="scc-view">
      {/* Top Header Row */}
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Security Command Center</h2>
          <p className="scc-subtitle">
            Autonomous multi-cloud IaC defense monitoring &amp; LangGraph agent telemetry.
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
          <div className="scc-metric-num">{workspaces.length}</div>
          <div className="scc-metric-label">Total Scans Executed</div>
        </div>

        <div className="scc-metric-card critical" onClick={() => onNavigate('findings')} style={{ cursor: 'pointer' }}>
          <div className="scc-metric-num">{summary.critical_count || 0}</div>
          <div className="scc-metric-label">Critical Findings</div>
        </div>

        <div className="scc-metric-card score">
          <div className="scc-metric-num">{postureScore}%</div>
          <div className="scc-metric-label">Secure Posture Score</div>
        </div>

        <div className="scc-metric-card queue" onClick={() => onNavigate('audit')} style={{ cursor: 'pointer' }}>
          <div className="scc-metric-num">{summary.human_review_count || 0}</div>
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
                <span>ANALYST</span>
              </div>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* CONSENSUS */}
            <div className="flow-node" onClick={() => onNavigate('consensus')}>
              <span>CONSENSUS</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* REMEDIATION */}
            <div className="flow-node" onClick={() => onNavigate('remediation')}>
              <span>REMEDIATION SYNTHESIZER</span>
            </div>
            <div className="flow-arrow-down">↓</div>

            {/* VALIDATION */}
            <div className="flow-node" onClick={() => onNavigate('pipeline')}>
              <span>VALIDATION</span>
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
              {totalFindings} TOTAL FINDINGS
            </span>
          </div>

          <div className="risk-dist-list">
            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#EF4444' }}>● CRITICAL</span>
                <span>{summary.critical_count || 0} ({calcPct(summary.critical_count || 0)}%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill crit"
                  style={{ width: `${calcPct(summary.critical_count || 0)}%` }}
                ></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#F97316' }}>● HIGH</span>
                <span>{summary.high_count || 0} ({calcPct(summary.high_count || 0)}%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill high"
                  style={{ width: `${calcPct(summary.high_count || 0)}%` }}
                ></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#F59E0B' }}>● MEDIUM</span>
                <span>{summary.medium_count || 0} ({calcPct(summary.medium_count || 0)}%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill med"
                  style={{ width: `${calcPct(summary.medium_count || 0)}%` }}
                ></div>
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: '#64748B' }}>● LOW</span>
                <span>{summary.low_count || 0} ({calcPct(summary.low_count || 0)}%)</span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill low"
                  style={{ width: `${calcPct(summary.low_count || 0)}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '24px', padding: '14px', background: 'rgba(18, 24, 33, 0.6)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8', marginBottom: '8px' }}>
              <span>Auto-Patch Eligibility</span>
              <b style={{ color: '#22C55E' }}>{autoPatchPct}%</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8' }}>
              <span>Human Review Escalations</span>
              <b style={{ color: '#F97316' }}>{summary.human_review_count || 0} items</b>
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
          {recentFindings.length > 0 && (
            <button
              className="soc-back-home-btn"
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={() => onNavigate('findings')}
            >
              View All Findings ({totalFindings}) →
            </button>
          )}
        </div>

        {recentFindings.length === 0 ? (
          <div style={{ padding: '36px 16px', textAlign: 'center', color: '#94A3B8', fontSize: '13px' }}>
            No security findings detected. Click "New Security Scan" to upload and evaluate an IaC template.
          </div>
        ) : (
          <table className="scc-findings-table">
            <thead>
              <tr>
                <th>SEVERITY</th>
                <th>FINDING TITLE</th>
                <th>RESOURCE / RULE</th>
                <th>PRIORITY</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {recentFindings.map((f) => (
                <tr key={f.finding_id || f.id}>
                  <td>
                    <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                  </td>
                  <td style={{ fontWeight: 600, color: '#FFFFFF' }}>{f.title}</td>
                  <td>
                    <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11.5px' }}>
                      {f.affected_resource || f.rule_id}
                    </span>
                  </td>
                  <td>
                    <span className="priority-score-badge">
                      {f.priority || Math.round((f.confidence_score || 0.9) * 100)}
                    </span>
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
        )}
      </div>
    </div>
  )
}
