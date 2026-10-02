import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  loginWithCredentials,
  registerWithCredentials,
  updateUserPassword,
} from '../auth.js'
import {
  sendVerificationCodeApi,
  verifyCodeApi,
  getGitHubOAuthStatus,
  getGitHubLoginUrl,
  getGoogleOAuthStatus,
  getGoogleLoginUrl,
} from '../api.js'
import '../auth.css'
import { captureUtmParams } from '../utils/utm.js'
import AuthCinematicBackground from '../components/auth/AuthCinematicBackground.jsx'
import AuthRobot from '../components/auth/AuthRobot.jsx'
import ThemeToggle from '../components/landing/ThemeToggle.jsx'

export default function Auth({ initialMode = 'login' }) {
  const navigate = useNavigate()
  const location = useLocation()

  // Theme state with local persistence: dark (Crystal Lavender) | light (Sakura Light)
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('agentshield-theme')
      if (saved === 'dark' || saved === 'light') return saved
    } catch {
      // fallback
    }
    return 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.body.setAttribute('data-theme', theme)
    document.documentElement.className = theme
    document.body.className = theme
    try {
      localStorage.setItem('agentshield-theme', theme)
    } catch {
      // fallback
    }
  }, [theme])

  // Mode state based on initialMode or URL path (/signup, /sign-up vs /login, /sign-in)
  const isSignUpPath =
    location.pathname === '/signup' ||
    location.pathname === '/sign-up' ||
    initialMode === 'signup'
  const [mode, setMode] = useState(isSignUpPath ? 'signup' : 'login')

  useEffect(() => {
    captureUtmParams()
    if (location.pathname === '/signup' || location.pathname === '/sign-up') {
      setMode('signup')
    } else if (location.pathname === '/login' || location.pathname === '/sign-in') {
      setMode('login')
    }
  }, [location.pathname])

  const handleModeChange = (newMode) => {
    setMode(newMode)
    setFeedback(null)
    const targetPath = newMode === 'signup' ? '/sign-up' : '/sign-in'
    if (location.pathname !== targetPath) {
      navigate(targetPath, { replace: true })
    }
  }

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    orgName: '',
    rememberMe: true,
  })

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [honeypot, setHoneypot] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [feedback, setFeedback] = useState(null) // { type: 'error' | 'success', text: '' }

  // Real OAuth configuration statuses from backend
  const [githubOAuthStatus, setGithubOAuthStatus] = useState(null)
  const [googleOAuthStatus, setGoogleOAuthStatus] = useState(null)

  // Forgot Password modal state
  // step: 'email' | 'code' | 'password' | 'success'
  const [forgotModal, setForgotModal] = useState(null)

  // Refs for orbital verification animation in modal
  const orbitRef = useRef(null)
  const hubRef = useRef(null)
  const slotRef = useRef(null)

  // Fetch OAuth configuration statuses & handle OAuth error redirects
  useEffect(() => {
    getGitHubOAuthStatus()
      .then((status) => {
        setGithubOAuthStatus(status)
      })
      .catch(() => {})

    getGoogleOAuthStatus()
      .then((status) => {
        setGoogleOAuthStatus(status)
      })
      .catch(() => {})

    const params = new URLSearchParams(location.search)
    const errorParam = params.get('error') || params.get('error_description')
    const ghError = params.get('github_error')
    const gError = params.get('google_error')
    if (errorParam) {
      setFeedback({ type: 'error', text: `Authentication Error: ${decodeURIComponent(errorParam)}` })
    } else if (ghError) {
      setFeedback({ type: 'error', text: `GitHub Authentication Error: ${decodeURIComponent(ghError)}` })
    } else if (gError) {
      setFeedback({ type: 'error', text: `Google Authentication Error: ${decodeURIComponent(gError)}` })
    }
  }, [location.search])

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  // Password strength calculation for signup
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

    if (honeypot) {
      setFeedback({ type: 'error', text: 'Automated submission detected.' })
      return
    }

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
          navigate(location.state?.from?.pathname || '/dashboard')
        }, 700)
      } catch (err) {
        setIsLoading(false)
        setFeedback({ type: 'error', text: err.message })
      }
    } else {
      // Login mode
      setIsLoading(true)
      try {
        await loginWithCredentials(formData.email, formData.password)
        setFeedback({
          type: 'success',
          text: 'Authentication successful! Loading console...',
        })
        setTimeout(() => {
          setIsLoading(false)
          navigate(location.state?.from?.pathname || '/dashboard')
        }, 700)
      } catch (err) {
        setIsLoading(false)
        setFeedback({ type: 'error', text: err.message })
      }
    }
  }

  // ==========================================
  // Real OAuth 2.0 Direct Authentication Handlers
  // ==========================================
  const handleContinueWithGitHub = () => {
    setFeedback(null)
    const targetUrl = location.state?.from?.pathname || '/dashboard'
    if (githubOAuthStatus && !githubOAuthStatus.configured) {
      setFeedback({
        type: 'error',
        text: 'GitHub OAuth is not configured on the backend server. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in backend/.env to enable live GitHub sign-in.',
      })
      return
    }
    setIsLoading(true)
    window.location.href = getGitHubLoginUrl({ return_to: targetUrl })
  }

  const handleContinueWithGoogle = () => {
    setFeedback(null)
    const targetUrl = location.state?.from?.pathname || '/dashboard'
    if (googleOAuthStatus && !googleOAuthStatus.configured) {
      setFeedback({
        type: 'error',
        text: 'Google OAuth is not configured on the backend server. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env to enable live Google sign-in.',
      })
      return
    }
    setIsLoading(true)
    window.location.href = getGoogleLoginUrl({ return_to: targetUrl })
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
      slotRef.current.style.transformOrigin = `${hubX}px ${hubY}px`
      slotRef.current.animate(
        [
          { transform: `rotate(0deg)` },
          { transform: `rotate(450deg)` },
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
      status: 'idle',
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
    <div className="auth-page" data-theme={theme}>
      {/* Dark Cinematic Security Background (Replaces previous cloud video) */}
      <AuthCinematicBackground />

      {/* Top-Left: Back to AgentShield */}
      <div className="auth-top-left-bar">
        <Link to="/" className="auth-back-btn" id="back-to-landing-btn" aria-label="Back to AgentShield home">
          <svg
            className="back-btn-icon"
            viewBox="0 0 24 24"
            width="17"
            height="17"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Back to AgentShield</span>
        </Link>
      </div>

      {/* Top-Right: Viewport-Anchored Theme Toggle */}
      <div className="auth-top-right-bar">
        <ThemeToggle theme={theme} setTheme={setTheme} />
      </div>

      {/* Main Interactive Stage Container: ONE Centered Translucent Glass Card */}
      <main className="auth-main-wrapper" id="main-content">
        <div className="auth-stage-container">
          <div className="auth-glass-card">
            {/* LEFT SECTION (45-50%): Standing Robot Visual Panel */}
            <div className="auth-card-left-panel">
              <AuthRobot />
            </div>

            {/* RIGHT SECTION (50-55%): Authentication Form */}
            <div className="auth-card-right-panel">
              {/* Brand Logo & Header */}
              <div className="auth-card-brand">
              <Link to="/" className="auth-brand-logo-wrap">
                <div className="auth-brand-icon">
                  <img src="/logo.png" alt="AgentShield AI Logo" className="auth-brand-logo-img" />
                </div>
                <span className="auth-brand-title">
                  AgentShield<span className="auth-brand-accent">AI</span>
                </span>
              </Link>
            </div>

            {/* Header Title & Subtitle according to user specification */}
            <div className="auth-card-header">
              <h1 className="auth-card-title">
                {mode === 'login' ? 'Welcome Back' : 'Create your account'}
              </h1>
              <p className="auth-card-sub">
                {mode === 'login'
                  ? 'Sign in to continue to AgentShield AI'
                  : 'Join AgentShield AI'}
              </p>
            </div>

            {/* Mode Switcher Pill */}
            <div className="auth-mode-pill">
              <button
                type="button"
                className={`mode-pill-btn ${mode === 'login' ? 'active' : ''}`}
                onClick={() => handleModeChange('login')}
              >
                Sign In
              </button>
              <button
                type="button"
                className={`mode-pill-btn ${mode === 'signup' ? 'active' : ''}`}
                onClick={() => handleModeChange('signup')}
              >
                Create Account
              </button>
            </div>

            {/* Inline Feedback / Alert Banner */}
            {feedback && (
              <div className={`auth-alert ${feedback.type}`} role="alert">
                <span className="alert-dot" aria-hidden="true"></span>
                <span>{feedback.text}</span>
              </div>
            )}

            {/* Main Credentials Form */}
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
                      placeholder="Alex Morgan"
                      autoComplete="name"
                    />
                  </div>
                </div>
              )}

              <div className="form-group">
                <label className="form-label" htmlFor="email">Email</label>
                <div className="input-wrap">
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                    placeholder="alex@company.com"
                    autoComplete="email"
                  />
                </div>
              </div>

              {mode === 'signup' && (
                <div className="form-group">
                  <label className="form-label" htmlFor="orgName">Organization (Optional)</label>
                  <div className="input-wrap">
                    <input
                      id="orgName"
                      type="text"
                      name="orgName"
                      value={formData.orgName}
                      onChange={handleInputChange}
                      className="form-input"
                      placeholder="Acme Cloud Engineering"
                      autoComplete="organization"
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
                    placeholder="••••••••••••"
                    autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
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

                {/* Password Strength Indicator (Signup) */}
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
                        ? 'Weak: Add numbers, uppercase & symbols'
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
                      type={showConfirmPassword ? 'text' : 'password'}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder="••••••••••••"
                      autoComplete="new-password"
                    />
                    <button
                      type="button"
                      className="password-toggle-btn"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                    >
                      {showConfirmPassword ? (
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
                </div>
              )}

              {/* Invisible Anti-Bot Honeypot */}
              <div style={{ position: 'absolute', left: '-9999px', opacity: 0, pointerEvents: 'none' }} aria-hidden="true">
                <label htmlFor="company_website">Do not fill this</label>
                <input
                  id="company_website"
                  type="text"
                  name="company_website"
                  value={honeypot}
                  onChange={(e) => setHoneypot(e.target.value)}
                  tabIndex={-1}
                  autoComplete="off"
                />
              </div>

              {mode === 'login' && (
                <div className="form-remember-row">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onChange={handleInputChange}
                    />
                    <span>Remember this device</span>
                  </label>
                </div>
              )}

              {/* Primary CTA Button */}
              <button
                type="submit"
                className="auth-submit-btn"
                disabled={isLoading}
              >
                <span className="btn-shine" aria-hidden="true"></span>
                {isLoading
                  ? (mode === 'login' ? 'Signing In...' : 'Creating Account...')
                  : (mode === 'login' ? 'Sign In' : 'Create Enterprise Account')}
              </button>
            </form>

            {/* Divider */}
            <div className="auth-divider">
              <span>or</span>
            </div>

            {/* Real OAuth SSO Buttons */}
            <div className="social-sso-group">
              <button
                type="button"
                className="sso-btn"
                onClick={handleContinueWithGoogle}
                id="continue-with-google-btn"
              >
                <svg className="sso-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z"/>
                  <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"/>
                  <path fill="#FBBC05" d="M5.6 14.8c-.3-.8-.4-1.8-.4-2.8s.1-2 .4-2.8L1.9 6.3C.7 8.7 0 10.3 0 12s.7 3.3 1.9 5.7l3.7-2.9z"/>
                  <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"/>
                </svg>
                <span>Google</span>
              </button>

              <button
                type="button"
                className="sso-btn"
                onClick={handleContinueWithGitHub}
                id="continue-with-github-btn"
              >
                <svg className="sso-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                <span>GitHub</span>
              </button>
            </div>

            {/* Navigation Text Link Switcher */}
            <div className="auth-switch-text-row">
              {mode === 'login' ? (
                <span>
                  Don't have an account?{' '}
                  <button
                    type="button"
                    className="auth-switch-link"
                    onClick={() => handleModeChange('signup')}
                  >
                    Sign up
                  </button>
                </span>
              ) : (
                <span>
                  Already have an account?{' '}
                  <button
                    type="button"
                    className="auth-switch-link"
                    onClick={() => handleModeChange('login')}
                  >
                    Sign in
                  </button>
                </span>
              )}
            </div>

            {/* Quick Evaluator Seed Hint */}
            {mode === 'login' && (
              <div className="auth-evaluator-hint">
                <span>Enterprise Evaluator: </span>
                <code>alex@company.com</code> / <code>Password123!</code>
              </div>
            )}

            {/* Legal Notice */}
            <div className="auth-legal-footer">
              Review our <Link to="/privacy">Privacy Policy</Link> and <Link to="/terms">Terms of Service</Link>.
            </div>
          </div>
        </div>
      </div>
    </main>

      {/* Forgot Password / Verification Code Modal (Preserved Workflow) */}
      {forgotModal && (
        <div className="modal-overlay" onClick={() => setForgotModal(null)} role="dialog" aria-modal="true">
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ margin: 0, fontFamily: 'Outfit', fontSize: '19px', fontWeight: 700, color: 'var(--auth-text-primary)' }}>
                {forgotModal.step === 'email' && 'Reset Your Password'}
                {forgotModal.step === 'code' && 'Enter Verification Code'}
                {forgotModal.step === 'password' && 'Set New Password'}
                {forgotModal.step === 'success' && 'Password Updated!'}
              </h2>
              <button
                type="button"
                onClick={() => setForgotModal(null)}
                style={{ background: 'none', border: 'none', color: 'var(--auth-text-muted)', fontSize: '18px', cursor: 'pointer' }}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            {forgotModal.error && (
              <div className="auth-alert error" style={{ marginBottom: '16px' }}>
                <span className="alert-dot" aria-hidden="true"></span>
                <span>{forgotModal.error}</span>
              </div>
            )}

            {/* Step 1: Enter Email */}
            {forgotModal.step === 'email' && (
              <form onSubmit={handleSendVerificationCode} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ fontSize: '13px', color: 'var(--auth-text-secondary)', margin: 0 }}>
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
                      onChange={(e) => setForgotModal((prev) => ({ ...prev, email: e.target.value }))}
                      className="form-input"
                      placeholder="alex@company.com"
                    />
                  </div>
                </div>

                <button type="submit" className="auth-submit-btn" disabled={forgotModal.loading}>
                  {forgotModal.loading ? 'Dispatching Verification...' : 'Send Verification Code →'}
                </button>
              </form>
            )}

            {/* Step 2: Orbital Verification Code */}
            {forgotModal.step === 'code' && (
              <form onSubmit={handleVerifyCode} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ fontSize: '13px', color: 'var(--auth-text-secondary)', margin: 0 }}>
                  Enter the 6-digit cryptographic verification code sent to <strong>{forgotModal.email}</strong>.
                </p>

                <div className="orbit-wrap" style={{ display: 'flex', justifyContent: 'center', margin: '8px 0' }}>
                  <div
                    ref={hubRef}
                    className="orbit-hub"
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '50%',
                      background: 'rgba(167, 139, 250, 0.15)',
                      border: '1px solid var(--auth-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                    }}
                  >
                    <div
                      ref={slotRef}
                      className="orbit-slot"
                      style={{
                        position: 'absolute',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: 'var(--auth-accent)',
                        boxShadow: '0 0 8px var(--auth-accent)',
                        top: '-4px',
                        left: '20px',
                      }}
                    />
                    <span style={{ fontSize: '18px' }}>🔐</span>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="verify-code">6-Digit Code</label>
                  <div className="input-wrap">
                    <input
                      id="verify-code"
                      type="text"
                      maxLength={6}
                      required
                      value={forgotModal.code}
                      onChange={(e) => setForgotModal((prev) => ({ ...prev, code: e.target.value.replace(/\D/g, '') }))}
                      className="form-input"
                      placeholder="123456"
                      style={{ letterSpacing: '0.25em', textAlign: 'center', fontSize: '18px', fontWeight: 700 }}
                    />
                  </div>
                </div>

                <button type="submit" className="auth-submit-btn" disabled={forgotModal.loading}>
                  {forgotModal.loading ? 'Verifying Code...' : 'Confirm Verification Code →'}
                </button>
              </form>
            )}

            {/* Step 3: New Password */}
            {forgotModal.step === 'password' && (
              <form onSubmit={handleResetPasswordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ fontSize: '13px', color: 'var(--auth-text-secondary)', margin: 0 }}>
                  Verification passed! Enter your new password below.
                </p>

                <div className="form-group">
                  <label className="form-label" htmlFor="reset-new-password">New Password</label>
                  <div className="input-wrap">
                    <input
                      id="reset-new-password"
                      type="password"
                      required
                      value={forgotModal.newPassword}
                      onChange={(e) => setForgotModal((prev) => ({ ...prev, newPassword: e.target.value }))}
                      className="form-input"
                      placeholder="Minimum 8 characters"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="reset-confirm-password">Confirm New Password</label>
                  <div className="input-wrap">
                    <input
                      id="reset-confirm-password"
                      type="password"
                      required
                      value={forgotModal.confirmPassword}
                      onChange={(e) => setForgotModal((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                      className="form-input"
                      placeholder="Re-enter password"
                    />
                  </div>
                </div>

                <button type="submit" className="auth-submit-btn" disabled={forgotModal.loading}>
                  {forgotModal.loading ? 'Committing New Password...' : 'Save New Password →'}
                </button>
              </form>
            )}

            {/* Step 4: Success */}
            {forgotModal.step === 'success' && (
              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div style={{ fontSize: '40px', marginBottom: '12px' }}>✓</div>
                <p style={{ fontSize: '14px', color: 'var(--auth-text-primary)', marginBottom: '20px' }}>
                  Your password has been successfully reset in the secure SQLite database.
                </p>
                <button type="button" className="auth-submit-btn" onClick={handleFinishReset}>
                  Return to Sign In →
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
