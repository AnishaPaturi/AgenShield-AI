import React, { useState, useEffect } from 'react'
import { scanDrift, getDrift } from '../../api.js'

export default function DriftView({ workspace, onToast, onNavigate }) {
  const [isScanning, setIsScanning] = useState(false)
  const [driftReport, setDriftReport] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!workspace?.workspace_id) {
      setDriftReport(null)
      return
    }

    async function load() {
      try {
        const report = await getDrift(workspace.workspace_id)
        if (report) setDriftReport(report)
      } catch (err) {
        // No cached drift report yet
      }
    }
    load()
  }, [workspace?.workspace_id])

  const handleScanDrift = async () => {
    if (!workspace?.workspace_id) return
    setIsScanning(true)
    setError(null)
    try {
      const report = await scanDrift(workspace.workspace_id)
      setDriftReport(report)
      if (onToast) {
        onToast(`Drift scan complete — ${report.total_drifts || 0} drift(s) detected.`)
      }
    } catch (err) {
      setError(err.message || 'Drift scan failed')
      if (onToast) onToast(err.message || 'Drift scan failed', true)
    } finally {
      setIsScanning(false)
    }
  }

  const drifts = driftReport?.drifts || []

  return (
    <div className="drift-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Live Cloud Infrastructure Drift Detection</h2>
          <p className="scc-subtitle">
            Continuous reconciliation between Git-defined IaC templates and runtime AWS/Azure/GCP cloud API state.
          </p>
        </div>
        {workspace && (
          <button
            className="btn-start-analysis"
            style={{ padding: '9px 20px', fontSize: '13px' }}
            onClick={handleScanDrift}
            disabled={isScanning}
          >
            {isScanning ? 'Scanning Cloud State...' : '⚡ Check Cloud Drift'}
          </button>
        )}
      </div>

      {!workspace ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Workspace Selected
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            Select an active workspace scan or run a new scan to check for cloud configuration drift against live runtime state.
          </p>
          <button
            className="btn-start-analysis"
            style={{ marginTop: '20px', padding: '8px 20px', fontSize: '13px' }}
            onClick={() => onNavigate('new-scan')}
          >
            ⚡ Run New Scan
          </button>
        </div>
      ) : drifts.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            {driftReport ? '✓ No Infrastructure Drift Detected' : 'Drift Scan Not Yet Executed'}
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            {driftReport
              ? 'All live cloud resources match the configurations declared in this workspace IaC template.'
              : 'Click "Check Cloud Drift" above to compare declared template state with live AWS/LocalStack resources.'}
          </p>
          {!driftReport && (
            <button
              className="btn-start-analysis"
              style={{ marginTop: '20px', padding: '8px 20px', fontSize: '13px' }}
              onClick={handleScanDrift}
              disabled={isScanning}
            >
              {isScanning ? 'Scanning Cloud State...' : '⚡ Check Cloud Drift'}
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {drifts.map((d, idx) => (
            <div key={d.drift_id || idx} className="scc-panel-card">
              <div className="scc-panel-head">
                <div className="scc-panel-title">
                  <span className="flow-node-dot" style={{ background: '#EF4444' }}></span>
                  <span>Drift: {d.resource_id}</span>
                </div>
                <span style={{ fontSize: '11px', color: '#EF4444', fontFamily: 'JetBrains Mono' }}>
                  {d.severity || 'HIGH'}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginTop: '12px' }}>
                <div style={{ background: '#040609', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '14px' }}>
                  <div style={{ fontSize: '11px', color: '#22C55E', fontFamily: 'JetBrains Mono', marginBottom: '8px' }}>
                    EXPECTED CONFIGURATION (IAC)
                  </div>
                  <pre style={{ margin: 0, fontFamily: 'JetBrains Mono', fontSize: '12px', color: '#86EFAC', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                    {typeof d.expected_state === 'object' ? JSON.stringify(d.expected_state, null, 2) : String(d.expected_state || 'N/A')}
                  </pre>
                </div>

                <div style={{ background: '#040609', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '14px' }}>
                  <div style={{ fontSize: '11px', color: '#EF4444', fontFamily: 'JetBrains Mono', marginBottom: '8px' }}>
                    ACTUAL LIVE STATE (CLOUD API)
                  </div>
                  <pre style={{ margin: 0, fontFamily: 'JetBrains Mono', fontSize: '12px', color: '#FCA5A5', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                    {typeof d.actual_state === 'object' ? JSON.stringify(d.actual_state, null, 2) : String(d.actual_state || 'N/A')}
                  </pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
