import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
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

export default function Console() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(getCurrentUser())
  const [activeTab, setActiveTab] = useState('dashboard') // 12 views
  const [healthy, setHealthy] = useState(null)
  const [workspaces, setWorkspaces] = useState([])
  const [currentWorkspace, setCurrentWorkspace] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [pendingCount, setPendingCount] = useState(0)
  const [toast, setToast] = useState({ message: '', isError: false })
  const [apiBaseVal, setApiBaseVal] = useState(getApiBase())

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
      navigate('/login')
      return
    }
    setCurrentUser(user)
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
  }, [navigate, refreshHealth, refreshWorkspaces, refreshAuditStats, showToast])

  async function handleScan(file, options = {}) {
    setScanning(true)
    setActiveTab('pipeline') // Switch to pipeline immediately to watch the agents execute!
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
    } catch (e) {
      showToast(e.message, true)
    }
  }

  async function handleDecide(patchId, decision) {
    if (!currentWorkspace) return
    try {
      await decidePatch(currentWorkspace.workspace_id, patchId, decision)
      showToast(`Patch ${decision === 'accept' ? 'accepted' : 'rejected'}`)
      const refreshed = await getWorkspace(currentWorkspace.workspace_id)
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

  return (
    <div className="soc-shell">
      {/* Top Security SOC Navigation Bar */}
      <header className="soc-topbar">
        <div className="soc-topbar-left">
          <Link to="/" className="soc-brand" title="AgentShield AI Home">
            <div className="soc-brand-shield">
              <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, fontSize: '13px', color: '#D6A84F' }}>
                AS
              </span>
            </div>
            <div className="soc-brand-name">
              AGENTSHIELD<span className="soc-brand-accent">AI</span>
            </div>
          </Link>

          <div className="soc-sys-status">
            <span className="soc-pulse-green"></span>
            <span>SYSTEM OPERATIONAL</span>
          </div>

          <div className="soc-cloud-indicator">
            <span>☁ AWS · AZURE · GCP</span>
          </div>
        </div>

        <div className="soc-topbar-right">
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
              style={{ width: '180px', padding: '5px 10px', fontSize: '11px' }}
            />
          </div>

          {currentUser && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 10px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', fontSize: '11.5px' }}>
              <span style={{ color: '#D6A84F', fontWeight: 600 }}>● {currentUser.name}</span>
              <button
                type="button"
                onClick={() => {
                  logout()
                  navigate('/login')
                }}
                style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', fontSize: '11px', textDecoration: 'underline' }}
                title="Sign out of console"
              >
                Sign Out
              </button>
            </div>
          )}

          <Link to="/" className="soc-back-home-btn" title="Back to Landing Page">
            ← Landing Page
          </Link>
        </div>
      </header>

      {/* 2-Column Body: Left Sidebar + Canvas */}
      <div className="soc-body">
        {/* Left Navigation Sidebar */}
        <aside className="soc-sidebar">
          {/* Group 1: OVERVIEW */}
          <div className="soc-nav-group">
            <div className="soc-nav-header">OVERVIEW</div>
            <button
              className={`soc-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Dashboard</span>
              </div>
            </button>
          </div>

          {/* Group 2: SCANNING */}
          <div className="soc-nav-group">
            <div className="soc-nav-header">SCANNING</div>
            <button
              className={`soc-nav-item ${activeTab === 'new-scan' ? 'active' : ''}`}
              onClick={() => setActiveTab('new-scan')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>New Scan</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'pipeline' ? 'active' : ''}`}
              onClick={() => setActiveTab('pipeline')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Agent Pipeline</span>
              </div>
              {scanning && <span className="spinner" style={{ width: '10px', height: '10px' }}></span>}
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'workspaces' ? 'active' : ''}`}
              onClick={() => setActiveTab('workspaces')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Workspaces</span>
              </div>
              {workspaces.length > 0 && (
                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '10.5px', color: '#64748B' }}>
                  {workspaces.length}
                </span>
              )}
            </button>
          </div>

          {/* Group 3: SECURITY */}
          <div className="soc-nav-group">
            <div className="soc-nav-header">SECURITY</div>
            <button
              className={`soc-nav-item ${activeTab === 'findings' ? 'active' : ''}`}
              onClick={() => setActiveTab('findings')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Findings</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'attack-map' ? 'active' : ''}`}
              onClick={() => setActiveTab('attack-map')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Attack Map</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'remediation' ? 'active' : ''}`}
              onClick={() => setActiveTab('remediation')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Remediation</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'consensus' ? 'active' : ''}`}
              onClick={() => setActiveTab('consensus')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>AI Consensus</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Audit Queue</span>
              </div>
              {pendingCount > 0 && <span className="soc-badge-counter">{pendingCount}</span>}
            </button>
          </div>

          {/* Group 4: KNOWLEDGE */}
          <div className="soc-nav-group">
            <div className="soc-nav-header">KNOWLEDGE</div>
            <button
              className={`soc-nav-item ${activeTab === 'multicloud' ? 'active' : ''}`}
              onClick={() => setActiveTab('multicloud')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Multi-Cloud</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'compliance' ? 'active' : ''}`}
              onClick={() => setActiveTab('compliance')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Compliance</span>
              </div>
            </button>

            <button
              className={`soc-nav-item ${activeTab === 'drift' ? 'active' : ''}`}
              onClick={() => setActiveTab('drift')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Drift Detection</span>
              </div>
            </button>
          </div>

          {/* Group 5: SYSTEM */}
          <div className="soc-nav-group">
            <div className="soc-nav-header">SYSTEM</div>
            <button
              className={`soc-nav-item ${activeTab === 'research' ? 'active' : ''}`}
              onClick={() => setActiveTab('research')}
            >
              <div className="soc-nav-item-left">
                <span className="soc-nav-bullet">◉</span>
                <span>Research Lab</span>
              </div>
            </button>
          </div>
        </aside>

        {/* Main Content Canvas */}
        <main className="soc-canvas">
          {activeTab === 'dashboard' && (
            <SecurityCommandCenter
              onNavigate={(tab) => setActiveTab(tab)}
              workspaces={workspaces}
            />
          )}

          {activeTab === 'new-scan' && (
            <NewScanView
              onScan={handleScan}
              scanning={scanning}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'pipeline' && (
            <AgentPipelineView
              workspace={currentWorkspace}
              scanning={scanning}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'findings' && (
            <FindingsView
              workspace={currentWorkspace}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'attack-map' && (
            <AttackPathView
              workspace={currentWorkspace}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'remediation' && (
            <RemediationView
              workspace={currentWorkspace}
              onDecide={handleDecide}
              onToast={showToast}
            />
          )}

          {activeTab === 'consensus' && (
            <ConsensusView
              workspace={currentWorkspace}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'audit' && (
            <AuditQueueView
              onToast={showToast}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'multicloud' && (
            <MultiCloudView
              workspaces={workspaces}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'compliance' && (
            <ComplianceView
              workspace={currentWorkspace}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'drift' && (
            <DriftView
              workspace={currentWorkspace}
              onToast={showToast}
              onNavigate={(tab) => setActiveTab(tab)}
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
                  onClick={() => setActiveTab('new-scan')}
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
                  selectedId={currentWorkspace?.workspace_id}
                  onSelect={handleSelectWorkspace}
                />
              )}

              {currentWorkspace && (
                <div style={{ marginTop: '28px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px' }}>
                  <ReportView workspace={currentWorkspace} onDecide={handleDecide} />
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      <Toast
        message={toast.message}
        isError={toast.isError}
        onDone={() => setToast({ message: '', isError: false })}
      />
    </div>
  )
}
