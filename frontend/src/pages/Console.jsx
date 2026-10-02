import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useLocation } from 'react-router-dom'
import {
  LogOut,
  ExternalLink,
  Shield,
  User,
  Menu,
  X,
  MessageSquare,
  LayoutDashboard,
  Scan,
  Cpu,
  Boxes,
  ShieldAlert,
  Network,
  Wrench,
  Sparkles,
  ClipboardCheck,
  Cloud,
  ShieldCheck,
  Activity,
  FlaskConical,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  ChevronRight,
} from 'lucide-react'
import ThemeToggle from '../components/landing/ThemeToggle.jsx'
import ConfirmationModal from '../components/common/ConfirmationModal.jsx'
import FeedbackModal from '../components/common/FeedbackModal.jsx'
import { getCurrentUser, setCurrentUser as saveCurrentUserSession, getRegisteredUsers, saveRegisteredUsers, logout } from '../auth.js'
import {
  checkHealth,
  listWorkspaces,
  getWorkspace,
  scanFile,
  decidePatch,
  getAuditQueueStats,
  getApiBase,
  setApiBase,
} from '../api.js'
import Toast from '../components/Toast.jsx'
import ReportView from '../components/ReportView.jsx'
import WorkspaceList from '../components/WorkspaceList.jsx'
import SecurityCommandCenter from '../components/soc/SecurityCommandCenter.jsx'
import NewScanView from '../components/soc/NewScanView.jsx'
import AgentPipelineView from '../components/soc/AgentPipelineView.jsx'
import FindingsView from '../components/soc/FindingsView.jsx'
import AttackPathView from '../components/soc/AttackPathView.jsx'
import RemediationView from '../components/soc/RemediationView.jsx'
import ConsensusView from '../components/soc/ConsensusView.jsx'
import AuditQueueView from '../components/soc/AuditQueueView.jsx'
import MultiCloudView from '../components/soc/MultiCloudView.jsx'
import ComplianceView from '../components/soc/ComplianceView.jsx'
import DriftView from '../components/soc/DriftView.jsx'
import ResearchLabView from '../components/soc/ResearchLabView.jsx'

