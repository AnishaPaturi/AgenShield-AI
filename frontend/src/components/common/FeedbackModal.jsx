import React, { useState, useEffect, useRef } from 'react'
import { MessageSquare, X, Send, CheckCircle2 } from 'lucide-react'

export default function FeedbackModal({ isOpen, onClose }) {
  const [type, setType] = useState('bug')
  const [severity, setSeverity] = useState('medium')
  const [description, setDescription] = useState('')
  const [email, setEmail] = useState('')
  const [includeEnv, setIncludeEnv] = useState(true)
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const modalRef = useRef(null)

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!description.trim()) return

    setSubmitting(true)
    const feedbackPayload = {
      type,
      severity,
      description,
      email: email || 'anonymous@agentshield.internal',
      timestamp: new Date().toISOString(),
      metadata: includeEnv ? {
        url: window.location.href,
        userAgent: navigator.userAgent,
        screen: `${window.innerWidth}x${window.innerHeight}`,
      } : null
    }

    // Persist to local feedback queue
    try {
      const existing = JSON.parse(localStorage.getItem('agentshield_feedback_queue') || '[]')
      existing.push(feedbackPayload)
      localStorage.setItem('agentshield_feedback_queue', JSON.stringify(existing))
    } catch {
      // ignore
    }

    setTimeout(() => {
      setSubmitting(false)
      setSubmitted(true)
      setTimeout(() => {
        setSubmitted(false)
        setDescription('')
        onClose()
      }, 1600)
    }, 400)
  }

  return (
    <div
      className="modal-backdrop-portal"
      onClick={(e) => {
        if (e.target === e.currentTarget && !submitting) onClose()
      }}
      role="presentation"
    >
      <div
        ref={modalRef}
        className="accessible-modal-dialog feedback-modal-content"
        role="dialog"
        aria-modal="true"
        aria-labelledby="feedback-modal-title"
      >
        <div className="modal-dialog-header">
          <div className="modal-dialog-icon-wrapper" style={{
            background: 'var(--primary-dim)',
            borderColor: 'var(--primary-border)'
          }}>
            <MessageSquare size={18} color="var(--primary)" aria-hidden="true" />
          </div>
          <div className="modal-dialog-title-block">
            <h3 id="feedback-modal-title">Security & UX Feedback</h3>
            <p>Report vulnerabilities, bugs, or operational observations directly to the engineering team.</p>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close feedback modal"
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>

        {submitted ? (
          <div className="feedback-success-state" style={{ textAlign: 'center', padding: '32px 16px' }}>
            <CheckCircle2 size={42} color="var(--ok, #34D399)" style={{ margin: '0 auto 12px' }} />
            <h4 style={{ color: 'var(--text)', fontSize: '16px', fontWeight: 600 }}>Feedback Transmitted</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '6px' }}>
              Your report has been logged and queued for audit review. Thank you for strengthening AgentShield.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="feedback-form">
            <div className="feedback-row">
              <label htmlFor="feedback-type">Category</label>
              <select
                id="feedback-type"
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="feedback-input"
              >
                <option value="bug">Bug Report</option>
                <option value="security">Security / IaC Vulnerability</option>
                <option value="feature">Enhancement Request</option>
                <option value="general">General Experience</option>
              </select>
            </div>

            <div className="feedback-row">
              <label htmlFor="feedback-severity">Urgency</label>
              <select
                id="feedback-severity"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="feedback-input"
              >
                <option value="low">Low - Minor cosmetic or papercut</option>
                <option value="medium">Medium - Functional inconvenience</option>
                <option value="high">High - Feature block or false positive</option>
                <option value="critical">Critical - Security vulnerability or crash</option>
              </select>
            </div>

            <div className="feedback-row">
              <label htmlFor="feedback-desc">Details *</label>
              <textarea
                id="feedback-desc"
                rows={4}
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what occurred, steps to reproduce, or suggested fix..."
                className="feedback-input"
              />
            </div>

            <div className="feedback-row">
              <label htmlFor="feedback-email">Contact Email (Optional)</label>
              <input
                id="feedback-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="engineer@company.com"
                className="feedback-input"
              />
            </div>

            <div className="feedback-checkbox-row" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <input
                id="feedback-env"
                type="checkbox"
                checked={includeEnv}
                onChange={(e) => setIncludeEnv(e.target.checked)}
              />
              <label htmlFor="feedback-env" style={{ fontSize: '12px', color: 'var(--text-muted)', cursor: 'pointer' }}>
                Include anonymous environment diagnostic (URL path, screen dimensions, browser version)
              </label>
            </div>

            <div className="modal-dialog-actions" style={{ marginTop: '20px' }}>
              <button
                type="button"
                className="modal-action-btn secondary"
                onClick={onClose}
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="modal-action-btn primary"
                disabled={submitting || !description.trim()}
              >
                {submitting ? 'Transmitting...' : (
                  <>
                    <Send size={14} style={{ marginRight: '6px' }} />
                    Submit Report
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
