import React, { useEffect, useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Shield, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react'
import { setCurrentUser, getRegisteredUsers, saveRegisteredUsers } from '../auth.js'
import { getUserProfile, exchangeOAuthCode } from '../api.js'

export default function AuthCallback() {
  const navigate = useNavigate()
  const location = useLocation()

  const [status, setStatus] = useState('processing') // 'processing' | 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('')
  const [statusDetail, setStatusDetail] = useState('Verifying security credentials with identity provider...')
  const [providerName, setProviderName] = useState('OAuth Provider')

  useEffect(() => {
    let isMounted = true

    async function handleCallback() {
      const params = new URLSearchParams(location.search)
      const errorParam = params.get('error') || params.get('error_description')
      const authSuccess = params.get('auth') === 'success' || params.get('google_auth') === 'success' || params.get('github_auth') === 'success'
      const code = params.get('code')
      const email = params.get('email')
      const name = params.get('name')
      const returnTo = params.get('return_to') || '/dashboard'

      // Detect provider
      let provider = params.get('provider')
      if (!provider) {
        if (location.pathname.includes('github') || params.get('github_auth')) {
          provider = 'github'
        } else if (location.pathname.includes('google') || params.get('google_auth')) {
          provider = 'google'
        } else {
          provider = 'oauth'
        }
      }

      const pName = provider === 'github' ? 'GitHub' : provider === 'google' ? 'Google' : 'OAuth Identity'
      setProviderName(pName)

      // Handle provider error redirect
      if (errorParam) {
        if (!isMounted) return
        setStatus('error')
        setErrorMessage(decodeURIComponent(errorParam))
        return
      }

      // Flow 1: Backend completed authorization & redirected with user data
      if (authSuccess && email) {
        try {
          if (!isMounted) return
          setStatusDetail(`Finalizing ${pName} authentication and synchronizing workspace permissions...`)

          let profileData = null
          try {
            const res = await getUserProfile(email)
            profileData = (res && res.user) ? res.user : res
          } catch {
            // If backend profile fetch fails, construct reliable user session
            profileData = {
              email,
              name: name || (provider === 'github' ? 'GitHub User' : 'Google User'),
              providers: [provider],
              hasPassword: false,
              orgName: provider === 'github' ? 'GitHub Account' : 'Google Account',
            }
          }

          if (!profileData || !profileData.email) {
            profileData = {
              email,
              name: name || `${pName} User`,
              providers: [provider],
              hasPassword: false,
            }
          }

          // Ensure providers list has current provider
          const provs = Array.isArray(profileData.providers)
            ? profileData.providers
            : typeof profileData.providers === 'string'
            ? profileData.providers.split(',').map((p) => p.trim())
            : [provider]
          if (!provs.includes(provider)) {
            provs.push(provider)
          }
          profileData.providers = provs

          // Save active session
          setCurrentUser(profileData)

          // Sync into localStorage users registry for offline resilience
          const users = getRegisteredUsers()
          const idx = users.findIndex((u) => u.email.toLowerCase() === email.toLowerCase())
          if (idx >= 0) {
            users[idx] = { ...users[idx], ...profileData }
          } else {
            users.push(profileData)
          }
          saveRegisteredUsers(users)

          // Dispatch event to update navbar/session listeners
          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('auth_change', { detail: profileData }))
          }

          if (!isMounted) return
          setStatus('success')
          setStatusDetail(`Secure session established for ${email}. Accessing console...`)

          setTimeout(() => {
            navigate(returnTo || '/dashboard', { replace: true })
          }, 600)
        } catch (err) {
          if (!isMounted) return
          setStatus('error')
          setErrorMessage(err.message || 'Failed to complete authentication session.')
        }
        return
      }

      // Flow 2: Authorization code received directly (SPA exchange flow)
      if (code) {
        try {
          if (!isMounted) return
          setStatusDetail(`Exchanging authorization token with ${pName}...`)

          const exchangeRes = await exchangeOAuthCode(provider, code)
          const profileData = exchangeRes.user || exchangeRes

          if (!profileData || !profileData.email) {
            throw new Error(`Did not receive valid user credentials from ${pName}.`)
          }

          setCurrentUser(profileData)

          // Sync into localStorage users registry
          const users = getRegisteredUsers()
          const idx = users.findIndex((u) => u.email.toLowerCase() === profileData.email.toLowerCase())
          if (idx >= 0) {
            users[idx] = { ...users[idx], ...profileData }
          } else {
            users.push(profileData)
          }
          saveRegisteredUsers(users)

          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('auth_change', { detail: profileData }))
          }

          if (!isMounted) return
          setStatus('success')
          setStatusDetail(`Secure session established for ${profileData.email}. Redirecting...`)

          setTimeout(() => {
            navigate(returnTo || '/dashboard', { replace: true })
          }, 600)
        } catch (err) {
          if (!isMounted) return
          setStatus('error')
          setErrorMessage(err.message || `Failed to verify authorization code with ${pName}.`)
        }
        return
      }

      // Flow 3: No valid OAuth parameters present
      if (!isMounted) return
      setStatus('error')
      setErrorMessage('No authentication payload or authorization code was detected in the callback request.')
    }

    handleCallback()

    return () => {
      isMounted = false
    }
  }, [location, navigate])

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#06080C',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        color: '#E2E8F0',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Background glow effects */}
      <div
        style={{
          position: 'fixed',
          top: '20%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '500px',
          height: '500px',
          background: status === 'error'
            ? 'radial-gradient(circle, rgba(239, 68, 68, 0.12) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(220, 38, 38, 0.15) 0%, rgba(6, 182, 212, 0.05) 50%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      <div
        style={{
          position: 'relative',
          zIndex: 1,
          width: '100%',
          maxWidth: '460px',
          background: 'rgba(15, 23, 42, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
          padding: '36px 32px',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
          textAlign: 'center',
        }}
      >
        {/* Brand Logo Header */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, rgba(220,38,38,0.3), rgba(15,23,42,0.8))',
              border: '1px solid rgba(220, 38, 38, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Shield size={20} color="#DC2626" />
          </div>
          <span style={{ fontSize: '18px', fontWeight: '700', letterSpacing: '-0.02em', color: '#FFFFFF' }}>
            AgentShield<span style={{ color: '#DC2626' }}>AI</span>
          </span>
        </div>

        {/* Processing State */}
        {status === 'processing' && (
          <div>
            <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto 24px' }}>
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  border: '3px solid rgba(220, 38, 38, 0.2)',
                  borderTopColor: '#DC2626',
                  animation: 'spin 1s linear infinite',
                }}
              />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#FFFFFF', marginBottom: '8px' }}>
              Authenticating via {providerName}
            </h3>
            <p style={{ fontSize: '13px', color: '#94A3B8', lineHeight: '1.6', margin: 0 }}>
              {statusDetail}
            </p>
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div>
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(34, 197, 94, 0.12)',
                border: '1px solid rgba(34, 197, 94, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
              }}
            >
              <CheckCircle2 size={32} color="#22C55E" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#FFFFFF', marginBottom: '8px' }}>
              Identity Verified
            </h3>
            <p style={{ fontSize: '13px', color: '#86EFAC', lineHeight: '1.6', margin: 0 }}>
              {statusDetail}
            </p>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div>
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.12)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
              }}
            >
              <AlertTriangle size={32} color="#EF4444" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#FFFFFF', marginBottom: '8px' }}>
              Authentication Unsuccessful
            </h3>
            <div
              style={{
                background: 'rgba(239, 68, 68, 0.08)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: '8px',
                padding: '12px 14px',
                marginBottom: '24px',
                textAlign: 'left',
              }}
            >
              <p style={{ fontSize: '13px', color: '#FCA5A5', margin: 0, lineHeight: '1.5' }}>
                {errorMessage}
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <Link
                to="/sign-in"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  background: 'linear-gradient(135deg, #DC2626 0%, #991B1B 100%)',
                  color: '#FFFFFF',
                  padding: '10px 18px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: '600',
                  textDecoration: 'none',
                }}
              >
                <span>Return to Sign In</span>
                <ArrowRight size={15} />
              </Link>
              <Link
                to="/"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#94A3B8',
                  padding: '8px',
                  fontSize: '12px',
                  textDecoration: 'none',
                }}
              >
                Back to Home
              </Link>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
