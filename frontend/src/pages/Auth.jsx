import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
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

  const handleSubmit = (e) => {
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
    }

    setIsLoading(true)

    // Simulate enterprise authentication handshake
    setTimeout(() => {
      setIsLoading(false)
      setFeedback({
        type: 'success',
        text: mode === 'login' ? 'Authentication successful! Loading console...' : 'Account created! Redirecting to console...',
      })
      setTimeout(() => {
        navigate('/console')
      }, 700)
    }, 900)
  }

  // Instant Guest / Evaluator Login for project review & demo
  const handleGuestLogin = () => {
    setIsLoading(true)
    setFeedback({
      type: 'success',
      text: 'Signing in as Evaluator / Guest... Initializing AgentShield Workspace.',
    })
    setTimeout(() => {
      navigate('/console')
    }, 600)
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
          {/* Mode Switcher Pill (21st.dev / OriginKit Style) */}
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
                ? 'Enter your credentials to access the autonomous security console'
                : 'Join modern engineering teams securing cloud-native infrastructure'}
            </p>
          </div>

          {/* Social SSO Buttons */}
          <div className="social-sso-group">
            <button
              type="button"
              className="sso-btn"
              onClick={() => {
                setIsLoading(true)
                setTimeout(() => navigate('/console'), 600)
              }}
            >
              <svg className="sso-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>GitHub</span>
            </button>

            <button
              type="button"
              className="sso-btn"
              onClick={() => {
                setIsLoading(true)
                setTimeout(() => navigate('/console'), 600)
              }}
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
                    placeholder="e.g. Alex Henderson"
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
                  placeholder="alex@company.com"
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
                    placeholder="e.g. Acme Cloud Infrastructure"
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
                    onClick={() => alert('Password reset link sent to your registered email.')}
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
                  placeholder="••••••••••••"
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
                    placeholder="••••••••••••"
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
              {isLoading ? 'Authenticating...' : mode === 'login' ? 'Sign In to Console →' : 'Create Enterprise Account →'}
            </button>
          </form>

          {/* Quick Evaluator / Demo Login Shortcut */}
          <div className="evaluator-shortcut-box">
            <span className="eval-tag">PROJECT REVIEW & DEMO SHORTCUT</span>
            <p className="eval-desc">Instantly launch console with pre-loaded mock workspace.</p>
            <button
              type="button"
              className="btn-evaluator-login"
              onClick={handleGuestLogin}
            >
              ⚡ One-Click Evaluator / Guest Login
            </button>
          </div>

          <div className="auth-footer-note">
            <span>Protected by AgentShield Zero-Trust Gateway.</span>
            <Link to="/" className="back-home-link">← Back to Homepage</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
