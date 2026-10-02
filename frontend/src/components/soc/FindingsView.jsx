import React, { useState, useMemo } from 'react'
import { Search, ShieldAlert, AlertTriangle, CheckCircle2, ArrowRight, X } from 'lucide-react'
import CopyButton from '../common/CopyButton.jsx'

export default function FindingsView({ workspace, onNavigate }) {
  const [filter, setFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [patchFilter, setPatchFilter] = useState('ALL') // ALL, AUTO, MANUAL
  const [selectedFinding, setSelectedFinding] = useState(null)

  const rawFindings = workspace?.report?.findings || []

  // Filter findings based on severity, patch eligibility, and keyword search
  const filtered = useMemo(() => {
    return rawFindings.filter((f) => {
      // Severity filter
      if (filter !== 'ALL' && f.severity !== filter) return false
      // Patch filter
      if (patchFilter === 'AUTO' && !f.auto_patchable) return false
      if (patchFilter === 'MANUAL' && f.auto_patchable) return false
      // Search query filter (matches title, rule_id, affected_resource, description)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const matchTitle = (f.title || '').toLowerCase().includes(q)
        const matchRule = (f.rule_id || '').toLowerCase().includes(q)
        const matchRes = (f.affected_resource || '').toLowerCase().includes(q)
        const matchDesc = (f.description || '').toLowerCase().includes(q)
        if (!matchTitle && !matchRule && !matchRes && !matchDesc) return false
      }
      return true
    })
  }, [rawFindings, filter, patchFilter, searchQuery])

  // Count metrics for quick filter strip
  const counts = useMemo(() => {
    return {
      all: rawFindings.length,
      critical: rawFindings.filter((f) => f.severity === 'CRITICAL').length,
      high: rawFindings.filter((f) => f.severity === 'HIGH').length,
      medium: rawFindings.filter((f) => f.severity === 'MEDIUM').length,
      low: rawFindings.filter((f) => f.severity === 'LOW').length,
      autoPatch: rawFindings.filter((f) => f.auto_patchable).length,
    }
  }, [rawFindings])

  return (
    <div className="findings-investigation-view">
      {/* Header with Title and Search/Filters */}
      <div className="scc-header-row" style={{ alignItems: 'flex-start' }}>
        <div>
          <h2 className="scc-title">Security Findings &amp; Investigation</h2>
          <p className="scc-subtitle">
            Autonomous threat prioritization with blast radius analysis, attack paths, and compliance control mappings.
          </p>
        </div>

        {/* Search bar & Filter Pills */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end', minWidth: '300px' }}>
          {/* Keyword Search Input */}
          <div style={{ position: 'relative', width: '100%' }}>
            <Search
              size={14}
              style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748B' }}
            />
            <input
              type="text"
              placeholder="Search findings, rule ID, resource..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '6px 10px 6px 30px',
                background: 'rgba(20, 26, 40, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '6px',
                fontSize: '12px',
                color: '#F1F5F9',
                outline: 'none',
              }}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#94A3B8',
                  cursor: 'pointer',
                  padding: 0,
                }}
              >
                <X size={13} />
              </button>
            )}
          </div>

          {/* Severity Pills */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {[
              { id: 'ALL', label: `ALL (${counts.all})` },
              { id: 'CRITICAL', label: `CRITICAL (${counts.critical})` },
              { id: 'HIGH', label: `HIGH (${counts.high})` },
              { id: 'MEDIUM', label: `MED (${counts.medium})` },
              { id: 'LOW', label: `LOW (${counts.low})` },
            ].map((s) => (
              <button
                key={s.id}
                className={`tab-btn ${filter === s.id ? 'active' : ''}`}
                style={{ fontSize: '11px', padding: '4px 10px' }}
                onClick={() => setFilter(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Findings List */}
      {filtered.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          {rawFindings.length === 0 ? (
            <div>
              <ShieldAlert size={40} style={{ color: '#10B981', margin: '0 auto 12px', opacity: 0.8 }} />
              <p style={{ fontSize: '15px', color: 'var(--text, #F8FAFC)', marginBottom: '8px', fontWeight: 600 }}>
                No Security Findings Detected
              </p>
              <p style={{ fontSize: '13px', maxWidth: '440px', margin: '0 auto 16px' }}>
                {workspace
                  ? 'No vulnerabilities were identified in this template definition.'
                  : 'No workspace is currently selected. Click "New Scan" to evaluate an IaC template.'}
              </p>
              <button
                className="btn-start-analysis"
                style={{ padding: '8px 20px', fontSize: '13px' }}
                onClick={() => onNavigate('new-scan')}
              >
                ⚡ Run New Scan
              </button>
            </div>
          ) : (
            <p style={{ fontSize: '14px' }}>
              No findings matching the current search &amp; severity filters.
            </p>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }} role="region" aria-live="polite" aria-label="Security findings list">
          {filtered.map((f) => {
            const confidenceDisplay =
              typeof f.confidence_score === 'number'
                ? `${Math.round(f.confidence_score * 100)}%`
                : '—'
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted, #94A3B8)', fontFamily: 'JetBrains Mono', flexWrap: 'wrap' }}>
                  {f.provider && <b style={{ color: 'var(--text, #FFFFFF)' }}>{f.provider} · </b>}
                  {f.iac_type && <span>{f.iac_type} · </span>}
                  <span style={{ color: '#38BDF8' }}>{f.affected_resource}</span>
                  {f.affected_resource && (
                    <CopyButton text={f.affected_resource} size={12} ariaLabel={`Copy resource identifier ${f.affected_resource}`} />
                  )}
                </div>

                {/* Meta Grid: Confidence, Blast Radius, Rule */}
                <div className="finding-inv-meta-grid">
                  <div>
                    <span>Confidence: </span>
                    <b>{confidenceDisplay}</b>
                  </div>
                  {f.blast_radius !== undefined && (
                    <div>
                      <span>Blast Radius: </span>
                      <b style={{ color: '#F59E0B' }}>
                        {f.blast_radius} assets
                      </b>
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>Rule ID: </span>
                    <b>{f.rule_id}</b>
                    {f.rule_id && <CopyButton text={f.rule_id} size={11} ariaLabel={`Copy rule ${f.rule_id}`} />}
                  </div>
                  <div>
                    <span>Auto-Patch: </span>
                    <b style={{ color: f.auto_patchable ? 'var(--ok, #34D399)' : '#F59E0B' }}>
                      {f.auto_patchable ? 'ELIGIBLE' : 'MANUAL TRIAGE'}
                    </b>
                  </div>
                </div>

                {/* Attack Path Flow (if present) */}
                {Array.isArray(f.attack_path) && f.attack_path.length > 0 && (
                  <div className="attack-path-investigation">
                    <div style={{ fontSize: '11px', color: 'var(--primary, #E11D48)', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
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
                <h3 style={{ margin: '8px 0 4px', color: 'var(--text, #F8FAFC)', fontFamily: 'Outfit' }}>
                  {selectedFinding.title}
                </h3>
                <div style={{ fontSize: '12px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
                  Rule: {selectedFinding.rule_id} · Resource: {selectedFinding.affected_resource}
                </div>
              </div>

              {selectedFinding.description && (
                <div style={{ background: 'rgba(20, 26, 40, 0.75)', border: '1px solid rgba(255, 255, 255, 0.08)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#CBD5E1', lineHeight: '1.6' }}>
                  <b>Impact Assessment:</b><br />
                  {selectedFinding.description}
                </div>
              )}

              {(selectedFinding.remediation || selectedFinding.remediation_hint) && (
                <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#86EFAC' }}>
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
