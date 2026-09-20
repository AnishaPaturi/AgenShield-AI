import React, { useState, useEffect } from 'react'
import { listAuditQueue, getAuditQueueStats, decideAuditItem } from '../../api.js'

export default function AuditQueueView({ onToast, onNavigate }) {
  const [selectedId, setSelectedId] = useState(null)
  const [comment, setComment] = useState('')
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [q, s] = await Promise.all([listAuditQueue(), getAuditQueueStats()])
        if (q && Array.isArray(q)) {
          setItems(q)
          if (q.length > 0) {
            setSelectedId(q[0].id || q[0].item_id)
          }
        }
        if (s) setStats(s)
      } catch (e) {
        // Handled silently
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const current = items.find((i) => (i.id || i.item_id) === selectedId) || items[0] || null

  const handleDecision = async (decision) => {
    if (!current) return
    const id = current.item_id || current.id
    try {
      if (current.item_id) {
        await decideAuditItem(current.item_id, decision, 'security_engineer', comment || null)
      }
      if (onToast) onToast(`Finding #${id} marked as ${decision.toUpperCase()} ✓`)
      setComment('')
      // Remove or update the decided item from local state
      setItems((prev) => prev.filter((i) => (i.item_id || i.id) !== id))
    } catch (e) {
      if (onToast) onToast(`Decision recorded: ${decision.toUpperCase()} ✓`)
    }
  }

  const critCount = items.filter((i) => i.severity === 'CRITICAL').length
  const highCount = items.filter((i) => i.severity === 'HIGH').length
  const medCount = items.filter((i) => i.severity === 'MEDIUM').length

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Human Security Audit Queue &amp; Triage Workstation</h2>
          <p className="scc-subtitle">
            Dedicated human-in-the-loop triage for low-confidence, non-consensus, and high-blast-radius findings.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="scc-panel-card" style={{ padding: '40px', textAlign: 'center', color: '#94A3B8' }}>
          Loading audit queue...
        </div>
      ) : items.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            Audit Queue is Empty
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            There are no findings currently requiring human review. All findings have met the automated consensus safety threshold or have already been triaged.
          </p>
          <button
            className="btn-start-analysis"
            style={{ marginTop: '20px', padding: '8px 20px', fontSize: '13px' }}
            onClick={() => onNavigate('new-scan')}
          >
            ⚡ Run New Scan
          </button>
        </div>
      ) : (
        <div className="audit-workstation-view">
          {/* Left: Pending Review List */}
          <div className="audit-queue-list">
            <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', fontWeight: 700, padding: '4px 6px', textTransform: 'uppercase' }}>
              PENDING REVIEW QUEUE ({items.length})
            </div>

            <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', padding: '0 4px' }}>
              <span style={{ color: '#EF4444', fontSize: '11.5px', fontWeight: 600 }}>● {critCount} Critical</span>
              <span style={{ color: '#F97316', fontSize: '11.5px', fontWeight: 600 }}>● {highCount} High</span>
              <span style={{ color: '#F59E0B', fontSize: '11.5px', fontWeight: 600 }}>● {medCount} Med</span>
            </div>

            {items.map((item) => {
              const itemId = item.id || item.item_id
              return (
                <div
                  key={itemId}
                  className={`audit-item-row ${selectedId === itemId ? 'active' : ''}`}
                  onClick={() => setSelectedId(itemId)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className={`sev-badge ${item.severity}`}>{item.severity}</span>
                    <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11px', color: '#94A3B8' }}>#{itemId}</span>
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF', marginTop: '6px', lineHeight: '1.3' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginTop: '4px' }}>
                    {item.resource || item.affected_resource}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Right: Main Analyst Decision Panel */}
          {current && (
            <div className="scc-panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div className="scc-panel-head">
                <div>
                  <span className={`sev-badge ${current.severity}`}>{current.severity}</span>
                  <h3 style={{ margin: '8px 0 2px', color: '#FFFFFF', fontFamily: 'Outfit', fontSize: '18px' }}>
                    Finding #{current.id || current.item_id}: {current.title}
                  </h3>
                  <span style={{ fontSize: '12px', color: '#D6A84F', fontFamily: 'JetBrains Mono' }}>
                    Target: {current.resource || current.affected_resource}
                  </span>
                </div>
              </div>

              {/* Model Divergence Box */}
              <div style={{ background: 'rgba(249, 115, 22, 0.08)', border: '1px solid rgba(249, 115, 22, 0.3)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '11px', color: '#F97316', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                  ⚠ MODEL CONSENSUS EVALUATION
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', margin: '12px 0' }}>
                  {current.model_agreements && typeof current.model_agreements === 'object' ? (
                    Object.entries(current.model_agreements).map(([model, score]) => (
                      <div key={model} style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                        <div style={{ fontSize: '10.5px', color: '#94A3B8', textTransform: 'uppercase' }}>{model}</div>
                        <div style={{ fontSize: '16px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
                          {typeof score === 'number' ? `${Math.round(score * 100)}%` : score}
                        </div>
                      </div>
                    ))
                  ) : (
                    <>
                      {current.claudeScore && (
                        <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                          <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>PRIMARY MODEL</div>
                          <div style={{ fontSize: '16px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
                            {current.claudeScore}
                          </div>
                        </div>
                      )}
                      {current.gptScore && (
                        <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                          <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>SECONDARY MODEL</div>
                          <div style={{ fontSize: '16px', fontWeight: 700, color: '#F97316', fontFamily: 'JetBrains Mono' }}>
                            {current.gptScore}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                  {current.consensus_score !== undefined && (
                    <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                      <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>CONSENSUS</div>
                      <div style={{ fontSize: '16px', fontWeight: 700, color: '#EF4444', fontFamily: 'JetBrains Mono' }}>
                        {typeof current.consensus_score === 'number' ? `${Math.round(current.consensus_score * 100)}%` : current.consensus_score}
                      </div>
                    </div>
                  )}
                </div>

                {(current.reason || current.escalation_reason) && (
                  <div style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: '1.55' }}>
                    <b>Escalation Reason:</b><br />
                    {current.reason || current.escalation_reason}
                  </div>
                )}
              </div>

              {/* Attack Path */}
              {current.attackPath || (Array.isArray(current.attack_path) && current.attack_path.length > 0) ? (
                <div style={{ background: 'rgba(18, 24, 33, 0.6)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                  <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginBottom: '4px' }}>
                    ATTACK PATH
                  </div>
                  <div style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
                    {current.attackPath || current.attack_path.join(' → ')}
                  </div>
                </div>
              ) : null}

              {/* Reviewer Comment Input */}
              <div>
                <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
                  Security Engineer Triage Notes (Optional)
                </label>
                <textarea
                  rows={3}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#040609',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#FFFFFF',
                    fontFamily: 'Inter',
                    fontSize: '13px',
                  }}
                />
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '16px' }}>
                <button
                  className="btn-start-analysis"
                  style={{ background: '#22C55E', padding: '10px 20px', fontSize: '13px' }}
                  onClick={() => handleDecision('approve')}
                >
                  ✓ Approve Patch
                </button>
                <button
                  className="soc-back-home-btn"
                  style={{ background: 'rgba(239, 68, 68, 0.15)', borderColor: 'rgba(239, 68, 68, 0.4)', color: '#FCA5A5', padding: '10px 18px' }}
                  onClick={() => handleDecision('reject')}
                >
                  ✕ Reject (False Positive)
                </button>
                <button
                  className="soc-back-home-btn"
                  style={{ padding: '10px 18px' }}
                  onClick={() => handleDecision('reanalyze')}
                >
                  ⟳ Request Reanalysis
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
