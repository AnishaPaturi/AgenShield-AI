import { useEffect, useState } from 'react'
import { decideAuditItem, getAuditQueueStats, listAuditQueue } from '../api.js'

export default function TriageDashboard({ onToast }) {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [statusFilter, setStatusFilter] = useState('PENDING_REVIEW')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const [comments, setComments] = useState({})
  const [openDiffs, setOpenDiffs] = useState({})

  async function loadQueue() {
    setLoading(true)
    try {
      const [queueData, statsData] = await Promise.all([
        listAuditQueue(statusFilter || null, priorityFilter || null),
        getAuditQueueStats(),
      ])
      setItems(queueData)
      setStats(statsData)
    } catch (e) {
      if (onToast) onToast(e.message, true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQueue()
  }, [statusFilter, priorityFilter])

  async function handleDecision(itemId, decision) {
    const comment = comments[itemId] || ''
    try {
      await decideAuditItem(itemId, decision, 'security_engineer', comment || null)
      if (onToast) {
        onToast(`Finding successfully ${decision === 'approve' ? 'APPROVED for auto-remediation' : 'REJECTED as false positive'}`)
      }
      // Remove comment state
      setComments((prev) => {
        const next = { ...prev }
        delete next[itemId]
        return next
      })
      await loadQueue()
    } catch (e) {
      if (onToast) onToast(e.message, true)
    }
  }

  function toggleDiff(itemId) {
    setOpenDiffs((prev) => ({ ...prev, [itemId]: !prev[itemId] }))
  }

  return (
    <div className="triage-dashboard">
      <div className="triage-header">
        <div>
          <h2>Human Security Audit Queue & Triage</h2>
          <p className="subtext">
            Automated escalation queue for low-confidence (C &lt; 0.85), non-consensus, and high-risk exploitability findings.
          </p>
        </div>
        <button className="ghost" onClick={loadQueue} title="Refresh audit queue">
          ⟳ Refresh
        </button>
      </div>

      {stats && (
        <div className="triage-stats-grid">
          <div className="tstat-card">
            <div className="val">{stats.total_items}</div>
            <div className="lbl">Total In Queue</div>
          </div>
          <div className="tstat-card pending">
            <div className="val">{stats.pending_count}</div>
            <div className="lbl">Pending Review</div>
          </div>
          <div className="tstat-card crit">
            <div className="val">{stats.critical_pending}</div>
            <div className="lbl">Critical Pending</div>
          </div>
          <div className="tstat-card approved">
            <div className="val">{stats.approved_count}</div>
            <div className="lbl">Approved</div>
          </div>
          <div className="tstat-card rejected">
            <div className="val">{stats.rejected_count}</div>
            <div className="lbl">Dismissed (FP)</div>
          </div>
        </div>
      )}

      <div className="triage-controls">
        <div className="triage-tabs">
          <button
            className={`tab-btn ${statusFilter === 'PENDING_REVIEW' ? 'active' : ''}`}
            onClick={() => setStatusFilter('PENDING_REVIEW')}
          >
            Pending Review {stats?.pending_count ? `(${stats.pending_count})` : ''}
          </button>
          <button
            className={`tab-btn ${statusFilter === 'APPROVED' ? 'active' : ''}`}
            onClick={() => setStatusFilter('APPROVED')}
          >
            Approved
          </button>
          <button
            className={`tab-btn ${statusFilter === 'REJECTED' ? 'active' : ''}`}
            onClick={() => setStatusFilter('REJECTED')}
          >
            Rejected
          </button>
          <button
            className={`tab-btn ${statusFilter === '' ? 'active' : ''}`}
            onClick={() => setStatusFilter('')}
          >
            All Items
          </button>
        </div>

        <div className="priority-select">
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical Priority</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>
        </div>
      </div>

      {loading && <div className="triage-loading">Loading audit queue...</div>}

      {!loading && items.length === 0 && (
        <div className="triage-empty">
          <div className="glyph">✓</div>
          <h3>Queue is clear</h3>
          <p>No findings currently pending human review with the active filter.</p>
        </div>
      )}

      <div className="triage-items">
        {items.map((item) => {
          const f = item.finding
          const patch = item.suggested_patch
          return (
            <div key={item.item_id} className={`triage-card ${f.severity} ${item.status}`}>
              <div className="triage-card-top">
                <div className="badges">
                  <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                  <span className={`priority-badge ${item.priority}`}>Priority: {item.priority} ({item.priority_score})</span>
                  <span className={`status-badge ${item.status}`}>{item.status.replace('_', ' ')}</span>
                  <span className="trigger-badge">{item.escalation_trigger}</span>
                </div>
                <div className="item-id" title={item.item_id}>ID: {item.item_id.slice(0, 8)}</div>
              </div>

              <div className="triage-title">
                <strong>{f.title}</strong> <code className="f-rule">{f.rule_id}</code>
              </div>

              <div className="escalation-alert">
                <span className="alert-icon">⚠️</span>
                <span><strong>Escalation reason:</strong> {item.escalation_reason}</span>
              </div>

              <p className="triage-desc">{f.description}</p>

              <div className="triage-meta-row">
                <span>Resource: <b>{f.affected_resource}</b></span>
                <span>Confidence: <b>{f.confidence_score}</b></span>
                {f.consensus_score !== null && <span>Consensus: <b>{f.consensus_score}</b></span>}
                <span>Blast Radius: <b>{item.blast_radius} resource(s)</b></span>
              </div>

              {item.attack_path && item.attack_path.length > 0 && (
                <div className="attack-path-strip">
                  <span className="path-label">⚡ Exploit Route:</span>
                  <div className="path-nodes">
                    {item.attack_path.map((node, i) => (
                      <span key={i} className="path-step">
                        <code>{node}</code>
                        {i < item.attack_path.length - 1 && <span className="arrow">→</span>}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {patch && patch.unified_diff && (
                <div className="patch-preview-wrapper">
                  <div className="patch-toggle" onClick={() => toggleDiff(item.item_id)}>
                    <span>{openDiffs[item.item_id] ? '▾' : '▸'}</span> Suggested Remediation Patch
                  </div>
                  {openDiffs[item.item_id] && (
                    <pre className="diff">
                      {patch.unified_diff}
                    </pre>
                  )}
                </div>
              )}

              {item.status === 'PENDING_REVIEW' ? (
                <div className="triage-action-box">
                  <input
                    type="text"
                    className="comment-input"
                    placeholder="Engineer rationale / notes (optional)..."
                    value={comments[item.item_id] || ''}
                    onChange={(e) =>
                      setComments({ ...comments, [item.item_id]: e.target.value })
                    }
                  />
                  <div className="btn-group">
                    <button
                      className="triage-btn approve"
                      onClick={() => handleDecision(item.item_id, 'approve')}
                    >
                      ✓ Approve (Send to Auto-Patch)
                    </button>
                    <button
                      className="triage-btn reject"
                      onClick={() => handleDecision(item.item_id, 'reject')}
                    >
                      ✕ Reject (False Positive)
                    </button>
                  </div>
                </div>
              ) : (
                <div className="triage-resolved-box">
                  <span>Reviewed by <b>{item.reviewer || 'Security Engineer'}</b> on {new Date(item.reviewed_at || item.created_at).toLocaleString()}</span>
                  {item.reviewer_comment && <div className="resolved-comment">"{item.reviewer_comment}"</div>}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
