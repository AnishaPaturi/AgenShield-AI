import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldAlert, ArrowLeft, Terminal } from 'lucide-react'

export default function NotFound() {
  const token = localStorage.getItem('agentshield_token')

  return (
    <div className="not-found-page-root" style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg, #060812)',
      color: 'var(--text, #F8FAFC)',
      padding: '24px'
    }}>
      <div style={{
        maxWidth: '520px',
        width: '100%',
        textAlign: 'center',
        padding: '48px 32px',
        background: 'var(--surface-glass, rgba(14, 19, 34, 0.75))',
        border: '1px solid var(--border, rgba(167, 139, 250, 0.15))',
        borderRadius: '16px',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 24px 60px rgba(0,0,0,0.5)'
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'var(--crit-bg, rgba(251, 113, 133, 0.12))',
          border: '1px solid var(--crit-border, rgba(251, 113, 133, 0.3))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 24px'
        }}>
          <ShieldAlert size={32} color="var(--crit, #FB7185)" />
        </div>

        <div style={{
          fontFamily: 'var(--mono)',
          fontSize: '12px',
          color: 'var(--primary)',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          marginBottom: '8px'
        }}>
          [ 404 : ROUTE UNMAPPED ]
        </div>

        <h1 style={{ fontSize: '28px', fontWeight: 800, margin: '0 0 12px', letterSpacing: '-0.02em' }}>
          Signal Not Found
        </h1>

        <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.6, marginBottom: '28px' }}>
          The requested coordinate does not exist in the security topology or has been decommissioned by the orchestrator.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link
            to={token ? "/home" : "/"}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, var(--primary, #A78BFA), #8B5CF6)',
              color: '#FFFFFF',
              fontWeight: 600,
              fontSize: '13px',
              textDecoration: 'none'
            }}
          >
            <ArrowLeft size={16} />
            {token ? 'Return to Security Console' : 'Return to Homepage'}
          </Link>

          <Link
            to="/scan"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '8px',
              background: 'var(--surface-2-glass, rgba(255, 255, 255, 0.05))',
              border: '1px solid var(--border)',
              color: 'var(--text)',
              fontWeight: 600,
              fontSize: '13px',
              textDecoration: 'none'
            }}
          >
            <Terminal size={15} />
            Launch Scanner
          </Link>
        </div>
      </div>
    </div>
  )
}
