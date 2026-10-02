import React, { useState, useEffect } from 'react'
import { Shield, Check, X } from 'lucide-react'

import { getCurrentUser } from '../../auth.js'

export default function CookieBanner() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    try {
      const consent = localStorage.getItem('agentshield_cookie_consent')
      const user = getCurrentUser()
      const path = window.location.pathname

      // Cookie banner is strictly for public informational/marketing pages
      const isPublicPage = path === '/' || path === '/privacy' || path === '/terms'

      if (user || consent || !isPublicPage) {
        setVisible(false)
        return
      }

      const timer = setTimeout(() => setVisible(true), 1200)
      return () => clearTimeout(timer)
    } catch {
      // ignore
    }

    const handleAuth = () => {
      if (getCurrentUser()) {
        setVisible(false)
      }
    }
    window.addEventListener('auth_change', handleAuth)
    return () => window.removeEventListener('auth_change', handleAuth)
  }, [])

  const handleChoice = (level) => {
    try {
      localStorage.setItem(
        'agentshield_cookie_consent',
        JSON.stringify({
          level,
          timestamp: new Date().toISOString(),
          version: '1.0'
        })
      )
    } catch {
      // ignore
    }
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div
      className="cookie-banner-bar"
      role="region"
      aria-label="Cookie and telemetry consent"
    >
      <div className="cookie-banner-inner">
        <div className="cookie-banner-content">
          <div className="cookie-icon-box">
            <Shield size={18} color="var(--primary, #A78BFA)" />
          </div>
          <div className="cookie-text-box">
            <p className="cookie-banner-title">Data Privacy & Storage Integrity</p>
            <p className="cookie-banner-desc">
              AgentShield uses strictly essential browser storage to preserve your authenticated session, cryptographic CSRF tokens, and interface preferences. We do not sell telemetry or track cross-site activity. Review our{' '}
              <a href="/privacy" className="cookie-link">Privacy Policy</a> and{' '}
              <a href="/terms" className="cookie-link">Terms</a>.
            </p>
          </div>
        </div>

        <div className="cookie-banner-actions">
          <button
            type="button"
            className="cookie-btn cookie-btn-subtle"
            onClick={() => handleChoice('essential_only')}
          >
            Essential Only
          </button>
          <button
            type="button"
            className="cookie-btn cookie-btn-primary"
            onClick={() => handleChoice('all')}
          >
            Accept All
          </button>
        </div>
      </div>
    </div>
  )
}
