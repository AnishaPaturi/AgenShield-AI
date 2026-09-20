import React, { useState } from 'react'

export default function FindingsView({ workspace, onNavigate }) {
  const [filter, setFilter] = useState('ALL')
  const [selectedFinding, setSelectedFinding] = useState(null)

  const rawFindings = workspace?.report?.findings || []
  const filtered = filter === 'ALL' ? rawFindings : rawFindings.filter((f) => f.severity === filter)

  return (
    <div className="findings-investigation-view">
      {/* Header with Filters */}
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Security Findings &amp; Investigation</h2>
          <p className="scc-subtitle">
            Every vulnerability calibrated with blast radius analysis, attack paths, and compliance control mappings.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
            <button
              key={s}
              className={`tab-btn ${filter === s ? 'active' : ''}`}
              style={{ fontSize: '11.5px', padding: '6px 12px' }}
              onClick={() => setFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Findings List */}
      {filtered.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          {rawFindings.length === 0 ? (
            <div>
              <p style={{ fontSize: '15px', color: '#FFFFFF', marginBottom: '8px' }}>
                No security findings detected
              </p>
              <p style={{ fontSize: '13px' }}>
                {workspace
                  ? 'No vulnerabilities were identified in this template.'
                  : 'No workspace is currently selected. Click "New Scan" to evaluate an IaC template.'}
              </p>
              <button
                className="btn-start-analysis"
                style={{ marginTop: '16px', padding: '8px 20px', fontSize: '13px' }}
                onClick={() => onNavigate('new-scan')}
              >
                ⚡ Run New Scan
              </button>
            </div>
          ) : (
            <p style={{ fontSize: '14px' }}>
              No findings matching severity filter <b>{filter}</b>.
            </p>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filtered.map((f) => {
            const confidencePct = Math.round((f.confidence_score || 0.9) * 100)
            const complianceList = Array.isArray(f.compliance_mappings)
              ? f.compliance_mappings
              : Array.isArray(f.compliance)
              ? f.compliance
              : []

            return (
              <div key={f.finding_id || f.id} className={`finding-inv-card ${f.severity}`}>
                {/* Card Top: Severity Badge + Priority Score */}
                <div className="finding-inv-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                    <span className="finding-inv-title">{f.title}</span>
                  </div>
                  {f.priority !== undefined && (
                    <div className="priority-score-badge">
                      PRIORITY {f.priority}
                    </div>
                  )}
                </div>

                {/* Target & IaC Format */}
                <div style={{ fontSize: '13px', color: '#94A3B8', fontFamily: 'JetBrains Mono' }}>
                  {f.provider && <b style={{ color: '#FFFFFF' }}>{f.provider} · </b>}
                  {f.iac_type && <span>{f.iac_type} · </span>}
                  <span style={{ color: '#D6A84F' }}>{f.affected_resource}</span>
                </div>

                {/* Meta Grid: Confidence, Blast Radius, Rule */}
                <div className="finding-inv-meta-grid">
                  <div>
                    <span>Confidence: </span>
                    <b>{confidencePct}%</b>
                  </div>
                  {f.blast_radius !== undefined && (
                    <div>
                      <span>Blast Radius: </span>
                      <b style={{ color: f.blast_radius >= 6 ? '#EF4444' : '#F97316' }}>
                        {f.blast_radius} assets
                      </b>
                    </div>
                  )}
                  <div>
                    <span>Rule ID: </span>
                    <b>{f.rule_id}</b>
                  </div>
                  <div>
                    <span>Auto-Patch: </span>
                    <b style={{ color: f.auto_patchable ? '#22C55E' : '#F97316' }}>
                      {f.auto_patchable ? 'ELIGIBLE' : 'MANUAL TRIAGE'}
                    </b>
                  </div>
                </div>

                {/* Attack Path Flow (if present) */}
                {Array.isArray(f.attack_path) && f.attack_path.length > 0 && (
                  <div className="attack-path-investigation">
                    <div style={{ fontSize: '11px', color: '#EF4444', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                      ⚡ EXPLOIT ATTACK PATH
                    </div>
                    <div className="attack-path-nodes-flow">
                      {f.attack_path.map((step, idx, arr) => (
                        <React.Fragment key={idx}>
                          <span className={`attack-node-pill ${idx === arr.length - 1 ? 'vuln' : ''}`}>
                            {step}
                          </span>
                          {idx < arr.length - 1 && <span className="attack-arrow">→</span>}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                )}

                {/* Compliance Badges (if present) */}
                {complianceList.length > 0 && (
                  <div>
                    <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginBottom: '6px' }}>
                      COMPLIANCE FRAMEWORK MAPPINGS
                    </div>
                    <div className="compliance-tags-row">
                      {complianceList.map((c) => (
                        <span key={typeof c === 'string' ? c : c.framework || c.control_id} className="compliance-tag">
                          [{typeof c === 'string' ? c : `${c.framework} ${c.control_id}`}]
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="finding-inv-actions">
                  <button
                    className="btn-view-finding"
                    onClick={() => setSelectedFinding(f)}
                  >
                    🔍 View Finding Details
                  </button>
                  <button
                    className="btn-view-patch"
                    onClick={() => onNavigate('remediation')}
                  >
                    ⚡ View AI Patch &amp; Diff →
                  </button>
                  <button
                    className="soc-back-home-btn"
                    onClick={() => onNavigate('attack-map')}
                  >
                    🕸️ View Attack Graph →
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Investigation Details Modal */}
      {selectedFinding && (
        <div className="modal-overlay" onClick={() => setSelectedFinding(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '640px' }}>
            <div className="modal-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Vulnerability Investigation</span>
              <button
                className="modal-close"
                onClick={() => setSelectedFinding(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span className={`sev-badge ${selectedFinding.severity}`}>{selectedFinding.severity}</span>
                <h3 style={{ margin: '8px 0 4px', color: '#FFFFFF', fontFamily: 'Outfit' }}>
                  {selectedFinding.title}
                </h3>
                <div style={{ fontSize: '12px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
                  Rule: {selectedFinding.rule_id} · Resource: {selectedFinding.affected_resource}
                </div>
              </div>

              {selectedFinding.description && (
                <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#CBD5E1', lineHeight: '1.6' }}>
                  <b>Impact Assessment:</b><br />
                  {selectedFinding.description}
                </div>
              )}

              {(selectedFinding.remediation || selectedFinding.remediation_hint) && (
                <div style={{ background: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#86EFAC' }}>
                  <b>Remediation Strategy:</b><br />
                  {selectedFinding.remediation || selectedFinding.remediation_hint}
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  className="soc-back-home-btn"
                  onClick={() => setSelectedFinding(null)}
                >
                  Close
                </button>
                <button
                  className="btn-start-analysis"
                  style={{ padding: '8px 18px', fontSize: '13px' }}
                  onClick={() => {
                    setSelectedFinding(null)
                    onNavigate('remediation')
                  }}
                >
                  Launch Remediation →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
