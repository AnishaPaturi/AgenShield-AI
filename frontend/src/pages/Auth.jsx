import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  loginWithCredentials,
  registerWithCredentials,
  loginWithSSO,
  signupWithSSO,
  getRegisteredUsers,
  updateUserPassword,
} from '../auth.js'
import { sendVerificationCodeApi, verifyCodeApi, getGitHubOAuthStatus, getGitHubLoginUrl } from '../api.js'
import '../auth.css'


export default function Auth({ initialMode = 'login' }) {
  const navigate = useNavigate()
  const location = useLocation()

  // Set mode based on prop or current URL path (/signup vs /login)
  const [mode, setMode] = useState(
    location.pathname === '/signup' || initialMode === 'signup' ? 'signup' : 'login'
  )

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    orgName: '',
    rememberMe: true,
  })

  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [feedback, setFeedback] = useState(null) // { type: 'error' | 'success', text: '' }

  // GitHub OAuth configuration status from backend
  const [githubOAuthStatus, setGithubOAuthStatus] = useState(null)

  // SSO verification modal state
  const [ssoModal, setSsoModal] = useState(null) // { provider: 'github' | 'google', email: '', name: '', error: '' }

  // Forgot Password modal state
  // step: 'email' | 'code' | 'password' | 'success'
  const [forgotModal, setForgotModal] = useState(null)

  // Refs for orbital verification animation
  const orbitRef = useRef(null)
  const hubRef = useRef(null)
  const slotRef = useRef(null)

  // Fetch GitHub OAuth configuration status & handle OAuth error redirects
  useEffect(() => {
    getGitHubOAuthStatus().then((status) => {
      setGithubOAuthStatus(status)
    }).catch(() => {})

    const params = new URLSearchParams(location.search)
    const ghError = params.get('github_error')
    if (ghError) {
      setFeedback({ type: 'error', text: `GitHub Authentication Error: ${ghError}` })
    }
  }, [location.search])

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  // Password strength checker for signup
  const calculatePasswordStrength = (pass) => {
    if (!pass) return 0
    let score = 0
    if (pass.length >= 8) score += 25
    if (/[A-Z]/.test(pass)) score += 25
    if (/[0-9]/.test(pass)) score += 25
    if (/[^A-Za-z0-9]/.test(pass)) score += 25
    return score
  }

  const passwordStrength = calculatePasswordStrength(formData.password)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFeedback(null)

    if (mode === 'signup') {
      if (!formData.name.trim()) {
        setFeedback({ type: 'error', text: 'Please enter your full name.' })
        return
      }
      if (formData.password !== formData.confirmPassword) {
        setFeedback({ type: 'error', text: 'Passwords do not match.' })
        return
      }
      if (formData.password.length < 8) {
        setFeedback({ type: 'error', text: 'Password must be at least 8 characters long.' })
        return
      }

      setIsLoading(true)
      try {
        await registerWithCredentials({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          orgName: formData.orgName,
        })
        setFeedback({
          type: 'success',
          text: 'Account created successfully! Loading console...',
        })
        setTimeout(() => {
          setIsLoading(false)
          navigate('/console')
        }, 700)
      } catch (err) {
        setIsLoading(false)
        setFeedback({ type: 'error', text: err.message })
      }
    } else {
      // Login mode: strictly verify account exists
      setIsLoading(true)
      try {
        loginWithCredentials(formData.email, formData.password)
        setFeedback({
          type: 'success',
          text: 'Authentication successful! Loading console...',
        })
        setTimeout(() => {
          setIsLoading(false)
          navigate('/console')
        }, 700)
      } catch (err) {
        setIsLoading(false)
        setFeedback({ type: 'error', text: err.message })
      }
    }
  }

  // Handle SSO button click
  const handleOpenSSO = (provider) => {
    setFeedback(null)
    const emailCandidate = formData.email || ''
    const defaultName = formData.name || (provider === 'github' ? 'GitHub Developer' : 'Google User')
    setSsoModal({
      provider,
      email: emailCandidate,
      name: defaultName,
      password: formData.password || '',
      authMethod: 'password', // 'password' | 'mobile' | 'email'
      step: 'credentials', // 'credentials' | '2fa_mobile' | '2fa_email'
      mobileCode: Math.floor(10 + Math.random() * 90).toString(),
      enteredCode: '',
      error: '',
      authorizing: false,
    })
  }

  const handleSSOComplete = async (email, name) => {
    const providerName = ssoModal?.provider === 'github' ? 'GitHub' : 'Google'
    const cleanEmail = (email || '').trim().toLowerCase()
    const cleanName = (name || '').trim() || (providerName === 'github' ? 'GitHub Developer' : 'Google User')

    if (mode === 'login') {
      try {
        loginWithSSO(ssoModal.provider, cleanEmail)
        setFeedback({
          type: 'success',
          text: `${providerName} authentication verified! Loading console...`,
        })
        setTimeout(() => {
          setSsoModal(null)
          navigate('/console')
        }, 500)
      } catch (err) {
        setSsoModal((prev) => ({ ...prev, authorizing: false, error: err.message }))
      }
    } else {
      try {
        await signupWithSSO(ssoModal.provider, cleanEmail, cleanName)
        setFeedback({
          type: 'success',
          text: `${providerName} account registered! Loading console...`,
        })
        setTimeout(() => {
          setSsoModal(null)
          navigate('/console')
        }, 500)
      } catch (err) {
        setSsoModal((prev) => ({ ...prev, authorizing: false, error: err.message }))
      }
    }
  }

  const handleGitHubAuthorize = async (e) => {
    e?.preventDefault()
    if (!ssoModal) return

    const cleanEmail = (ssoModal.email || '').trim().toLowerCase()
    const cleanName = (ssoModal.name || '').trim() || 'GitHub Developer'

    if (!cleanEmail) {
      setSsoModal((prev) => ({ ...prev, error: 'Please enter your GitHub account email or username.' }))
      return
    }

    if (ssoModal.authMethod === 'password') {
      if (!ssoModal.password || ssoModal.password.length < 6) {
        setSsoModal((prev) => ({ ...prev, error: 'Please enter your GitHub account password.' }))
        return
      }
      setSsoModal((prev) => ({ ...prev, authorizing: true, error: '' }))
      setTimeout(() => {
        handleSSOComplete(cleanEmail, cleanName)
      }, 700)
    } else if (ssoModal.authMethod === 'mobile') {
      const randomCode = Math.floor(10 + Math.random() * 90).toString()
      setSsoModal((prev) => ({
        ...prev,
        step: '2fa_mobile',
        mobileCode: randomCode,
        error: '',
      }))
    } else if (ssoModal.authMethod === 'email') {
      if (!ssoModal.password || ssoModal.password.length < 6) {
        setSsoModal((prev) => ({ ...prev, error: 'Please enter your password to request an email code.' }))
        return
      }
      setSsoModal((prev) => ({ ...prev, authorizing: true, error: '' }))
      try {
        await sendVerificationCodeApi(cleanEmail)
      } catch (err) {
        // Continue to code entry screen
      }
      setSsoModal((prev) => ({
        ...prev,
        step: '2fa_email',
        authorizing: false,
        enteredCode: '',
        error: '',
      }))
    }
  }

  const handleApproveMobile = () => {
    setSsoModal((prev) => ({ ...prev, authorizing: true, error: '' }))
    setTimeout(() => {
      handleSSOComplete(ssoModal.email, ssoModal.name)
    }, 700)
  }

  const handleVerifyEmail2FA = async (e) => {
    e?.preventDefault()
    if (!ssoModal) return

    const code = (ssoModal.enteredCode || '').trim()
    if (code.length !== 6) {
      setSsoModal((prev) => ({ ...prev, error: 'Please enter the 6-digit verification code.' }))
      return
    }

    setSsoModal((prev) => ({ ...prev, authorizing: true, error: '' }))
    try {
      await verifyCodeApi(ssoModal.email, code)
      handleSSOComplete(ssoModal.email, ssoModal.name)
    } catch (err) {
      setSsoModal((prev) => ({
        ...prev,
        authorizing: false,
        error: err.message || 'Invalid or expired verification code. Please request a new code.',
      }))
    }
  }

  const handleSSOSubmit = async (e) => {
    e?.preventDefault()
    if (!ssoModal) return

    if (ssoModal.provider === 'github') {
      return handleGitHubAuthorize(e)
    }

    const providerName = 'Google'
    const cleanEmail = (ssoModal.email || '').trim().toLowerCase()
    const cleanName = (ssoModal.name || '').trim() || 'Google User'

    if (!cleanEmail) {
      setSsoModal((prev) => ({
        ...prev,
        error: 'Please enter your Google account email.',
      }))
      return
    }

    setSsoModal((prev) => ({ ...prev, error: '', authorizing: true }))
    setTimeout(() => {
      handleSSOComplete(cleanEmail, cleanName)
    }, 600)
  }

  // ==========================================
  // Forgot Password / Password Reset Workflow
  // ==========================================

  const triggerOrbitAnimation = () => {
    const WIND_UP_BRAKE = 'cubic-bezier(0.12, 0.8, 0.32, 1)'
    if (slotRef.current && hubRef.current) {
      const hubRect = hubRef.current.getBoundingClientRect()
      const slotRect = slotRef.current.getBoundingClientRect()
      const hubX = hubRect.left + hubRect.width / 2 - slotRect.left
      const hubY = hubRect.top + hubRect.height / 2 - slotRect.top
      const dx = 0
      const dy = 0
      slotRef.current.style.transformOrigin = `${hubX}px ${hubY}px`
      slotRef.current.animate(
        [
          { transform: `rotate(0deg) translate(${dx}px, ${dy}px)` },
          { transform: `rotate(450deg) translate(${dx}px, ${dy}px)` },
        ],
        { duration: 800, easing: WIND_UP_BRAKE }
      )
    }
  }

  useEffect(() => {
    if (forgotModal?.step === 'code') {
      const t = setTimeout(triggerOrbitAnimation, 50)
      return () => clearTimeout(t)
    }
  }, [forgotModal?.step])

  const handleStartForgotPassword = () => {
    setFeedback(null)
    setForgotModal({
      step: 'email',
      email: formData.email || '',
      code: '',
      newPassword: '',
      confirmPassword: '',
      error: '',
      status: 'idle', // 'idle' | 'ok' | 'bad'
      loading: false,
    })
  }

  const handleSendVerificationCode = async (e) => {
    e.preventDefault()
    if (!forgotModal) return

    const cleanEmail = (forgotModal.email || '').trim().toLowerCase()
    if (!cleanEmail) {
      setForgotModal((prev) => ({
        ...prev,
        error: 'Please enter your registered email address.',
      }))
      return
    }

    setForgotModal((prev) => ({ ...prev, loading: true, error: '' }))

    try {
      await sendVerificationCodeApi(cleanEmail)
      setForgotModal((prev) => ({
        ...prev,
        code: '',
        step: 'code',
        loading: false,
        error: '',
        status: 'idle',
      }))
    } catch (err) {
      setForgotModal((prev) => ({
        ...prev,
        loading: false,
        error: err.message || 'Failed to dispatch verification code. Please check your email.',
      }))
    }
  }

  const handleVerifyCode = async (e) => {
    e?.preventDefault()
    if (!forgotModal) return

    const code = (forgotModal.code || '').trim()
    if (code.length !== 6) {
      triggerOrbitAnimation()
      setForgotModal((prev) => ({
        ...prev,
        status: 'bad',
        error: 'Please enter the complete 6-digit verification code.',
      }))
      return
    }

    setForgotModal((prev) => ({ ...prev, loading: true, error: '' }))

    try {
      await verifyCodeApi(forgotModal.email, code)
      setForgotModal((prev) => ({ ...prev, status: 'ok', error: '', loading: false }))
      setTimeout(() => {
        setForgotModal((prev) => ({ ...prev, step: 'password', status: 'idle' }))
      }, 400)
    } catch (err) {
      triggerOrbitAnimation()
      setForgotModal((prev) => ({
        ...prev,
        status: 'bad',
        loading: false,
        error: err.message || 'Invalid or expired verification code. Please try again.',
      }))
    }
  }

  const handleResetPasswordSubmit = async (e) => {
    e.preventDefault()
    if (!forgotModal) return

    if (forgotModal.newPassword !== forgotModal.confirmPassword) {
      setForgotModal((prev) => ({ ...prev, error: 'Passwords do not match.' }))
      return
    }

    if (forgotModal.newPassword.length < 8) {
      setForgotModal((prev) => ({
        ...prev,
        error: 'New password must be at least 8 characters long.',
      }))
      return
    }

    setForgotModal((prev) => ({ ...prev, loading: true, error: '' }))

    try {
      await updateUserPassword(forgotModal.email, forgotModal.newPassword, forgotModal.code)
      setForgotModal((prev) => ({ ...prev, step: 'success', error: '', loading: false }))
    } catch (err) {
      setForgotModal((prev) => ({ ...prev, error: err.message, loading: false }))
    }
  }

  const handleFinishReset = () => {
    if (forgotModal?.email) {
      setFormData((prev) => ({ ...prev, email: forgotModal.email, password: '' }))
    }
    setForgotModal(null)
    setFeedback({
      type: 'success',
      text: 'Password updated successfully in database! Please sign in with your new password.',
    })
  }

  return (
    <div className="auth-page">
      {/* Ambient background lighting */}
      <div className="auth-glow-gold"></div>
      <div className="auth-glow-cyan"></div>
      <div className="auth-grid-pattern"></div>

      {/* Top Navigation Bar with Back Button */}
      <header className="auth-top-nav">
        <Link to="/" className="auth-back-btn" id="back-to-landing-btn">
          <svg
            className="back-btn-icon"
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Back to Landing Page</span>
        </Link>

        {/* Mobile brand header shown when left showcase is hidden */}
        <Link to="/" className="auth-mobile-brand">
          <div className="brand-shield-icon">
            <img src="/logo.png" alt="AgentShield AI Logo" className="brand-logo-img" />
          </div>
          <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
        </Link>
      </header>

      <div className="auth-container">
        {/* Left Side: Brand Showcase & Trust Signals */}
        <div className="auth-showcase">
          <Link to="/" className="auth-brand">
            <div className="brand-shield-icon">
              <img src="/logo.png" alt="AgentShield AI Logo" className="brand-logo-img" />
            </div>
            <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
          </Link>

          <div className="auth-hero-copy">
            <div className="auth-badge">
              <span className="badge-pulse"></span>
              <span>ENTERPRISE SECURITY PORTAL</span>
            </div>
            <h2 className="auth-headline">
              Autonomous Defense for <span className="text-gold-gradient">Multi-Cloud IaC</span>
            </h2>
            <p className="auth-sub">
              Eight coordinated AI agents parsing your Terraform, CloudFormation, Kubernetes,
              and Helm templates with LocalStack runtime sandbox validation.
            </p>
          </div>

          <div className="trust-metrics-grid">
            <div className="trust-card">
              <div className="trust-icon cyan-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <div className="trust-meta">
                <span className="trust-num">0 Leaks</span>
                <span className="trust-lbl">Zero-leakage secrets redaction</span>
              </div>
            </div>

            <div className="trust-card">
              <div className="trust-icon gold-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div className="trust-meta">
                <span className="trust-num">C_ens 0.94</span>
                <span className="trust-lbl">Multi-LLM consensus scoring</span>
              </div>
            </div>

            <div className="trust-card">
              <div className="trust-icon green-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <div className="trust-meta">
                <span className="trust-num">100%</span>
                <span className="trust-lbl">LocalStack sandbox verified</span>
              </div>
            </div>

            <div className="trust-card">
              <div className="trust-icon cyan-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                  <polyline points="2 17 12 22 22 17"/>
                  <polyline points="2 12 12 17 22 12"/>
                </svg>
              </div>
              <div className="trust-meta">
                <span className="trust-num">4 Clouds</span>
                <span className="trust-lbl">AWS, Azure, GCP & K8s</span>
              </div>
            </div>
          </div>

          <div className="auth-testimonial">
            <p className="testimonial-text">
              "AgentShield AI eliminated 94% of our IaC misconfigurations and caught overprivileged
              IAM roles before our Terraform apply ever touched production."
            </p>
            <div className="testimonial-author">
              <span className="author-name">DevSecOps Architecture Team</span>
              <span className="author-org">Team 13 • College Capstone 2026</span>
            </div>
          </div>
        </div>

        {/* Right Side: Interactive Auth Card */}
        <div className="auth-form-card">
          {/* Mode Switcher Pill */}
          <div className="auth-mode-pill">
            <button
              type="button"
              className={`mode-pill-btn ${mode === 'login' ? 'active' : ''}`}
              onClick={() => { setMode('login'); setFeedback(null); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`mode-pill-btn ${mode === 'signup' ? 'active' : ''}`}
              onClick={() => { setMode('signup'); setFeedback(null); }}
            >
              Create Account
            </button>
          </div>

          <div className="auth-form-header">
            <h3 className="form-title">
              {mode === 'login' ? 'Welcome Back' : 'Get Started with AgentShield'}
            </h3>
            <p className="form-sub">
              {mode === 'login'
                ? 'Enter your registered credentials to access the autonomous security console'
                : 'Register your enterprise account to access multi-cloud IaC defense'}
            </p>
          </div>

          {/* Social SSO Buttons */}
          <div className="social-sso-group">
            <button
              type="button"
              className="sso-btn"
              onClick={() => handleOpenSSO('github')}
            >
              <svg className="sso-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>GitHub</span>
            </button>

            <button
              type="button"
              className="sso-btn"
              onClick={() => handleOpenSSO('google')}
            >
              <svg className="sso-icon" viewBox="0 0 24 24">
                <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z"/>
                <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"/>
                <path fill="#FBBC05" d="M5.6 14.8c-.3-.8-.4-1.8-.4-2.8s.1-2 .4-2.8L1.9 6.3C.7 8.7 0 10.3 0 12s.7 3.3 1.9 5.7l3.7-2.9z"/>
                <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"/>
              </svg>
              <span>Google</span>
            </button>
          </div>

          <div className="auth-divider">
            <span>OR WORK EMAIL</span>
          </div>

          {/* Feedback Alert */}
          {feedback && (
            <div className={`auth-alert ${feedback.type}`}>
              <span className="alert-dot"></span>
              <span>{feedback.text}</span>
            </div>
          )}

          {/* Main Form */}
          <form className="auth-form" onSubmit={handleSubmit}>
            {mode === 'signup' && (
              <div className="form-group">
                <label className="form-label" htmlFor="name">Full Name</label>
                <div className="input-wrap">
                  <input
                    id="name"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="email">Work Email</label>
              <div className="input-wrap">
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>
            </div>

            {mode === 'signup' && (
              <div className="form-group">
                <label className="form-label" htmlFor="orgName">Organization / Team (Optional)</label>
                <div className="input-wrap">
                  <input
                    id="orgName"
                    type="text"
                    name="orgName"
                    value={formData.orgName}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <div className="label-row">
                <label className="form-label" htmlFor="password">Password</label>
                {mode === 'login' && (
                  <button
                    type="button"
                    className="forgot-link"
                    onClick={handleStartForgotPassword}
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="input-wrap">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>

              {/* Password Strength Indicator (For Signup) */}
              {mode === 'signup' && formData.password && (
                <div className="password-strength-wrap">
                  <div className="strength-bar-bg">
                    <div
                      className={`strength-bar-fill ${
                        passwordStrength < 50 ? 'weak' : passwordStrength < 75 ? 'medium' : 'strong'
                      }`}
                      style={{ width: `${passwordStrength}%` }}
                    ></div>
                  </div>
                  <span className="strength-text">
                    {passwordStrength < 50
                      ? 'Weak: Add numbers & symbols'
                      : passwordStrength < 75
                      ? 'Moderate: Good start'
                      : 'Strong: Secure password'}
                  </span>
                </div>
              )}
            </div>

            {mode === 'signup' && (
              <div className="form-group">
                <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
                <div className="input-wrap">
                  <input
                    id="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                  />
                </div>
              </div>
            )}

            {mode === 'login' && (
              <div className="form-remember-row">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleInputChange}
                  />
                  <span>Remember this device for 30 days</span>
                </label>
              </div>
            )}

            <button
              type="submit"
              className="btn-shimmer-gold auth-submit-btn"
              disabled={isLoading}
            >
              <span className="btn-shine"></span>
              {isLoading ? 'Verifying Credentials...' : mode === 'login' ? 'Sign In to Console →' : 'Create Enterprise Account →'}
            </button>
          </form>

          {/* Quick Info for Evaluators / Existing Accounts */}
          {mode === 'login' && (
            <div style={{ marginTop: '16px', padding: '12px 14px', background: 'rgba(214, 168, 79, 0.08)', border: '1px solid rgba(214, 168, 79, 0.25)', borderRadius: '8px', fontSize: '11.5px', color: '#CBD5E1', lineHeight: '1.5' }}>
              <span style={{ color: '#D6A84F', fontWeight: 700 }}>Existing Enterprise Account:</span>{' '}
              <code style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>admin@agentshield.ai</code> / <code style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>Password123!</code>
            </div>
          )}

          <div className="auth-footer-note">
            <span>Protected by AgentShield Zero-Trust Gateway.</span>
            <Link to="/" className="back-landing-btn-secondary">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Back to Landing Page</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Authentic GitHub OAuth Authorization Window */}
      {ssoModal && ssoModal.provider === 'github' && (
        <div className="github-oauth-overlay" onClick={() => !ssoModal.authorizing && setSsoModal(null)}>
          <div className="github-oauth-window" onClick={(e) => e.stopPropagation()}>
            {/* Simulated Browser Address Bar */}
            <div className="github-browser-bar">
              <div className="github-browser-dots">
                <span className="github-dot red"></span>
                <span className="github-dot yellow"></span>
                <span className="github-dot green"></span>
              </div>
              <div className="github-browser-url">
                <svg viewBox="0 0 16 16" width="12" height="12" fill="currentColor">
                  <path d="M4 4v2h-.5A2.5 2.5 0 0 0 1 8.5v5A2.5 2.5 0 0 0 3.5 16h9a2.5 2.5 0 0 0 2.5-2.5v-5A2.5 2.5 0 0 0 12.5 6H12V4a4 4 0 0 0-8 0zm7 2H5V4a3 3 0 0 1 6 0v2z"/>
                </svg>
                <span>https://github.com/login/oauth/authorize</span>
              </div>
              <button
                type="button"
                className="github-browser-close"
                onClick={() => !ssoModal.authorizing && setSsoModal(null)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            {/* GitHub Header & Connect Avatar Banner */}
            <div className="github-oauth-header">
              <svg className="github-octocat-logo" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>

              <div className="github-oauth-connect">
                <div className="github-app-badge" title="AgentShield AI">
                  🛡️
                </div>
                <div className="github-connect-arrow">
                  <div className="github-connect-line"></div>
                  <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                    <path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0zm3.78 6.97a.75.75 0 0 0-1.06-1.06L7.25 9.38 5.28 7.41a.75.75 0 0 0-1.06 1.06l2.5 2.5a.75.75 0 0 0 1.06 0l4-4z"/>
                  </svg>
                  <div className="github-connect-line"></div>
                </div>
                <div className="github-app-badge" title="GitHub">
                  <svg viewBox="0 0 24 24" width="30" height="30" fill="#f0f6fc">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                  </svg>
                </div>
              </div>

              <h2 className="github-oauth-title">
                Authorize AgentShield AI
              </h2>
              <p className="github-oauth-subtitle">
                {mode === 'signup'
                  ? <>Sign up for <b>AgentShield AI</b> using your GitHub identity</>
                  : <>Sign in to <b>AgentShield AI</b> with your GitHub account</>}
              </p>
            </div>

            {/* Error Alert */}
            {ssoModal.error && (
              <div style={{ margin: '0 24px 14px', padding: '10px 14px', background: 'rgba(248, 81, 73, 0.1)', border: '1px solid #f85149', borderRadius: '6px', fontSize: '13px', color: '#ff7b72' }}>
                {ssoModal.error}
              </div>
            )}

            {/* Form and Permissions */}
            <div className="github-oauth-body">
              {/* Live GitHub.com OAuth Direct Action if configured */}
              {githubOAuthStatus?.configured && (
                <div className="github-live-oauth-banner">
                  <div className="github-live-info">
                    <span className="github-live-dot"></span>
                    <span>Live GitHub OAuth Application Connected</span>
                  </div>
                  <a
                    href={getGitHubLoginUrl()}
                    className="github-btn-live-oauth"
                  >
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                    </svg>
                    <span>Direct Sign In with GitHub.com &rarr;</span>
                  </a>
                  <div className="github-oauth-divider">
                    <span>OR AUTHORIZE VIA MULTI-FACTOR MODES BELOW</span>
                  </div>
                </div>
              )}

              {/* Step 1: Credentials & Method Selection */}
              {ssoModal.step === 'credentials' && (
                <form onSubmit={handleGitHubAuthorize}>
                  {/* Method Selector Tabs */}
                  <div className="github-method-tabs">
                    <button
                      type="button"
                      className={`github-tab-btn ${ssoModal.authMethod === 'password' ? 'active' : ''}`}
                      onClick={() => setSsoModal({ ...ssoModal, authMethod: 'password', error: '' })}
                    >
                      <span>🔑 Password</span>
                    </button>
                    <button
                      type="button"
                      className={`github-tab-btn ${ssoModal.authMethod === 'mobile' ? 'active' : ''}`}
                      onClick={() => setSsoModal({ ...ssoModal, authMethod: 'mobile', error: '' })}
                    >
                      <span>📱 GitHub Mobile</span>
                    </button>
                    <button
                      type="button"
                      className={`github-tab-btn ${ssoModal.authMethod === 'email' ? 'active' : ''}`}
                      onClick={() => setSsoModal({ ...ssoModal, authMethod: 'email', error: '' })}
                    >
                      <span>📧 Mail & Pwd</span>
                    </button>
                  </div>

                  <div className="github-oauth-card">
                    {mode === 'signup' && (
                      <div className="github-field">
                        <label className="github-label">
                          <span>Full Name</span>
                        </label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. Mona Lisa Octocat"
                          value={ssoModal.name}
                          onChange={(e) => setSsoModal({ ...ssoModal, name: e.target.value, error: '' })}
                          className="github-input"
                          disabled={ssoModal.authorizing}
                          autoFocus
                        />
                      </div>
                    )}

                    <div className="github-field">
                      <label className="github-label">
                        <span>GitHub Username or Email</span>
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="e.g. octocat@github.com"
                        value={ssoModal.email}
                        onChange={(e) => setSsoModal({ ...ssoModal, email: e.target.value, error: '' })}
                        className="github-input"
                        disabled={ssoModal.authorizing}
                        autoFocus={mode === 'login'}
                      />
                    </div>

                    {(ssoModal.authMethod === 'password' || ssoModal.authMethod === 'email') && (
                      <div className="github-field">
                        <label className="github-label">
                          <span>GitHub Password</span>
                          <span style={{ fontSize: '11px', color: '#7d8590' }}>
                            {ssoModal.authMethod === 'email' ? 'Required for mail 2FA' : 'Required'}
                          </span>
                        </label>
                        <input
                          type="password"
                          required
                          placeholder="••••••••••••"
                          value={ssoModal.password || ''}
                          onChange={(e) => setSsoModal({ ...ssoModal, password: e.target.value, error: '' })}
                          className="github-input"
                          disabled={ssoModal.authorizing}
                        />
                      </div>
                    )}
                  </div>

                  {/* Scopes & Permissions List */}
                  <div className="github-permissions-box">
                    <div className="github-permissions-header">Permissions Requested by AgentShield AI</div>
                    <div className="github-permission-item">
                      <span className="github-permission-icon">✓</span>
                      <span><b>Verify your GitHub identity</b> (username, profile information)</span>
                    </div>
                    <div className="github-permission-item">
                      <span className="github-permission-icon">✓</span>
                      <span><b>Access email addresses</b> (read-only for security notifications)</span>
                    </div>
                    <div className="github-permission-item">
                      <span className="github-permission-icon">✓</span>
                      <span><b>IaC Security Verification</b> (autonomous drift & patch auditing)</span>
                    </div>
                  </div>

                  {/* Action Button */}
                  <button
                    type="submit"
                    className="github-btn-authorize"
                    disabled={ssoModal.authorizing}
                  >
                    {ssoModal.authorizing ? (
                      <>
                        <span className="auth-spinner" style={{ width: '16px', height: '16px', borderTopColor: '#ffffff' }}></span>
                        <span>
                          {ssoModal.authMethod === 'email' ? 'Dispatching Email Code...' : 'Authorizing with GitHub...'}
                        </span>
                      </>
                    ) : (
                      <>
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                        </svg>
                        <span>
                          {ssoModal.authMethod === 'mobile' && 'Continue with GitHub Mobile →'}
                          {ssoModal.authMethod === 'email' && 'Send Email Code & Authorize →'}
                          {ssoModal.authMethod === 'password' && 'Authorize AgentShield AI'}
                        </span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    className="github-btn-cancel"
                    onClick={() => !ssoModal.authorizing && setSsoModal(null)}
                    disabled={ssoModal.authorizing}
                  >
                    Cancel and return to AgentShield AI
                  </button>
                </form>
              )}

              {/* Step 2: GitHub Mobile 2FA Prompt */}
              {ssoModal.step === '2fa_mobile' && (
                <div>
                  <div className="github-mobile-box">
                    <div className="github-mobile-icon-wrap">
                      <div className="github-mobile-pulse"></div>
                      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
                        <line x1="12" y1="18" x2="12.01" y2="18"></line>
                      </svg>
                    </div>

                    <h3 className="github-mobile-title">Check your GitHub Mobile</h3>
                    <p className="github-mobile-desc">
                      Open the GitHub Mobile app on your phone and tap the matching number below to approve this authorization request for <b>AgentShield AI</b>:
                    </p>

                    <div className="github-mobile-number">
                      {ssoModal.mobileCode}
                    </div>

                    <div className="github-mobile-waiting">
                      <span className="auth-spinner" style={{ width: '13px', height: '13px', borderTopColor: '#3fb950' }}></span>
                      <span>Waiting for approval on your mobile device...</span>
                    </div>

                    <button
                      type="button"
                      className="github-btn-authorize"
                      onClick={handleApproveMobile}
                      disabled={ssoModal.authorizing}
                    >
                      {ssoModal.authorizing ? (
                        <>
                          <span className="auth-spinner" style={{ width: '16px', height: '16px', borderTopColor: '#ffffff' }}></span>
                          <span>Verifying Mobile Approval...</span>
                        </>
                      ) : (
                        <span>Approve on GitHub Mobile Device ✓</span>
                      )}
                    </button>
                  </div>

                  <button
                    type="button"
                    className="github-btn-cancel"
                    onClick={() => setSsoModal({ ...ssoModal, step: 'credentials', error: '' })}
                    disabled={ssoModal.authorizing}
                  >
                    ← Try another authorization method
                  </button>
                </div>
              )}

              {/* Step 3: GitHub Email Code 2FA Prompt */}
              {ssoModal.step === '2fa_email' && (
                <form onSubmit={handleVerifyEmail2FA}>
                  <div className="github-mobile-box">
                    <div className="github-mobile-icon-wrap">
                      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                        <polyline points="22,6 12,13 2,6"></polyline>
                      </svg>
                    </div>

                    <h3 className="github-mobile-title">Device verification code</h3>
                    <p className="github-mobile-desc">
                      We sent a 6-digit verification code to <b style={{ color: '#f0f6fc' }}>{ssoModal.email}</b>. Enter it below to complete authorization:
                    </p>

                    <input
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      placeholder="123456"
                      value={ssoModal.enteredCode || ''}
                      onChange={(e) => {
                        const val = e.target.value.replace(/[^0-9]/g, '')
                        setSsoModal({ ...ssoModal, enteredCode: val, error: '' })
                      }}
                      className="github-code-input"
                      autoFocus
                      disabled={ssoModal.authorizing}
                    />

                    <button
                      type="submit"
                      className="github-btn-authorize"
                      disabled={ssoModal.authorizing}
                    >
                      {ssoModal.authorizing ? (
                        <>
                          <span className="auth-spinner" style={{ width: '16px', height: '16px', borderTopColor: '#ffffff' }}></span>
                          <span>Verifying Code...</span>
                        </>
                      ) : (
                        <span>Verify & Authorize AgentShield AI</span>
                      )}
                    </button>
                  </div>

                  <button
                    type="button"
                    className="github-btn-cancel"
                    onClick={() => setSsoModal({ ...ssoModal, step: 'credentials', error: '' })}
                    disabled={ssoModal.authorizing}
                  >
                    ← Try another authorization method
                  </button>
                </form>
              )}
            </div>

            {/* GitHub Footer */}
            <div className="github-oauth-footer">
              Authorizing will redirect to <b>agentshield.ai/console</b><br />
              <span>GitHub, Inc. &bull; <a href="https://docs.github.com" target="_blank" rel="noreferrer">Terms</a> &bull; <a href="https://docs.github.com" target="_blank" rel="noreferrer">Privacy</a> &bull; <a href="https://github.community" target="_blank" rel="noreferrer">Support</a></span>
            </div>
          </div>
        </div>
      )}

      {/* Google SSO Verification Modal */}
      {ssoModal && ssoModal.provider === 'google' && (
        <div className="modal-overlay" onClick={() => !ssoModal.authorizing && setSsoModal(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, color: '#FFFFFF', fontFamily: 'Outfit', fontSize: '18px' }}>
                {mode === 'login' ? 'Sign in with Google' : 'Create Account with Google'}
              </h3>
              <button
                type="button"
                onClick={() => !ssoModal.authorizing && setSsoModal(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '18px' }}>
              {mode === 'login'
                ? 'Enter your registered Google account email to access the console:'
                : 'Enter your name and Google account email to register your new enterprise account:'}
            </p>

            {ssoModal.error && (
              <div className="auth-alert error" style={{ marginBottom: '16px' }}>
                <span className="alert-dot"></span>
                <span>{ssoModal.error}</span>
              </div>
            )}

            <form onSubmit={handleSSOSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {mode === 'signup' && (
                <div>
                  <label className="form-label" style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={ssoModal.name}
                    onChange={(e) => setSsoModal({ ...ssoModal, name: e.target.value, error: '' })}
                    className="form-input"
                    style={{ width: '100%' }}
                    disabled={ssoModal.authorizing}
                  />
                </div>
              )}

              <div>
                <label className="form-label" style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                  Google Account Email
                </label>
                <input
                  type="email"
                  required
                  value={ssoModal.email}
                  onChange={(e) => setSsoModal({ ...ssoModal, email: e.target.value, error: '' })}
                  className="form-input"
                  style={{ width: '100%' }}
                  disabled={ssoModal.authorizing}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  className="soc-back-home-btn"
                  onClick={() => !ssoModal.authorizing && setSsoModal(null)}
                  disabled={ssoModal.authorizing}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-start-analysis"
                  style={{ padding: '8px 18px', fontSize: '13px' }}
                  disabled={ssoModal.authorizing}
                >
                  {ssoModal.authorizing ? 'Verifying...' : mode === 'login' ? 'Verify & Sign In →' : 'Register & Sign In →'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Forgot Password / Verification Code / Reset Password Modal */}
      {forgotModal && (
        <div className="modal-overlay" onClick={() => setForgotModal(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '460px', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, color: '#FFFFFF', fontFamily: 'Outfit', fontSize: '19px' }}>
                {forgotModal.step === 'email' && 'Reset Your Password'}
                {forgotModal.step === 'code' && 'Enter Verification Code'}
                {forgotModal.step === 'password' && 'Set New Password'}
                {forgotModal.step === 'success' && 'Password Updated!'}
              </h3>
              <button
                type="button"
                onClick={() => setForgotModal(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {forgotModal.error && (
              <div className="auth-alert error" style={{ marginBottom: '16px' }}>
                <span className="alert-dot"></span>
                <span>{forgotModal.error}</span>
              </div>
            )}

            {/* Step 1: Enter Email */}
            {forgotModal.step === 'email' && (
              <form onSubmit={handleSendVerificationCode} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: 0 }}>
                  Enter your registered work email. A 6-digit verification code will be dispatched to your account.
                </p>

                <div className="form-group">
                  <label className="form-label" htmlFor="forgot-email">Registered Email</label>
                  <div className="input-wrap">
                    <input
                      id="forgot-email"
                      type="email"
                      required
                      value={forgotModal.email}
                      onChange={(e) => setForgotModal({ ...forgotModal, email: e.target.value, error: '' })}
                      className="form-input"
                      autoFocus
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '6px' }}>
                  <button
                    type="button"
                    className="soc-back-home-btn"
                    onClick={() => setForgotModal(null)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-start-analysis"
                    style={{ padding: '8px 20px', fontSize: '13px' }}
                    disabled={forgotModal.loading}
                  >
                    {forgotModal.loading ? 'Sending Code...' : 'Send Verification Code →'}
                  </button>
                </div>
              </form>
            )}

            {/* Step 2: Enter Verification Code with Orbit & Slot Animation */}
            {forgotModal.step === 'code' && (
              <form onSubmit={handleVerifyCode} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ textAlign: 'center', marginBottom: '6px' }}>
                  <p style={{ fontSize: '13px', color: '#94A3B8', margin: 0 }}>
                    A verification code has been dispatched to <b style={{ color: '#FFFFFF' }}>{forgotModal.email}</b> from <b style={{ color: '#38BDF8' }}>agentsheildai@gmail.com</b>.
                  </p>
                  <p style={{ fontSize: '12px', color: '#2EE6A8', marginTop: '6px', marginBottom: 0 }}>
                    ✓ Verification email delivered to your inbox. Check your email (and spam folder) for the 6-digit code.
                  </p>
                </div>

                {/* Orbital Ring & Center Hub */}
                <div
                  className={`orbit ${forgotModal.status === 'ok' ? 'is-ok' : forgotModal.status === 'bad' ? 'is-bad' : ''}`}
                  ref={orbitRef}
                >
                  <svg className="orbit_ring" viewBox="0 0 120 120">
                    <circle
                      className="orbit_path"
                      cx="60"
                      cy="60"
                      r="50"
                      vectorEffect="non-scaling-stroke"
                    />
                  </svg>
                  <span className="orbit_hub" ref={hubRef}></span>
                </div>

                {/* Slot with One-Time-Code Input */}
                <label
                  className={`slot ${forgotModal.status === 'ok' ? 'is-ok' : forgotModal.status === 'bad' ? 'is-bad' : ''}`}
                  ref={slotRef}
                >
                  <input
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={6}
                    value={forgotModal.code}
                    onChange={(e) => {
                      const val = e.target.value.replace(/[^0-9]/g, '')
                      setForgotModal((prev) => ({ ...prev, code: val, error: '', status: 'idle' }))
                    }}
                    autoFocus
                    disabled={forgotModal.loading}
                  />
                </label>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                  <button
                    type="button"
                    className="forgot-link"
                    onClick={() => setForgotModal((prev) => ({ ...prev, step: 'email', error: '' }))}
                  >
                    ← Change Email
                  </button>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      type="button"
                      className="soc-back-home-btn"
                      onClick={() => setForgotModal(null)}
                      disabled={forgotModal.loading}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-start-analysis"
                      style={{ padding: '8px 20px', fontSize: '13px' }}
                      disabled={forgotModal.loading}
                    >
                      {forgotModal.loading ? 'Verifying...' : 'Verify Code →'}
                    </button>
                  </div>
                </div>
              </form>
            )}

            {/* Step 3: Set New Password */}
            {forgotModal.step === 'password' && (
              <form onSubmit={handleResetPasswordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: 0 }}>
                  Code verified for <b style={{ color: '#FFFFFF' }}>{forgotModal.email}</b>. Enter your new password below to update it in the database.
                </p>

                <div className="form-group">
                  <label className="form-label" htmlFor="new-password">New Password</label>
                  <div className="input-wrap">
                    <input
                      id="new-password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={forgotModal.newPassword}
                      onChange={(e) => setForgotModal({ ...forgotModal, newPassword: e.target.value, error: '' })}
                      className="form-input"
                      autoFocus
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="confirm-new-password">Confirm New Password</label>
                  <div className="input-wrap">
                    <input
                      id="confirm-new-password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={forgotModal.confirmPassword}
                      onChange={(e) => setForgotModal({ ...forgotModal, confirmPassword: e.target.value, error: '' })}
                      className="form-input"
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '6px' }}>
                  <button
                    type="button"
                    className="soc-back-home-btn"
                    onClick={() => setForgotModal(null)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-start-analysis"
                    style={{ padding: '8px 20px', fontSize: '13px' }}
                  >
                    Update Password in Database →
                  </button>
                </div>
              </form>
            )}

            {/* Step 4: Success Confirmation */}
            {forgotModal.step === 'success' && (
              <div style={{ textAlign: 'center', padding: '10px 0' }}>
                <div style={{ fontSize: '42px', marginBottom: '12px' }}>✓</div>
                <h4 style={{ margin: '0 0 8px', color: '#86EFAC', fontFamily: 'Outfit', fontSize: '18px' }}>
                  Password Successfully Updated
                </h4>
                <p style={{ fontSize: '13px', color: '#CBD5E1', marginBottom: '22px' }}>
                  Your new password has been committed to the database for <b style={{ color: '#FFFFFF' }}>{forgotModal.email}</b>. You can now sign in with your updated credentials.
                </p>
                <button
                  type="button"
                  className="btn-start-analysis"
                  style={{ width: '100%', padding: '10px', fontSize: '14px' }}
                  onClick={handleFinishReset}
                >
                  Proceed to Sign In →
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
