import { useCallback, useEffect, useState } from 'react'
import Header from '../components/Header.jsx'
import UploadPanel from '../components/UploadPanel.jsx'
import WorkspaceList from '../components/WorkspaceList.jsx'
import ReportView from '../components/ReportView.jsx'
import TriageDashboard from '../components/TriageDashboard.jsx'
import Toast from '../components/Toast.jsx'
import { checkHealth, listWorkspaces, getWorkspace, scanFile, decidePatch, getAuditQueueStats } from '../api.js'

export default function Console() {
  const [healthy, setHealthy] = useState(null)
  const [workspaces, setWorkspaces] = useState([])
  const [currentWorkspace, setCurrentWorkspace] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [viewMode, setViewMode] = useState('scan') // 'scan' | 'triage'
  const [pendingCount, setPendingCount] = useState(0)
  const [toast, setToast] = useState({ message: '', isError: false })

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
      setWorkspaces(list)
    } catch {
      setWorkspaces([])
    }
  }, [])

  const refreshAuditStats = useCallback(async () => {
    try {
      const stats = await getAuditQueueStats()
      setPendingCount(stats.pending_count || 0)
    } catch {
      setPendingCount(0)
    }
  }, [])

  useEffect(() => {
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
  }, [refreshHealth, refreshWorkspaces, refreshAuditStats])

  async function handleScan(file) {
    setScanning(true)
    try {
      const ws = await scanFile(file)
      showToast(`Scan complete — ${ws.report.summary.total_vulnerabilities} finding(s)`)
      await refreshWorkspaces()
      await refreshAuditStats()
      setCurrentWorkspace(ws)
    } catch (e) {
      showToast(e.message, true)
    } finally {
      setScanning(false)
    }
  }

  async function handleSelect(id) {
    try {
      const ws = await getWorkspace(id)
      setCurrentWorkspace(ws)
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

  function handleApiBaseChange() {
    refreshHealth()
    refreshWorkspaces()
    refreshAuditStats()
    setCurrentWorkspace(null)
  }

  return (
    <>
      <Header healthy={healthy} onApiBaseChange={handleApiBaseChange} />
      <div className="console-nav">
        <button
          className={`nav-tab ${viewMode === 'scan' ? 'active' : ''}`}
          onClick={() => setViewMode('scan')}
        >
          🛡️ Scanner &amp; Reports
        </button>
        <button
          className={`nav-tab ${viewMode === 'triage' ? 'active' : ''}`}
          onClick={() => {
            setViewMode('triage')
            refreshAuditStats()
          }}
        >
          ⚠️ Human Security Audit Queue {pendingCount > 0 && <span className="tab-badge">{pendingCount}</span>}
        </button>
      </div>

      {viewMode === 'triage' ? (
        <main className="triage-main-container">
          <TriageDashboard onToast={showToast} />
        </main>
      ) : (
        <div className="layout">
          <aside>
            <UploadPanel onScan={handleScan} scanning={scanning} />
            <div className="section-label">Scan history</div>
            <WorkspaceList
              workspaces={workspaces}
              selectedId={currentWorkspace?.workspace_id}
              onSelect={handleSelect}
            />
          </aside>
          <main>
            {currentWorkspace ? (
              <ReportView workspace={currentWorkspace} onDecide={handleDecide} />
            ) : (
              <div className="empty-state">
                <div className="glyph">◎</div>
                <div>Upload an Infrastructure-as-Code file to run<br />the full AgentShield pipeline.</div>
              </div>
            )}
          </main>
        </div>
      )}
      <Toast message={toast.message} isError={toast.isError} onDone={() => setToast({ message: '', isError: false })} />
    </>
  )
}

