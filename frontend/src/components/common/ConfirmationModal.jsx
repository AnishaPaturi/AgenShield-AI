import React, { useEffect, useRef } from 'react'
import { AlertTriangle, X } from 'lucide-react'

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  description = 'Are you sure you want to proceed? This action may not be reversible.',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  danger = true,
  loading = false,
}) {
  const modalRef = useRef(null)
  const cancelButtonRef = useRef(null)

  useEffect(() => {
    if (!isOpen) return

    // Focus cancel button on mount for safety
    if (cancelButtonRef.current) {
      cancelButtonRef.current.focus()
    }

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.stopPropagation()
        onClose()
      } else if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement?.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement?.focus()
            e.preventDefault()
          }
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = prevOverflow
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      className="modal-backdrop-portal"
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) onClose()
      }}
      role="presentation"
    >
      <div
        ref={modalRef}
        className="accessible-modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-modal-title"
        aria-describedby="confirm-modal-desc"
      >
        <div className="modal-dialog-header">
          <div className="modal-dialog-icon-wrapper" style={{
            background: danger ? 'var(--crit-bg, rgba(251, 113, 133, 0.12))' : 'var(--primary-dim)',
            borderColor: danger ? 'var(--crit-border, rgba(251, 113, 133, 0.3))' : 'var(--primary-border)'
          }}>
            <AlertTriangle
              size={20}
              color={danger ? 'var(--crit, #FB7185)' : 'var(--primary, #A78BFA)'}
              aria-hidden="true"
            />
          </div>
          <div className="modal-dialog-title-block">
            <h3 id="confirm-modal-title">{title}</h3>
            <p id="confirm-modal-desc">{description}</p>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            disabled={loading}
            aria-label="Close dialog"
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>

        <div className="modal-dialog-actions">
          <button
            ref={cancelButtonRef}
            type="button"
            className="modal-action-btn secondary"
            onClick={onClose}
            disabled={loading}
          >
            {cancelText}
          </button>
          <button
            type="button"
            className={`modal-action-btn ${danger ? 'danger' : 'primary'}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
