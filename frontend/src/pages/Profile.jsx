import React, { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  User,
  Shield,
  Key,
  Mail,
  Phone,
  Building,
  Upload,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Lock,
  Globe,
  Clock,
  Laptop,
  LogOut,
  Eye,
  EyeOff,
} from 'lucide-react'
import ThemeToggle from '../components/landing/ThemeToggle.jsx'
import Toast from '../components/Toast.jsx'
import ConfirmationModal from '../components/common/ConfirmationModal.jsx'
import {
  getCurrentUser,
  updateUserProfileData,
  changeUserEmailAddress,
  changeUserAccountPassword,
  updateUserPassword,
  unlinkAccountProvider,
  uploadUserAvatar,
  removeUserAvatar,
  logout,
} from '../auth.js'
import {
  getUserProfile,
  getGitHubLoginUrl,
  getGoogleLoginUrl,
  getGitHubOAuthStatus,
  getGoogleOAuthStatus,
} from '../api.js'

export default function Profile() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(getCurrentUser())
  const [toast, setToast] = useState({ message: '', isError: false })

  // Theme support
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('agentshield-theme')
      if (saved === 'dark' || saved === 'light') return saved
    } catch {}
    return 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.body.setAttribute('data-theme', theme)
    document.documentElement.className = theme
    document.body.className = theme
    try {
      localStorage.setItem('agentshield-theme', theme)
    } catch {}
  }, [theme])

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: currentUser?.name || '',
    orgName: currentUser?.orgName || '',
    phone: currentUser?.phone || '',
  })
  const [isSavingProfile, setIsSavingProfile] = useState(false)

  // Avatar file input ref
  const avatarInputRef = useRef(null)
  const [avatarPreview, setAvatarPreview] = useState(currentUser?.avatar || null)
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)

  // Change Password state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [showCurrentPass, setShowCurrentPass] = useState(false)
  const [showNewPass, setShowNewPass] = useState(false)
  const [isChangingPass, setIsChangingPass] = useState(false)
  const [passFeedback, setPassFeedback] = useState(null)

  // Change Email Modal state
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [logoutModalOpen, setLogoutModalOpen] = useState(false)
  const [emailForm, setEmailForm] = useState({
    newEmail: '',
    password: '',
  })
  const [isChangingEmail, setIsChangingEmail] = useState(false)
  const [emailFeedback, setEmailFeedback] = useState(null)

  // OAuth states for Provider Linking
  const [isUnlinking, setIsUnlinking] = useState(null)
  const [githubOAuthStatus, setGithubOAuthStatus] = useState(null)
  const [googleOAuthStatus, setGoogleOAuthStatus] = useState(null)

  useEffect(() => {
    getGitHubOAuthStatus().then(setGithubOAuthStatus).catch(() => {})
    getGoogleOAuthStatus().then(setGoogleOAuthStatus).catch(() => {})
  }, [])

  // Refresh profile from backend SQLite on mount
  useEffect(() => {
    if (!currentUser?.email) return
    getUserProfile(currentUser.email)
      .then((res) => {
        const freshUser = (res && res.user) ? res.user : res
        if (freshUser && freshUser.email) {
          const fresh = { ...currentUser, ...freshUser }
          setCurrentUser(fresh)
          setProfileForm({
            name: fresh.name || '',
            orgName: fresh.org_name || fresh.orgName || '',
            phone: fresh.phone || '',
          })
          if (fresh.avatar) {
            setAvatarPreview(fresh.avatar)
          }
        }
      })
      .catch(() => {})
  }, [currentUser?.email])

  // Listen for global auth changes
  useEffect(() => {
    const handleAuthChange = (e) => {
      if (e.detail) {
        setCurrentUser(e.detail)
        setProfileForm({
          name: e.detail.name || '',
          orgName: e.detail.orgName || e.detail.org_name || '',
          phone: e.detail.phone || '',
        })
        setAvatarPreview(e.detail.avatar || null)
      }
    }
    window.addEventListener('auth_change', handleAuthChange)
    return () => window.removeEventListener('auth_change', handleAuthChange)
  }, [])

  const showToast = (message, isError = false) => {
    setToast({ message, isError })
  }

  const userProviders = Array.isArray(currentUser?.providers)
    ? currentUser.providers.map((p) => String(p).toLowerCase())
    : typeof currentUser?.providers === 'string'
    ? currentUser.providers.split(',').map((p) => p.trim().toLowerCase())
    : ['email']
  const isGitHubLinked = userProviders.includes('github')
  const isGoogleLinked = userProviders.includes('google')
  const hasPassword = currentUser?.hasPassword === true

  // Handle Profile Update
  const handleSaveProfile = async (e) => {
    e.preventDefault()
    if (!currentUser?.email) return
    setIsSavingProfile(true)
    try {
      const updated = await updateUserProfileData(currentUser.email, {
        name: profileForm.name,
        orgName: profileForm.orgName,
        phone: profileForm.phone,
      })
      setCurrentUser(updated)
      showToast('Personal information updated successfully! ✓')
    } catch (err) {
      showToast(err.message || 'Failed to update profile.', true)
    } finally {
      setIsSavingProfile(false)
    }
  }

  // Handle Avatar Selection & Upload (< 2MB)
  const handleAvatarFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      showToast('Please select a valid image file (.png, .jpg, .webp).', true)
      return
    }

    if (file.size > 2 * 1024 * 1024) {
      showToast('Avatar file size exceeds 2MB limit. Please choose a smaller image.', true)
      return
    }

    setIsUploadingAvatar(true)
    const reader = new FileReader()
    reader.onload = async () => {
      const base64 = reader.result
      setAvatarPreview(base64)
      try {
        await uploadUserAvatar(currentUser.email, base64)
        showToast('Profile photo updated successfully! ✓')
      } catch (err) {
        showToast(err.message || 'Failed to update profile photo.', true)
      } finally {
        setIsUploadingAvatar(false)
      }
    }
    reader.onerror = () => {
      setIsUploadingAvatar(false)
      showToast('Error reading image file.', true)
    }
    reader.readAsDataURL(file)
  }

  // Handle Remove Avatar
  const handleRemoveAvatar = async () => {
    if (!currentUser?.email) return
    setIsUploadingAvatar(true)
    try {
      await removeUserAvatar(currentUser.email)
      setAvatarPreview(null)
      showToast('Profile photo removed.')
    } catch (err) {
      showToast(err.message || 'Failed to remove photo.', true)
    } finally {
      setIsUploadingAvatar(false)
    }
  }

  // Handle Password Change
  const handleChangePassword = async (e) => {
    e.preventDefault()
    setPassFeedback(null)

    if (!passwordForm.currentPassword) {
      setPassFeedback({ type: 'error', text: 'Please enter your current password.' })
      return
    }
    if (passwordForm.newPassword.length < 8) {
      setPassFeedback({ type: 'error', text: 'New password must be at least 8 characters long.' })
      return
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPassFeedback({ type: 'error', text: 'New passwords do not match.' })
      return
    }

    setIsChangingPass(true)
    try {
      await changeUserAccountPassword(
        currentUser.email,
        passwordForm.currentPassword,
        passwordForm.newPassword
      )
      setPassFeedback({ type: 'success', text: 'Password successfully updated! ✓' })
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
      showToast('Account password updated! ✓')
    } catch (err) {
      setPassFeedback({ type: 'error', text: err.message || 'Incorrect password verification.' })
    } finally {
      setIsChangingPass(false)
    }
  }

  // Handle Setting Initial Password (for OAuth users who have no password)
  const handleSetPassword = async (e) => {
    e.preventDefault()
    setPassFeedback(null)

    if (passwordForm.newPassword.length < 8) {
      setPassFeedback({ type: 'error', text: 'New password must be at least 8 characters long.' })
      return
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPassFeedback({ type: 'error', text: 'New passwords do not match.' })
      return
    }

    setIsChangingPass(true)
    try {
      await updateUserPassword(
        currentUser.email,
        passwordForm.newPassword
      )
      setPassFeedback({ type: 'success', text: 'Password successfully set! You can now sign in using email & password. ✓' })
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
      setCurrentUser((prev) => ({
        ...prev,
        hasPassword: true,
        providers: Array.from(new Set([...(prev?.providers || []), 'email'])),
      }))
      showToast('Account password established! ✓')
    } catch (err) {
      setPassFeedback({ type: 'error', text: err.message || 'Failed to establish password.' })
    } finally {
      setIsChangingPass(false)
    }
  }

  // Handle Unlinking an OAuth Provider
  const handleUnlinkProvider = async (provider) => {
    if (!currentUser?.email) return
    const provName = provider === 'github' ? 'GitHub' : 'Google'

    const userProvs = Array.isArray(currentUser?.providers)
      ? currentUser.providers.map((p) => p.toLowerCase())
      : typeof currentUser?.providers === 'string'
      ? currentUser.providers.split(',').map((p) => p.trim().toLowerCase())
      : ['email']

    const hasPassword = currentUser.hasPassword === true
    const remainingCount = userProvs.filter((p) => p !== provider.toLowerCase()).length

    if (!hasPassword && remainingCount === 0) {
      showToast(`Cannot disconnect ${provName}. It is your only sign-in method. Please set an account password first.`, true)
      return
    }

    if (!window.confirm(`Are you sure you want to disconnect ${provName} from your account?`)) {
      return
    }

    setIsUnlinking(provider)
    try {
      const updated = await unlinkAccountProvider(currentUser.email, provider)
      setCurrentUser(updated)
      showToast(`${provName} identity successfully disconnected. ✓`)
    } catch (err) {
      showToast(err.message || `Failed to unlink ${provName}.`, true)
    } finally {
      setIsUnlinking(null)
    }
  }

  // Handle Connecting an OAuth Provider
  const handleConnectProvider = (provider) => {
    if (!currentUser?.email) return
    const targetUrl = '/profile'
    if (provider === 'github') {
      if (githubOAuthStatus && !githubOAuthStatus.configured) {
        showToast('GitHub OAuth is not configured in backend/.env', true)
        return
      }
      window.location.href = getGitHubLoginUrl({ return_to: targetUrl, link_email: currentUser.email })
    } else {
      if (googleOAuthStatus && !googleOAuthStatus.configured) {
        showToast('Google OAuth is not configured in backend/.env', true)
        return
      }
      window.location.href = getGoogleLoginUrl({ return_to: targetUrl, link_email: currentUser.email })
    }
  }

  // Handle Email Change
  const handleChangeEmail = async (e) => {
    e.preventDefault()
    setEmailFeedback(null)

    const cleanNew = (emailForm.newEmail || '').trim().toLowerCase()
    if (!cleanNew || !cleanNew.includes('@')) {
      setEmailFeedback({ type: 'error', text: 'Please enter a valid email address.' })
      return
    }
    if (cleanNew === currentUser.email.toLowerCase()) {
      setEmailFeedback({ type: 'error', text: 'New email cannot be the same as current email.' })
      return
    }
    if (!emailForm.password) {
      setEmailFeedback({ type: 'error', text: 'Please enter your password to confirm.' })
      return
    }

    setIsChangingEmail(true)
    try {
      const updated = await changeUserEmailAddress(
        currentUser.email,
        cleanNew,
        emailForm.password
      )
      setCurrentUser(updated)
      setShowEmailModal(false)
      setEmailForm({ newEmail: '', password: '' })
      showToast(`Email successfully updated to ${cleanNew}! ✓`)
    } catch (err) {
      setEmailFeedback({ type: 'error', text: err.message || 'Failed to update email address.' })
    } finally {
      setIsChangingEmail(false)
    }
  }

  // Handle Logout
  const handleLogout = () => {
    logout()
    navigate('/sign-in')
  }

  // User initials fallback
  const initials = currentUser?.name
    ? currentUser.name
        .split(' ')
        .filter(Boolean)
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : 'OP'

  // Format account creation date
  const memberSince = currentUser?.createdAt
    ? new Date(currentUser.createdAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Current Session'

  return (
    <div className="soc-shell profile-page-shell">
      {/* Top Navigation Bar */}
      <header className="soc-topbar">
        <div className="soc-topbar-left">
          <Link to="/dashboard" className="soc-brand" title="Return to Dashboard">
            <div className="soc-brand-shield">
              <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, fontSize: '13px', color: '#DC2626' }}>
                AS
              </span>
            </div>
            <div className="soc-brand-name">
              AGENTSHIELD<span className="soc-brand-accent">AI</span>
            </div>
          </Link>

          <div className="soc-sys-status">
            <span className="soc-pulse-green" />
            <span>ACCOUNT SECURITY PORTAL</span>
          </div>
        </div>

        <div className="soc-topbar-right">
          <Link to="/dashboard" className="soc-back-home-btn" style={{ textDecoration: 'none' }}>
            <ArrowLeft size={13} />
            <span>Console</span>
          </Link>

          {/* Theme Switcher: Immediately to the left of the profile circle */}
          <div className="soc-theme-toggle-container">
            <ThemeToggle theme={theme} setTheme={setTheme} />
          </div>

          {/* Profile Circle Avatar: Absolute rightmost item */}
          <div className="soc-profile-wrapper">
            <div className="soc-profile-circle-btn active" title={currentUser?.name}>
              {avatarPreview ? (
                <img
                  src={avatarPreview}
                  alt={currentUser?.name || 'Avatar'}
                  style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                />
              ) : (
                <span className="profile-circle-initials">{initials}</span>
              )}
              <span className="profile-status-indicator" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Profile Canvas */}
      <main className="profile-main-container soc-canvas">
        <div className="soc-page-container profile-content-grid">
          {/* Header Banner */}
          <div className="profile-header-card">
            <div className="profile-header-left">
              <div className="profile-large-avatar-box">
                {avatarPreview ? (
                  <img
                    src={avatarPreview}
                    alt={currentUser?.name}
                    className="profile-large-avatar-img"
                  />
                ) : (
                  <div className="profile-large-avatar-fallback">{initials}</div>
                )}

                <button
                  type="button"
                  className="profile-avatar-upload-btn"
                  onClick={() => avatarInputRef.current?.click()}
                  title="Upload profile picture (<2MB)"
                  disabled={isUploadingAvatar}
                >
                  <Upload size={14} />
                </button>
              </div>

              <div className="profile-header-text">
                <div className="profile-name-row">
                  <h1 className="profile-title">{currentUser?.name || 'Security Operator'}</h1>
                  <span className="profile-role-badge">
                    {currentUser?.role ? currentUser.role.toUpperCase() : 'ENTERPRISE OPERATOR'}
                  </span>
                </div>
                <div className="profile-meta-row">
                  <span className="profile-meta-item">
                    <Mail size={13} />
                    {currentUser?.email}
                  </span>
                  <span className="profile-meta-item">
                    <Building size={13} />
                    {currentUser?.orgName || currentUser?.org_name || 'Personal Workspace'}
                  </span>
                  <span className="profile-meta-item">
                    <Clock size={13} />
                    Member since {memberSince}
                  </span>
                </div>
              </div>
            </div>

            <div className="profile-header-actions">
              <input
                ref={avatarInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarFileChange}
                style={{ display: 'none' }}
              />
              <button
                type="button"
                className="soc-back-home-btn"
                onClick={() => avatarInputRef.current?.click()}
                disabled={isUploadingAvatar}
              >
                <Upload size={13} />
                <span>Upload Photo</span>
              </button>

              {avatarPreview && (
                <button
                  type="button"
                  className="soc-back-home-btn text-danger"
                  onClick={handleRemoveAvatar}
                  disabled={isUploadingAvatar}
                  title="Remove custom photo"
                >
                  <Trash2 size={13} />
                  <span>Remove</span>
                </button>
              )}
            </div>
          </div>

          {/* 2-Column Grid: Left (Personal Info & Security) | Right (Sessions & Providers) */}
          <div className="profile-two-column-layout">
            {/* Column 1: Personal Information Form */}
            <div className="profile-cards-column">
              {/* Card 1: Personal Details */}
              <div className="scc-panel-card profile-section-card">
                <div className="scc-panel-head">
                  <div className="scc-panel-title">
                    <User size={16} className="text-red" />
                    <span>Personal Information</span>
                  </div>
                  <span style={{ fontSize: '11px', color: '#64748B' }}>Primary Identity</span>
                </div>

                <form onSubmit={handleSaveProfile} className="profile-form">
                  <div className="profile-field-group">
                    <label className="profile-label">Full Name / Display Name</label>
                    <div className="profile-input-wrapper">
                      <User size={15} className="field-icon" />
                      <input
                        type="text"
                        className="profile-text-input"
                        placeholder="e.g. Alex Henderson"
                        value={profileForm.name}
                        onChange={(e) => setProfileForm((p) => ({ ...p, name: e.target.value }))}
                        required
                      />
                    </div>
                  </div>

                  <div className="profile-field-group">
                    <label className="profile-label">Organization / Company</label>
                    <div className="profile-input-wrapper">
                      <Building size={15} className="field-icon" />
                      <input
                        type="text"
                        className="profile-text-input"
                        placeholder="e.g. Acme Cloud Infrastructure"
                        value={profileForm.orgName}
                        onChange={(e) => setProfileForm((p) => ({ ...p, orgName: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="profile-field-group">
                    <label className="profile-label">Phone Number</label>
                    <div className="profile-input-wrapper">
                      <Phone size={15} className="field-icon" />
                      <input
                        type="tel"
                        className="profile-text-input"
                        placeholder="e.g. +1 (555) 234-5678"
                        value={profileForm.phone}
                        onChange={(e) => setProfileForm((p) => ({ ...p, phone: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="profile-field-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <label className="profile-label">Registered Enterprise Email</label>
                      <button
                        type="button"
                        className="profile-inline-link-btn"
                        onClick={() => {
                          setShowEmailModal(true)
                          setEmailFeedback(null)
                        }}
                      >
                        Change Email Address
                      </button>
                    </div>
                    <div className="profile-input-wrapper readonly">
                      <Mail size={15} className="field-icon" />
                      <input
                        type="email"
                        className="profile-text-input"
                        value={currentUser?.email || ''}
                        readOnly
                        disabled
                      />
                      <span className="profile-verified-tag">VERIFIED</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '14px' }}>
                    <button
                      type="submit"
                      className="btn-start-analysis"
                      style={{ padding: '8px 22px', fontSize: '13px' }}
                      disabled={isSavingProfile}
                    >
                      {isSavingProfile ? 'Saving Changes...' : 'Save Profile Changes'}
                    </button>
                  </div>
                </form>
              </div>

              {/* Card 2: Password & Credentials */}
              <div className="scc-panel-card profile-section-card">
                <div className="scc-panel-head">
                  <div className="scc-panel-title">
                    <Key size={16} className="text-red" />
                    <span>{hasPassword ? 'Change Password' : 'Set Account Password'}</span>
                  </div>
                  <span style={{ fontSize: '11px', color: hasPassword ? '#64748B' : '#EAB308' }}>
                    {hasPassword ? 'Account Credentials' : 'Password Not Configured'}
                  </span>
                </div>

                {!hasPassword && (
                  <div style={{
                    margin: '0 0 16px',
                    padding: '12px 14px',
                    background: 'rgba(234, 179, 8, 0.08)',
                    border: '1px solid rgba(234, 179, 8, 0.25)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#FDE047',
                    lineHeight: '1.5',
                  }}>
                    Your account is authenticated via external identity ({userProviders.join(', ')}). Create a password to enable email &amp; password sign-in.
                  </div>
                )}

                {passFeedback && (
                  <div className={`auth-feedback-box ${passFeedback.type}`}>
                    {passFeedback.type === 'error' ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
                    <span>{passFeedback.text}</span>
                  </div>
                )}

                <form onSubmit={hasPassword ? handleChangePassword : handleSetPassword} className="profile-form">
                  {hasPassword && (
                    <div className="profile-field-group">
                      <label className="profile-label">Current Password</label>
                      <div className="profile-input-wrapper">
                        <Lock size={15} className="field-icon" />
                        <input
                          type={showCurrentPass ? 'text' : 'password'}
                          className="profile-text-input"
                          placeholder="••••••••••••"
                          value={passwordForm.currentPassword}
                          onChange={(e) => setPasswordForm((p) => ({ ...p, currentPassword: e.target.value }))}
                          required={hasPassword}
                        />
                        <button
                          type="button"
                          className="toggle-pass-btn"
                          onClick={() => setShowCurrentPass(!showCurrentPass)}
                        >
                          {showCurrentPass ? <EyeOff size={14} /> : <Eye size={14} />}
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="profile-field-group">
                    <label className="profile-label">
                      {hasPassword ? 'New Password (min. 8 characters)' : 'Create Password (min. 8 characters)'}
                    </label>
                    <div className="profile-input-wrapper">
                      <Lock size={15} className="field-icon" />
                      <input
                        type={showNewPass ? 'text' : 'password'}
                        className="profile-text-input"
                        placeholder="••••••••••••"
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm((p) => ({ ...p, newPassword: e.target.value }))}
                        required
                      />
                      <button
                        type="button"
                        className="toggle-pass-btn"
                        onClick={() => setShowNewPass(!showNewPass)}
                      >
                        {showNewPass ? <EyeOff size={14} /> : <Eye size={14} />}
                      </button>
                    </div>
                  </div>

                  <div className="profile-field-group">
                    <label className="profile-label">
                      {hasPassword ? 'Confirm New Password' : 'Confirm Password'}
                    </label>
                    <div className="profile-input-wrapper">
                      <Lock size={15} className="field-icon" />
                      <input
                        type={showNewPass ? 'text' : 'password'}
                        className="profile-text-input"
                        placeholder="••••••••••••"
                        value={passwordForm.confirmPassword}
                        onChange={(e) => setPasswordForm((p) => ({ ...p, confirmPassword: e.target.value }))}
                        required
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '14px' }}>
                    <button
                      type="submit"
                      className="soc-back-home-btn"
                      style={{ padding: '8px 22px', fontSize: '13px' }}
                      disabled={isChangingPass}
                    >
                      {isChangingPass
                        ? 'Saving...'
                        : hasPassword
                        ? 'Update Password'
                        : 'Set Account Password'}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Column 2: Account Security, Providers, and Active Sessions */}
            <div className="profile-cards-column">
              {/* Card 3: Connected Authentication Providers */}
              <div className="scc-panel-card profile-section-card">
                <div className="scc-panel-head">
                  <div className="scc-panel-title">
                    <Shield size={16} className="text-red" />
                    <span>Connected Identity Providers</span>
                  </div>
                </div>

                <div className="providers-list">
                  {/* Email & Password */}
                  <div className={`provider-item ${hasPassword ? 'active' : ''}`}>
                    <div className="provider-item-left">
                      <div className="provider-icon-box">
                        <Mail size={15} />
                      </div>
                      <div>
                        <div className="provider-name">Email &amp; Password</div>
                        <div className="provider-desc">
                          {hasPassword ? currentUser?.email : 'No password set on account'}
                        </div>
                      </div>
                    </div>
                    {hasPassword ? (
                      <span className="provider-badge active">CONNECTED</span>
                    ) : (
                      <span className="provider-badge not-linked" style={{ color: '#EAB308', borderColor: 'rgba(234,179,8,0.3)' }}>
                        NO PASSWORD
                      </span>
                    )}
                  </div>

                  {/* GitHub SSO */}
                  <div className={`provider-item ${isGitHubLinked ? 'active' : ''}`}>
                    <div className="provider-item-left">
                      <div className="provider-icon-box">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
                          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                        </svg>
                      </div>
                      <div>
                        <div className="provider-name">GitHub SSO</div>
                        <div className="provider-desc">OAuth 2.0 Security Protocol</div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {isGitHubLinked ? (
                        <>
                          <span className="provider-badge active">LINKED</span>
                          <button
                            type="button"
                            onClick={() => handleUnlinkProvider('github')}
                            disabled={isUnlinking === 'github'}
                            style={{
                              background: 'transparent',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              color: '#F87171',
                              borderRadius: '6px',
                              padding: '3px 10px',
                              fontSize: '11px',
                              fontWeight: '600',
                              cursor: 'pointer',
                            }}
                            title="Disconnect GitHub account"
                          >
                            {isUnlinking === 'github' ? 'Disconnecting...' : 'Disconnect'}
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleConnectProvider('github')}
                          style={{
                            background: 'rgba(255, 255, 255, 0.06)',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            color: '#F1F5F9',
                            borderRadius: '6px',
                            padding: '4px 12px',
                            fontSize: '11px',
                            fontWeight: '600',
                            cursor: 'pointer',
                          }}
                        >
                          Connect GitHub
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Google Workspace */}
                  <div className={`provider-item ${isGoogleLinked ? 'active' : ''}`}>
                    <div className="provider-item-left">
                      <div className="provider-icon-box">
                        <svg viewBox="0 0 24 24" width="15" height="15">
                          <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z"/>
                          <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"/>
                          <path fill="#FBBC05" d="M5.6 14.8c-.3-.8-.4-1.8-.4-2.8s.1-2 .4-2.8L1.9 6.3C.7 8.7 0 10.3 0 12s.7 3.3 1.9 5.7l3.7-2.9z"/>
                          <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"/>
                        </svg>
                      </div>
                      <div>
                        <div className="provider-name">Google Workspace</div>
                        <div className="provider-desc">OpenID Connect Protocol</div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {isGoogleLinked ? (
                        <>
                          <span className="provider-badge active">LINKED</span>
                          <button
                            type="button"
                            onClick={() => handleUnlinkProvider('google')}
                            disabled={isUnlinking === 'google'}
                            style={{
                              background: 'transparent',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              color: '#F87171',
                              borderRadius: '6px',
                              padding: '3px 10px',
                              fontSize: '11px',
                              fontWeight: '600',
                              cursor: 'pointer',
                            }}
                            title="Disconnect Google account"
                          >
                            {isUnlinking === 'google' ? 'Disconnecting...' : 'Disconnect'}
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleConnectProvider('google')}
                          style={{
                            background: 'rgba(255, 255, 255, 0.06)',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            color: '#F1F5F9',
                            borderRadius: '6px',
                            padding: '4px 12px',
                            fontSize: '11px',
                            fontWeight: '600',
                            cursor: 'pointer',
                          }}
                        >
                          Connect Google
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 4: Session Security & Devices */}
              <div className="scc-panel-card profile-section-card">
                <div className="scc-panel-head">
                  <div className="scc-panel-title">
                    <Laptop size={16} className="text-red" />
                    <span>Active Session Security</span>
                  </div>
                  <span className="soc-pulse-green" style={{ width: '8px', height: '8px' }} />
                </div>

                <div className="session-security-box">
                  <div className="session-item current">
                    <div className="session-item-header">
                      <span className="session-device-title">Current Browser Session</span>
                      <span className="session-current-pill">THIS DEVICE</span>
                    </div>
                    <div className="session-meta-lines">
                      <div><b>Client:</b> {navigator.userAgent.slice(0, 60)}...</div>
                      <div><b>Origin:</b> {window.location.origin}</div>
                      <div><b>Security Context:</b> Authenticated Session</div>
                      <div><b>User ID:</b> <code style={{ color: '#DC2626' }}>{currentUser?.id || currentUser?.sub || 'Local Session'}</code></div>
                    </div>
                  </div>
                </div>

                <div className="profile-signout-container">
                  <button
                    type="button"
                    className="profile-signout-btn"
                    onClick={() => setLogoutModalOpen(true)}
                  >
                    <LogOut size={14} />
                    <span>Sign Out of AgentShield</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Change Email Modal */}
      {showEmailModal && (
        <div className="modal-overlay" onClick={() => setShowEmailModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
            <div className="modal-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Change Enterprise Email</span>
              <button
                className="modal-close"
                onClick={() => setShowEmailModal(false)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '6px' }}>
              Updating your email address will update your primary login credentials across AgentShield AI.
            </p>

            {emailFeedback && (
              <div className={`auth-feedback-box ${emailFeedback.type}`} style={{ marginTop: '12px' }}>
                {emailFeedback.type === 'error' ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
                <span>{emailFeedback.text}</span>
              </div>
            )}

            <form onSubmit={handleChangeEmail} style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="profile-label">New Email Address</label>
                <input
                  type="email"
                  className="profile-text-input"
                  placeholder="new.email@company.com"
                  value={emailForm.newEmail}
                  onChange={(e) => setEmailForm((prev) => ({ ...prev, newEmail: e.target.value }))}
                  required
                />
              </div>

              <div>
                <label className="profile-label">Confirm Password</label>
                <input
                  type="password"
                  className="profile-text-input"
                  placeholder="••••••••••••"
                  value={emailForm.password}
                  onChange={(e) => setEmailForm((prev) => ({ ...prev, password: e.target.value }))}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  className="soc-back-home-btn"
                  onClick={() => setShowEmailModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-start-analysis"
                  style={{ padding: '8px 20px', fontSize: '13px' }}
                  disabled={isChangingEmail}
                >
                  {isChangingEmail ? 'Updating Email...' : 'Confirm Email Change'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Safe Signout Confirmation Modal (Item 15) */}
      <ConfirmationModal
        isOpen={logoutModalOpen}
        onClose={() => setLogoutModalOpen(false)}
        onConfirm={handleLogout}
        title="Sign Out of AgentShield"
        description="Are you sure you want to end your active operator session and sign out?"
        confirmText="Sign Out"
        cancelText="Stay Signed In"
        danger={true}
      />

      <Toast
        message={toast.message}
        isError={toast.isError}
        onDone={() => setToast({ message: '', isError: false })}
      />
    </div>
  )
}