export default function Console({ initialTab }) {
  const navigate = useNavigate()
  const params = useParams()
  const location = useLocation()
  const [currentUser, setCurrentUser] = useState(getCurrentUser())
  const [activeTab, setActiveTab] = useState(initialTab || 'dashboard') // 12 views
  const [healthy, setHealthy] = useState(null)
  const [workspaces, setWorkspaces] = useState([])
  const [currentWorkspace, setCurrentWorkspace] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [pendingCount, setPendingCount] = useState(0)
  const [toast, setToast] = useState({ message: '', isError: false })
  const [apiBaseVal, setApiBaseVal] = useState(getApiBase())
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [logoutConfirmOpen, setLogoutConfirmOpen] = useState(false)
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false)

  // Collapsible sidebar state with session and localStorage persistence
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem('agentshield_sidebar_collapsed') === 'true'
    } catch {
      return false
    }
  })

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => {
      const next = !prev
      try {
        localStorage.setItem('agentshield_sidebar_collapsed', String(next))
      } catch {}
      return next
    })
  }, [])

  // Global keyboard shortcut: Ctrl+B or Cmd+B toggles sidebar
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault()
        toggleSidebar()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleSidebar])

  // Authenticated Theme state: dark / light with persistence
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('agentshield-theme')
      if (saved === 'dark' || saved === 'light') return saved
    } catch {
      // fallback
    }
    return 'dark'
  })
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false)

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

  // Close dropdown on click outside
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (!e.target.closest('.soc-profile-wrapper')) {
        setProfileDropdownOpen(false)
      }
    }
    document.addEventListener('click', handleOutsideClick)
    return () => document.removeEventListener('click', handleOutsideClick)
  }, [])

  const showToast = useCallback((message, isError = false) => {
    setToast({ message, isError })
  }, [])

  const refreshHealth = useCallback(async () => {
    try {
      await checkHealth()
      setHealthy(true)
    } catch {
      setHealthy(false)
    }
  }, [])

  const refreshWorkspaces = useCallback(async () => {
    try {
      const list = await listWorkspaces()
      setWorkspaces(list || [])
      if (list && list.length > 0) {
        setCurrentWorkspace((prev) => {
          if (!prev) {
            getWorkspace(list[0].workspace_id).then(setCurrentWorkspace).catch(() => {})
          }
          return prev
        })
      }
    } catch {
      setWorkspaces([])
    }
  }, [])

  const refreshAuditStats = useCallback(async () => {
    try {
      const stats = await getAuditQueueStats()
      if (stats?.pending_count !== undefined) {
        setPendingCount(stats.pending_count)
      }
    } catch {
      setPendingCount(0)
    }
  }, [])

  useEffect(() => {
    // Detect GitHub OAuth 2.0 redirect return
    const params = new URLSearchParams(window.location.search)
    if (params.get('github_auth') === 'success') {
      const email = (params.get('email') || '').trim().toLowerCase()
      const name = (params.get('name') || '').trim() || 'GitHub Developer'
      const login = (params.get('login') || '').trim()

      if (email) {
        const users = getRegisteredUsers()
        let ghUser = users.find((u) => u.email.toLowerCase() === email)
        if (!ghUser) {
          ghUser = {
            id: `usr-${Date.now()}`,
            name: name,
            email: email,
            password: '',
            orgName: login ? `${login} (GitHub)` : 'GitHub Enterprise',
            providers: ['github'],
            createdAt: new Date().toISOString(),
          }
          users.push(ghUser)
        } else {
          if (!ghUser.providers) ghUser.providers = ['email']
          if (!ghUser.providers.includes('github')) {
            ghUser.providers.push('github')
          }
        }
        saveRegisteredUsers(users)
        saveCurrentUserSession(ghUser)
        setCurrentUser(ghUser)
        // Clean URL query parameters
        window.history.replaceState({}, document.title, window.location.pathname)
        showToast(`Welcome ${name}! Authenticated via GitHub (@${login || email})`)
      }
    }

    // Detect Google OAuth 2.0 redirect return
    if (params.get('google_auth') === 'success') {
      const email = (params.get('email') || '').trim().toLowerCase()
      const name = (params.get('name') || '').trim() || 'Google User'

      if (email) {
        const users = getRegisteredUsers()
        let gUser = users.find((u) => u.email.toLowerCase() === email)
        if (!gUser) {
          gUser = {
            id: `usr-${Date.now()}`,
            name: name,
            email: email,
            password: '',
            orgName: 'Google Account',
            providers: ['google'],
            createdAt: new Date().toISOString(),
          }
          users.push(gUser)
        } else {
          if (!gUser.providers) gUser.providers = ['email']
          if (!gUser.providers.includes('google')) {
            gUser.providers.push('google')
          }
        }
        saveRegisteredUsers(users)
        saveCurrentUserSession(gUser)
        setCurrentUser(gUser)
        // Clean URL query parameters
        window.history.replaceState({}, document.title, window.location.pathname)
        showToast(`Welcome ${name}! Authenticated via Google (${email})`)
      }
    }

    const user = getCurrentUser()
    if (!user) {
      navigate('/sign-in')
      return
    }
    setCurrentUser(user)
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
  }, [navigate, refreshHealth, refreshWorkspaces, refreshAuditStats, showToast])

  // Reactive listener for auth changes from Profile or other tabs
  useEffect(() => {
    const handleAuthChange = (e) => {
      if (e.detail) {
        setCurrentUser(e.detail)
      } else {
        const u = getCurrentUser()
        if (u) setCurrentUser(u)
      }
    }
    window.addEventListener('auth_change', handleAuthChange)
    return () => window.removeEventListener('auth_change', handleAuthChange)
  }, [])

  // Sync activeTab with URL pathname and parameter ID
  useEffect(() => {
    const path = location.pathname
    if (path === '/dashboard' || path === '/home' || path === '/console') {
      setActiveTab('dashboard')
    } else if (path === '/scan') {
      setActiveTab('new-scan')
    } else if (path.startsWith('/agents')) {
      setActiveTab('pipeline')
    } else if (path.startsWith('/projects')) {
      setActiveTab('workspaces')
      if (params.id) {
        handleSelectWorkspace(params.id)
      }
    } else if (path.startsWith('/results')) {
      setActiveTab('findings')
      if (params.id) {
        handleSelectWorkspace(params.id)
      }
    } else if (path === '/settings') {
      setActiveTab('research')
    } else if (initialTab) {
      setActiveTab(initialTab)
    }
  }, [location.pathname, params.id, initialTab])

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab)
    setMobileNavOpen(false)
    if (tab === 'dashboard') {
      navigate('/dashboard')
    } else if (tab === 'new-scan') {
      navigate('/scan')
    } else if (tab === 'pipeline') {
      navigate('/agents')
    } else if (tab === 'workspaces') {
      navigate('/projects')
    } else if (tab === 'findings' && currentWorkspace?.workspace_id) {
      navigate(`/results/${currentWorkspace.workspace_id}`)
    }
  }, [navigate, currentWorkspace?.workspace_id])

  async function handleScan(file, options = {}) {
    setScanning(true)
    setActiveTab('pipeline') // Switch to pipeline immediately to watch the agents execute!
    navigate('/agents')
    try {
      const ws = await scanFile(file)
      showToast(`Scan complete — ${ws.report?.summary?.total_vulnerabilities || 0} finding(s)`)
      await refreshWorkspaces()
      await refreshAuditStats()
      setCurrentWorkspace(ws)
    } catch (e) {
      showToast(e.message, true)
    } finally {
      setScanning(false)
    }
  }

  async function handleSelectWorkspace(id) {
    try {
      const ws = await getWorkspace(id)
      setCurrentWorkspace(ws)
      setActiveTab('findings')
      navigate(`/results/${id}`)
    } catch (e) {
      showToast(e.message, true)
    }
  }

  async function handleDecide(arg1, arg2, arg3) {
    let wsId = currentWorkspace?.workspace_id
    let patchId = arg1
    let decision = arg2
    if (arg3 !== undefined) {
      wsId = arg1
      patchId = arg2
      decision = arg3
    }
    const decNorm = (decision === 'approved' || decision === 'accept' || decision === 'apply') ? 'accept' : 'reject'
    if (!wsId || !patchId) return
    try {
      await decidePatch(wsId, patchId, decNorm)
      showToast(`Patch ${decNorm === 'accept' ? 'accepted' : 'rejected'} successfully! ✓`)
      const refreshed = await getWorkspace(wsId)
      setCurrentWorkspace(refreshed)
      refreshWorkspaces()
      refreshAuditStats()
    } catch (e) {
      showToast(e.message, true)
    }
  }

  function commitApiBase() {
    setApiBase(apiBaseVal)
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
  }

  const activeWorkspace = currentWorkspace || (workspaces && workspaces.length > 0 ? workspaces[0] : null)

  const BREADCRUMB_MAP = {
    dashboard: { section: 'Overview', title: 'Security Command Center' },
    workspaces: { section: 'Overview', title: 'Workspace Scans & Archives' },
    'new-scan': { section: 'Operations', title: 'New IaC Security Scan' },
    pipeline: { section: 'Operations', title: 'Agent Pipeline Telemetry' },
    multicloud: { section: 'Operations', title: 'Multi-Cloud Posture' },
    findings: { section: 'Security Analysis', title: 'Vulnerability Findings' },
    'attack-map': { section: 'Security Analysis', title: 'Attack Path Graph' },
    consensus: { section: 'Security Analysis', title: 'Multi-LLM Consensus' },
    remediation: { section: 'Remediation & Compliance', title: 'Remediation Workbench' },
    audit: { section: 'Remediation & Compliance', title: 'Human Audit Queue' },
    drift: { section: 'Remediation & Compliance', title: 'AWS Drift Detection' },
    compliance: { section: 'Remediation & Compliance', title: 'Compliance Center' },
    research: { section: 'Research & Lab', title: 'Research & Benchmark Lab' },
  }

  const currentBreadcrumb = BREADCRUMB_MAP[activeTab] || { section: 'Security Operations', title: activeTab }

  const navSections = [
    {
      header: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'workspaces', label: 'Workspaces', icon: Boxes, badge: workspaces.length > 0 ? workspaces.length : null },
      ],
    },
    {
      header: 'OPERATIONS',
      items: [
        { id: 'new-scan', label: 'New Scan', icon: Scan },
        { id: 'pipeline', label: 'Agent Pipeline', icon: Cpu, isLive: scanning },
        { id: 'multicloud', label: 'Multi-Cloud', icon: Cloud },
      ],
    },
    {
      header: 'SECURITY ANALYSIS',
      items: [
        { id: 'findings', label: 'Findings', icon: ShieldAlert, badge: activeWorkspace?.report?.summary?.total_vulnerabilities || null },
        { id: 'attack-map', label: 'Attack Map', icon: Network },
        { id: 'consensus', label: 'AI Consensus', icon: Sparkles },
      ],
    },
    {
      header: 'REMEDIATION & COMPLIANCE',
      items: [
        { id: 'remediation', label: 'Remediation', icon: Wrench },
        { id: 'audit', label: 'Audit Queue', icon: ClipboardCheck, badge: pendingCount > 0 ? pendingCount : null, isAlert: pendingCount > 0 },
        { id: 'drift', label: 'Drift Detection', icon: Activity },
        { id: 'compliance', label: 'Compliance', icon: ShieldCheck },
      ],
    },
    {
      header: 'RESEARCH & LAB',
      items: [
        { id: 'research', label: 'Research Lab', icon: FlaskConical },
      ],
    },
  ]

  return (
    <div className="soc-shell">
      {/* Skip to Main Content Link */}
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>

      {/* Mobile Backdrop Overlay */}
      {mobileNavOpen && (
        <div
          className="soc-sidebar-backdrop"
          onClick={() => setMobileNavOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* 1. Full-Height Collapsible Left Sidebar */}
      <aside
        className={`soc-sidebar ${sidebarCollapsed ? 'collapsed' : ''} ${mobileNavOpen ? 'mobile-open' : ''}`}
        aria-label="Main Navigation"
      >
        {/* Sidebar Header: Brand & Collapse Toggle */}
        <div className="soc-sidebar-head">
          <Link to="/" className="soc-sidebar-brand" title="AgentShield AI Home">
            <div className="soc-brand-shield">
              <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, fontSize: '13px', color: '#E11D48' }}>
                AS
              </span>
            </div>
            <div className="soc-brand-name">
              AGENTSHIELD<span className="soc-brand-accent">AI</span>
            </div>
          </Link>

          <button
            type="button"
            className="soc-sidebar-toggle-btn"
            onClick={toggleSidebar}
            title="Close sidebar (Ctrl+B)"
            aria-label="Close sidebar"
          >
            <PanelLeftClose size={16} />
          </button>
        </div>

        {/* Active Workspace / Scope Pill */}
        <div className="soc-sidebar-workspace-pill" title={`Active: ${activeWorkspace?.name || 'Default SOC'}`}>
          <span className="ws-pill-dot" />
          <span className="ws-pill-text">{activeWorkspace?.name || 'Default Workspace'}</span>
          <span className="ws-pill-badge">{activeWorkspace?.iac_type || 'IaC'}</span>
        </div>

        {/* Navigation Groups */}
        <nav className="soc-sidebar-nav">
          {navSections.map((sec) => (
            <div key={sec.header} className="soc-nav-group">
              <div className="soc-nav-header">{sec.header}</div>
              {sec.items.map((item) => {
                const Icon = item.icon
                const isActive = activeTab === item.id
                return (
                  <button
                    key={item.id}
                    type="button"
                    className={`soc-nav-item ${isActive ? 'active' : ''}`}
                    onClick={() => handleTabChange(item.id)}
                  >
                    <div className="soc-nav-item-left">
                      <Icon size={16} className="soc-nav-icon" />
                      <span className="soc-nav-label">{item.label}</span>
                    </div>

                    {item.isLive && (
                      <span className="soc-nav-pulse-dot" title="Active scanning..." />
                    )}

                    {item.badge !== null && item.badge !== undefined && (
                      <span className={`soc-badge-counter ${item.isAlert ? 'alert' : ''}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          ))}
        </nav>

        {/* Sidebar Footer: Profile & Session Toggle */}
        <div className="soc-sidebar-footer">
          <Link
            to="/profile"
            className="soc-sidebar-user-pill"
            title={`${currentUser?.name || 'Security Operator'} (Settings)`}
          >
            <div className="soc-sidebar-user-avatar">
              {currentUser?.avatar ? (
                <img src={currentUser.avatar} alt="Avatar" />
              ) : (
                <span>
                  {currentUser?.name
                    ? currentUser.name.split(' ').filter(Boolean).map((n) => n[0]).join('').slice(0, 2).toUpperCase()
                    : 'OP'}
                </span>
              )}
              <span className="avatar-status-dot" />
            </div>
            <div className="soc-sidebar-user-meta">
              <span className="user-name">{currentUser?.name || 'Security Operator'}</span>
              <span className="user-org">{currentUser?.orgName || currentUser?.org_name || 'Personal Workspace'}</span>
            </div>
          </Link>
        </div>
      </aside>

      {/* Floating Reopen Button (Desktop only, when sidebar is closed) */}
      {sidebarCollapsed && !mobileNavOpen && (
        <button
          type="button"
          className="soc-floating-reopen-btn"
          onClick={toggleSidebar}
          title="Open sidebar (Ctrl+B)"
          aria-label="Open sidebar"
        >
          <PanelLeftOpen size={15} />
        </button>
      )}

      {/* 2. Main Area: Compact Topbar + Canvas */}
      <div className="soc-main-area">
        <header className="soc-topbar">
          <div className="soc-topbar-left">
            {/* Mobile Navigation Drawer Toggle */}
            <button
              type="button"
              className="soc-mobile-menu-btn"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              aria-label={mobileNavOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={mobileNavOpen}
            >
              {mobileNavOpen ? <X size={18} /> : <Menu size={18} />}
            </button>

            {/* Authenticated Topbar Brand Mark (Shown when sidebar is closed) */}
            {sidebarCollapsed && (
              <Link
                to="/dashboard"
                className="soc-topbar-brand"
                title="AgentShield AI Dashboard"
                onClick={() => handleTabChange('dashboard')}
              >
                <div className="soc-topbar-brand-shield">
                  <Shield size={12} strokeWidth={2.4} />
                </div>
                <span className="soc-topbar-brand-name">
                  AgentShield <span className="soc-brand-accent">AI</span>
                </span>
              </Link>
            )}

            {/* Breadcrumbs */}
            <div className="soc-breadcrumbs">
              <span className="breadcrumb-section">{currentBreadcrumb.section}</span>
              <span className="breadcrumb-sep">/</span>
              <span className="breadcrumb-title">{currentBreadcrumb.title}</span>
            </div>

            {/* Active Workspace Chip */}
            {activeWorkspace && (
              <div className="soc-workspace-chip" title={`Current Workspace ID: ${activeWorkspace.workspace_id}`}>
                <span className="chip-dot" />
                <span className="chip-text">{activeWorkspace.name || 'Workspace'}</span>
              </div>
            )}
          </div>

          <div className="soc-topbar-right">
            {/* Authentic Degraded vs Operational Backend Status */}
            <div className={`soc-sys-status ${healthy === false ? 'degraded' : ''}`}>
              <span className={healthy === false ? 'soc-pulse-red' : healthy === true ? 'soc-pulse-green' : 'soc-pulse-yellow'}></span>
              <span>{healthy === false ? '● BACKEND OFFLINE' : healthy === true ? 'SYSTEM OPERATIONAL' : 'VERIFYING...'}</span>
            </div>

            <div className="soc-cloud-indicator">
              <span>☁ AWS · AZURE · GCP</span>
            </div>

            {/* In-App Feedback & Vulnerability Report Button */}
            <button
              type="button"
              className="soc-feedback-topbar-btn"
              onClick={() => setFeedbackModalOpen(true)}
              title="Report security observation or issue"
              aria-label="Report security feedback"
            >
              <MessageSquare size={13} />
              <span className="feedback-btn-text">Feedback</span>
            </button>

            {/* API Config Input */}
            <div className="api-cfg">
              <span className={`dot ${healthy === null ? '' : healthy ? 'up' : 'down'}`}></span>
              <label htmlFor="apiBase" style={{ fontSize: '11px', color: '#64748B' }}>API</label>
              <input
                id="apiBase"
                type="text"
                spellCheck={false}
                value={apiBaseVal}
                onChange={(e) => setApiBaseVal(e.target.value)}
                onBlur={commitApiBase}
                onKeyDown={(e) => e.key === 'Enter' && commitApiBase()}
                style={{ width: '130px', padding: '4px 8px', fontSize: '11px' }}
              />
            </div>

            {/* Theme Switcher: Immediately to the LEFT of the profile circle */}
            <div className="soc-theme-toggle-container">
              <ThemeToggle theme={theme} setTheme={setTheme} />
            </div>

            {/* Profile Circle: ABSOLUTE RIGHTMOST ITEM */}
            <div className="soc-profile-wrapper">
              <button
                type="button"
                id="navbar-profile-btn"
                className="soc-profile-circle-btn"
                onClick={() => setProfileDropdownOpen((prev) => !prev)}
                aria-label="User Account Profile"
                title={currentUser ? `${currentUser.name} (Account Menu)` : 'Account Menu'}
              >
                <span className="profile-circle-initials">
                  {currentUser?.avatar ? (
                    <img
                      src={currentUser.avatar}
                      alt={currentUser?.name || 'Avatar'}
                      style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                    />
                  ) : currentUser?.name ? (
                    currentUser.name
                      .split(' ')
                      .filter(Boolean)
                      .map((n) => n[0])
                      .join('')
                      .slice(0, 2)
                      .toUpperCase()
                  ) : (
                    'OP'
                  )}
                </span>
                <span className="profile-status-indicator" />
                <span className="sr-only">Profile</span>
              </button>

              {/* Floating Glass Dropdown Menu */}
              {profileDropdownOpen && (
                <div className="soc-profile-dropdown" role="menu">
                  <div className="dropdown-user-header">
                    <div className="dropdown-user-avatar">
                      {currentUser?.avatar ? (
                        <img
                          src={currentUser.avatar}
                          alt="Avatar"
                          style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                        />
                      ) : (
                        <User size={16} />
                      )}
                    </div>
                    <div className="dropdown-user-meta">
                      <div className="dropdown-user-name">{currentUser?.name || 'Security Operator'}</div>
                      <div className="dropdown-user-email">{currentUser?.email || 'Authenticated User'}</div>
                      <div className="dropdown-user-org">{currentUser?.orgName || currentUser?.org_name || 'Personal Workspace'}</div>
                    </div>
                  </div>

                  <div className="dropdown-divider" />

                  <Link
                    to="/profile"
                    className="dropdown-menu-item"
                    onClick={() => setProfileDropdownOpen(false)}
                  >
                    <User size={13} />
                    <span>Account Profile &amp; Security</span>
                  </Link>

                  <Link
                    to="/"
                    className="dropdown-menu-item"
                    onClick={() => setProfileDropdownOpen(false)}
                  >
                    <ExternalLink size={13} />
                    <span>Public Landing Page</span>
                  </Link>

                  <div className="dropdown-divider" />

                  <button
                    type="button"
                    className="dropdown-menu-item signout-btn"
                    onClick={() => {
                      setProfileDropdownOpen(false)
                      setLogoutConfirmOpen(true)
                    }}
                  >
                    <LogOut size={13} />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content Canvas */}
        <main className="soc-canvas" id="main-content">
          <div className="soc-page-container">
            {activeTab === 'dashboard' && (
              <SecurityCommandCenter
                onNavigate={(tab) => handleTabChange(tab)}
                workspaces={workspaces}
                currentUser={currentUser}
              />
            )}

            {activeTab === 'new-scan' && (
              <NewScanView
                onScan={handleScan}
                scanning={scanning}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'pipeline' && (
              <AgentPipelineView
                workspace={activeWorkspace}
                scanning={scanning}
                onNavigate={(tab) => handleTabChange(tab)}
                initialAgent={params.id}
              />
            )}

            {activeTab === 'findings' && (
              <FindingsView
                workspace={activeWorkspace}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'attack-map' && (
              <AttackPathView
                workspace={activeWorkspace}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'remediation' && (
              <RemediationView
                workspace={activeWorkspace}
                onDecide={handleDecide}
                onToast={showToast}
              />
            )}

            {activeTab === 'consensus' && (
              <ConsensusView
                workspace={activeWorkspace}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'audit' && (
              <AuditQueueView
                onToast={showToast}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'multicloud' && (
              <MultiCloudView
                workspaces={workspaces}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'compliance' && (
              <ComplianceView
                workspace={activeWorkspace}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'drift' && (
              <DriftView
                workspace={activeWorkspace}
                onToast={showToast}
                onNavigate={(tab) => handleTabChange(tab)}
              />
            )}

            {activeTab === 'research' && (
              <ResearchLabView workspaces={workspaces} />
            )}

            {activeTab === 'workspaces' && (
              <div className="scc-panel-card">
                <div className="scc-panel-head">
                  <div className="scc-panel-title">
                    <span>Workspace Scan Archives</span>
                  </div>
                  <button
                    className="btn-start-analysis"
                    style={{ padding: '6px 14px', fontSize: '12px' }}
                    onClick={() => handleTabChange('new-scan')}
                  >
                    + New Scan
                  </button>
                </div>

                {workspaces.length === 0 ? (
                  <div className="ws-empty" style={{ padding: '30px 0', textAlign: 'center' }}>
                    No saved workspace scans yet. Click "New Scan" to run your first template.
                  </div>
                ) : (
                  <WorkspaceList
                    workspaces={workspaces}
                    selectedId={activeWorkspace?.workspace_id}
                    onSelect={handleSelectWorkspace}
                  />
                )}

                {activeWorkspace && (
                  <div style={{ marginTop: '28px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px' }}>
                    <ReportView workspace={activeWorkspace} onDecide={handleDecide} />
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>

      <Toast
        message={toast.message}
        isError={toast.isError}
        onDone={() => setToast({ message: '', isError: false })}
      />

      {/* Accessible Logout Confirmation Dialog (Item 15) */}
      <ConfirmationModal
        isOpen={logoutConfirmOpen}
        onClose={() => setLogoutConfirmOpen(false)}
        onConfirm={() => {
          setLogoutConfirmOpen(false)
          logout()
          navigate('/sign-in')
        }}
        title="Sign Out of Security Operations"
        description="Are you sure you want to end your active session in the AgentShield SOC console?"
        confirmText="Sign Out"
        cancelText="Stay Signed In"
        danger={true}
      />

      {/* In-App Vulnerability & Feedback Modal (Item 18) */}
      <FeedbackModal
        isOpen={feedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
      />
    </div>
  )
}
