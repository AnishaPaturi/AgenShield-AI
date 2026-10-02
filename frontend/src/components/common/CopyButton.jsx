import React, { useState } from 'react'
import { Copy, Check } from 'lucide-react'

export default function CopyButton({
  text,
  label = null,
  ariaLabel = 'Copy to clipboard',
  className = '',
  size = 14,
  style = {},
}) {
  const [copied, setCopied] = useState(false)
  const [failed, setFailed] = useState(false)

  const handleCopy = async (e) => {
    e.stopPropagation()
    e.preventDefault()

    if (!text) return

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text)
      } else {
        // Fallback for older browsers / non-secure contexts
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }

      setCopied(true)
      setFailed(false)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setFailed(true)
      setTimeout(() => setFailed(false), 2000)
    }
  }

  return (
    <button
      type="button"
      className={`copy-btn ${copied ? 'copied' : ''} ${className}`}
      onClick={handleCopy}
      aria-label={copied ? 'Copied to clipboard' : ariaLabel}
      title={copied ? 'Copied!' : failed ? 'Failed to copy' : ariaLabel}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        background: copied
          ? 'var(--ok-bg, rgba(52, 211, 153, 0.12))'
          : 'var(--surface-2-glass, rgba(255, 255, 255, 0.05))',
        border: copied
          ? '1px solid var(--ok-border, rgba(52, 211, 153, 0.35))'
          : '1px solid var(--border-subtle, rgba(255, 255, 255, 0.1))',
        borderRadius: '6px',
        padding: '3px 8px',
        color: copied ? 'var(--ok, #34D399)' : 'var(--text-muted, #94A3B8)',
        fontSize: '11px',
        fontFamily: 'JetBrains Mono, monospace',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        ...style,
      }}
    >
      {copied ? <Check size={size} strokeWidth={2.5} /> : <Copy size={size} />}
      {label && <span>{copied ? 'Copied' : label}</span>}
      {!label && copied && <span>Copied</span>}
    </button>
  )
}
