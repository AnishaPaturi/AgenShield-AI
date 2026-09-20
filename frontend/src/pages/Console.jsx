import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
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
  const [activeTab, setActiveTab] = useState('dashboard') // 12 views
  const [healthy, setHealthy] = useState(null)
  const [workspaces, setWorkspaces] = useState([])
  const [currentWorkspace, setCurrentWorkspace] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [pendingCount, setPendingCount] = useState(3)
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
      setPendingCount(3)
    }
  }, [])

  useEffect(() => {
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
  }, [refreshHealth, refreshWorkspaces, refreshAuditStats])

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
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'remediation' && (
            <RemediationView
              onDecide={handleDecide}
              onToast={showToast}
            />
          )}

          {activeTab === 'consensus' && (
            <ConsensusView
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
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'compliance' && (
            <ComplianceView
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'drift' && (
            <DriftView
              onToast={showToast}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'research' && (
            <ResearchLabView />
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
