import React, { useState } from 'react'

export default function RemediationView({ workspace, onDecide, onToast }) {
  const patches = workspace?.patches || []
  const [selectedPatchIndex, setSelectedPatchIndex] = useState(0)

  const activePatch = patches[selectedPatchIndex] || null

  const handleApply = async () => {
    if (!activePatch || !workspace) return
    if (onDecide) {
      await onDecide(workspace.workspace_id, activePatch.patch_id, 'approved')
    }
    if (onToast) onToast(`Patch ${activePatch.patch_id} approved and applied! ✓`)
  }

  const handleReject = async () => {
    if (!activePatch || !workspace) return
    if (onDecide) {
      await onDecide(workspace.workspace_id, activePatch.patch_id, 'rejected')
    }
    if (onToast) onToast(`Patch ${activePatch.patch_id} marked as rejected.`)
  }

  return (
    <div className="remediation-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Code + AI Remediation Workbench</h2>
          <p className="scc-subtitle">
            Executable Git diff patch synthesized by Remediation Agent with dual-stage linter &amp; runtime verification.
          </p>
        </div>
        {activePatch && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className={`status-tag ${activePatch.status || activePatch.remediation_status || 'PENDING'}`}>
              {activePatch.status || activePatch.remediation_status || 'PENDING'}
            </span>
          </div>
        )}
      </div>

      {patches.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Remediation Patches Available
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            {workspace
              ? 'No automated remediation patches were generated for this workspace.'
              : 'No workspace is currently selected. Run a scan on an IaC template to generate automated patches.'}
          </p>
        </div>
      ) : (
        <>
          {/* Patch Selector if multiple patches */}
          {patches.length > 1 && (
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {patches.map((p, idx) => (
                <button
                  key={p.patch_id || idx}
                  className={`tab-btn ${selectedPatchIndex === idx ? 'active' : ''}`}
                  onClick={() => setSelectedPatchIndex(idx)}
                >
                  Patch #{idx + 1} ({p.patch_id})
                </button>
              ))}
            </div>
          )}

          {/* Split Screen: BEFORE vs AFTER */}
          <div className="remediation-split">
            {/* Left: BEFORE (Vulnerable) */}
            <div className="code-pane">
              <div className="code-pane-header">
                <span style={{ color: '#FCA5A5' }}>● ORIGINAL SNIPPET</span>
                <span style={{ color: '#64748B' }}>
                  {activePatch?.file_path || workspace?.template?.file_path || 'template.iac'}
                </span>
              </div>
              <pre className="code-pane-body">
                {activePatch?.original_snippet || '# No original snippet available'}
              </pre>
            </div>

            {/* Right: AFTER (Remediated) */}
            <div className="code-pane">
              <div className="code-pane-header">
                <span style={{ color: '#86EFAC' }}>● REMEDIATED PATCH / DIFF</span>
                <span style={{ color: '#D6A84F' }}>
                  {activePatch?.status || activePatch?.remediation_status || 'Synthesized'}
                </span>
              </div>
              <pre className="code-pane-body">
                {activePatch?.diff || activePatch?.remediated_snippet || '# No diff available'}
              </pre>
            </div>
          </div>

          {/* Validation Results if present */}
          {activePatch?.validation_results && activePatch.validation_results.length > 0 && (
            <div className="ai-remediation-checklist">
              <div style={{ fontFamily: 'Outfit', fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '8px' }}>
                Automated Verification Results
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                {activePatch.validation_results.map((vr, i) => (
                  <div key={i} className="check-item">
                    <span style={{ color: vr.passed ? '#22C55E' : '#EF4444' }}>
                      {vr.passed ? '✓' : '✕'}
                    </span>{' '}
                    {vr.check_name}: {vr.passed ? 'Passed' : vr.error || 'Failed'}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ fontSize: '12.5px', color: '#94A3B8' }}>
              Patch ID: <code style={{ color: '#D6A84F' }}>{activePatch?.patch_id}</code>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                className="soc-back-home-btn"
                style={{ padding: '10px 20px', fontSize: '13px' }}
                onClick={handleReject}
              >
                ✕ Reject Patch
              </button>
              <button
                className="btn-start-analysis"
                style={{ padding: '10px 24px', fontSize: '13.5px' }}
                onClick={handleApply}
              >
                ✓ Apply &amp; Commit Patch →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
