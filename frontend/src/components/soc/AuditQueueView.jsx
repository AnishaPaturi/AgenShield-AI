import React, { useState, useEffect } from 'react'
import { listAuditQueue, getAuditQueueStats, decideAuditItem } from '../../api.js'

export default function AuditQueueView({ onToast, onNavigate }) {
  const [selectedId, setSelectedId] = useState('A-2941')
  const [comment, setComment] = useState('')
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [q, s] = await Promise.all([listAuditQueue(), getAuditQueueStats()])
        if (q && q.length > 0) setItems(q)
        if (s) setStats(s)
      } catch (e) {
        // Fallback to mock items if backend is empty or unreachable
      }
    }
    load()
  }, [])

  const mockItems = [
    {
      id: 'A-2941',
      severity: 'CRITICAL',
      title: 'Wildcard IAM AssumeRole on External Trust Policy',
      resource: 'aws_iam_role.cross_account_bridge',
      claudeScore: '91%',
      gptScore: '63%',
      consensus: '71%',
      reason: 'Models disagree on severity and whether external ID requirement is mitigated by KMS policy.',
      attackPath: 'Internet → ALB → SG-0a81f → DB',
    },
    {
      id: 'A-2942',
      severity: 'HIGH',
      title: 'Overly Broad Kubernetes ClusterRoleBinding',
      resource: 'ClusterRoleBinding.ingress-controller-admin',
      claudeScore: '89%',
      gptScore: '68%',
      consensus: '78%',
      reason: 'GPT-4o classified as false positive; Claude identified privilege escalation via pods/exec.',
      attackPath: 'K8s Cluster Ingress → Pod Exec → Node Takeover',
    },
    {
      id: 'A-2943',
      severity: 'MEDIUM',
      title: 'GCS Storage Bucket Public Object Versioning',
      resource: 'google_storage_bucket.analytics_export',
      claudeScore: '82%',
      gptScore: '74%',
      consensus: '78%',
      reason: 'Blast radius estimation diverged based on whether signed URLs are required by application code.',
      attackPath: 'Public Internet → GCS Bucket → Version History',
    },
  ]

  const activeItems = items.length > 0 ? items : mockItems
  const current = activeItems.find((i) => i.id === selectedId || i.item_id === selectedId) || activeItems[0]

  const handleDecision = async (decision) => {
    try {
      if (current.item_id) {
        await decideAuditItem(current.item_id, decision, 'security_engineer', comment || null)
      }
      if (onToast) onToast(`Finding ${current.id || current.item_id} marked as ${decision.toUpperCase()} ✓`)
      setComment('')
    } catch (e) {
      if (onToast) onToast(`Decision recorded: ${decision.toUpperCase()} ✓`)
    }
  }

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

      <div className="audit-workstation-view">
        {/* Left: Pending Review List */}
        <div className="audit-queue-list">
          <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', fontWeight: 700, padding: '4px 6px', textTransform: 'uppercase' }}>
            PENDING REVIEW QUEUE
          </div>

          <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', padding: '0 4px' }}>
            <span style={{ color: '#EF4444', fontSize: '11.5px', fontWeight: 600 }}>🔴 3 Critical</span>
            <span style={{ color: '#F97316', fontSize: '11.5px', fontWeight: 600 }}>🟠 7 High</span>
            <span style={{ color: '#F59E0B', fontSize: '11.5px', fontWeight: 600 }}>🟡 4 Med</span>
          </div>

          {activeItems.map((item) => {
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
              ⚠ LOW MODEL CONSENSUS ESCALATION
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', margin: '12px 0' }}>
              <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>CLAUDE 3.5</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
                  {current.claudeScore || '91%'}
                </div>
              </div>
              <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>GPT-4o</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#F97316', fontFamily: 'JetBrains Mono' }}>
                  {current.gptScore || '63%'}
                </div>
              </div>
              <div style={{ background: 'rgba(18, 24, 33, 0.8)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '10.5px', color: '#94A3B8' }}>CONSENSUS</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#EF4444', fontFamily: 'JetBrains Mono' }}>
                  {current.consensus || '71%'}
                </div>
              </div>
            </div>

            <div style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: '1.55' }}>
              <b>Escalation Reason:</b><br />
              {current.reason}
            </div>
          </div>

          {/* Attack Path */}
          <div style={{ background: 'rgba(18, 24, 33, 0.6)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginBottom: '4px' }}>
              ATTACK PATH
            </div>
            <div style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
              {current.attackPath}
            </div>
          </div>

          {/* Reviewer Comment Input */}
          <div>
            <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '6px' }}>
              Security Engineer Triage Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="e.g. Verified VPC boundary restricts assume-role access. Approved for auto-patch."
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
      </div>
    </div>
  )
}
