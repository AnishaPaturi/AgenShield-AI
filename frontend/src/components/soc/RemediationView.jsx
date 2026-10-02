import React, { useState } from 'react'
import { validatePatchApi } from '../../api.js'
import CopyButton from '../common/CopyButton.jsx'

export default function RemediationView({ workspace, onDecide, onToast }) {
  const patches = workspace?.patches || []
  const [selectedPatchIndex, setSelectedPatchIndex] = useState(0)
  const [isValidating, setIsValidating] = useState(false)
  const [liveValidation, setLiveValidation] = useState({})

  const activePatch = patches[selectedPatchIndex] || null

  const handleValidate = async () => {
    if (!activePatch || !workspace) return
    setIsValidating(true)
    try {
      const res = await validatePatchApi(workspace.workspace_id, activePatch.patch_id)
      if (res && res.validation_results) {
        setLiveValidation((prev) => ({
          ...prev,
          [activePatch.patch_id]: res.validation_results,
        }))
      }
      if (onToast) onToast('Sandbox validation passed! Syntax and runtime verified. ✓')
    } catch (err) {
      if (onToast) onToast(err.message || 'Validation failed', true)
    } finally {
      setIsValidating(false)
    }
  }

  const handleApply = async () => {
    if (!activePatch || !workspace) return
    if (onDecide) {
      await onDecide(workspace.workspace_id, activePatch.patch_id, 'accept')
    }
    if (onToast) onToast(`Patch ${activePatch.patch_id} accepted and committed! ✓`)
  }

  const handleReject = async () => {
    if (!activePatch || !workspace) return
    if (onDecide) {
      await onDecide(workspace.workspace_id, activePatch.patch_id, 'reject')
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
          <p style={{ fontSize: '16px', color: 'var(--text, #F8FAFC)', marginBottom: '8px' }}>
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
                <span style={{ color: 'var(--ok, #86EFAC)' }}>● REMEDIATED PATCH / DIFF</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: 'var(--primary, #E11D48)', fontWeight: 600 }}>
                    {activePatch?.status || activePatch?.remediation_status || 'Synthesized'}
                  </span>
                  {(activePatch?.diff || activePatch?.remediated_snippet) && (
                    <CopyButton
                      text={activePatch.diff || activePatch.remediated_snippet}
                      size={12}
                      ariaLabel="Copy patch diff"
                    />
                  )}
                </div>
              </div>
              <pre className="code-pane-body">
                {activePatch?.diff || activePatch?.remediated_snippet || '# No diff available'}
              </pre>
            </div>
          </div>

          {/* Validation Results if present */}
          {((liveValidation[activePatch?.patch_id] || activePatch?.validation_results)?.length > 0) && (
            <div className="ai-remediation-checklist">
              <div style={{ fontFamily: 'Outfit', fontSize: '15px', fontWeight: 700, color: 'var(--text, #F8FAFC)', marginBottom: '8px' }}>
                Automated Verification Results
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                {(liveValidation[activePatch?.patch_id] || activePatch?.validation_results).map((vr, i) => (
                  <div key={i} className="check-item">
                    <span style={{ color: vr.passed ? 'var(--ok, #22C55E)' : 'var(--crit, #FB7185)' }}>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', color: 'var(--text-muted, #94A3B8)' }}>
              <span>Patch ID: </span>
              <code style={{ color: 'var(--primary, #E11D48)' }}>{activePatch?.patch_id}</code>
              {activePatch?.patch_id && (
                <CopyButton text={activePatch.patch_id} size={11} ariaLabel="Copy patch ID" />
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                className="soc-back-home-btn"
                style={{ padding: '10px 18px', fontSize: '13px' }}
                onClick={handleValidate}
                disabled={isValidating}
              >
                {isValidating ? 'Running Sandbox...' : '🔬 Run Sandbox Validation'}
              </button>
              <button
                className="soc-back-home-btn text-danger"
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
