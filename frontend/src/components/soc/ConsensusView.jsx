import React from 'react'

export default function ConsensusView({ workspace, onNavigate }) {
  const findings = workspace?.report?.findings || []
  const hasData = findings.length > 0

  // Calculate real average consensus score
  const validScores = findings
    .map((f) => f.consensus_score)
    .filter((s) => typeof s === 'number')

  const avgScore = validScores.length > 0
    ? validScores.reduce((a, b) => a + b, 0) / validScores.length
    : (workspace?.report?.summary?.consensus_score || 0)

  const consensusPct = Math.round(avgScore * 100)
  const isAutoPatch = avgScore >= 0.85

  // Extract model evaluations across findings
  const modelAgreements = {}
  findings.forEach((f) => {
    if (f.model_agreements && typeof f.model_agreements === 'object') {
      Object.entries(f.model_agreements).forEach(([model, score]) => {
        if (!modelAgreements[model]) modelAgreements[model] = []
        if (typeof score === 'number') modelAgreements[model].push(score)
      })
    }
  })

  const modelsList = Object.entries(modelAgreements).map(([model, scores]) => ({
    name: model,
    avg: Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 100),
    count: scores.length,
  }))

  return (
    <div className="consensus-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Multi-LLM Ensemble Consensus Engine</h2>
          <p className="scc-subtitle">
            Cross-model verification between diverse frontier models eradicates AI hallucinations
            prior to patch generation.
          </p>
        </div>
      </div>

      {!hasData ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Consensus Data Available
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            {workspace
              ? 'No findings were detected in the current workspace to evaluate consensus on.'
              : 'No workspace is currently selected. Run a scan on an IaC template to evaluate multi-model consensus.'}
          </p>
          <button
            className="btn-start-analysis"
            style={{ marginTop: '20px', padding: '8px 20px', fontSize: '13px' }}
            onClick={() => onNavigate('new-scan')}
          >
            ⚡ Run New Scan
          </button>
        </div>
      ) : (
        <>
          {/* Model Cards Grid */}
          <div className="consensus-models-grid">
            {modelsList.length > 0 ? (
              modelsList.map((m) => (
                <div key={m.name} className="model-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="model-name">{m.name}</span>
                    <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11px', color: '#D6A84F' }}>
                      ENSEMBLE NODE
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: '#CBD5E1' }}>
                    Evaluations: <b style={{ color: '#FFFFFF' }}>{m.count} findings</b>
                  </div>
                  <div style={{ fontSize: '13px', color: '#94A3B8' }}>
                    Confidence Index:{' '}
                    <b style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
                      {m.avg}%
                    </b>
                  </div>
                </div>
              ))
            ) : (
              <div className="model-card" style={{ gridColumn: '1 / -1' }}>
                <div style={{ fontSize: '14px', color: '#FFFFFF', fontWeight: 600 }}>
                  Active Ensemble Pipeline
                </div>
                <div style={{ fontSize: '12.5px', color: '#94A3B8', marginTop: '6px' }}>
                  Ensemble verification evaluated {findings.length} finding(s) across the active LLM cluster.
                </div>
              </div>
            )}
          </div>

          {/* Center Consensus Hub */}
          <div className="consensus-hub">
            <div style={{ fontSize: '12px', color: '#94A3B8', fontFamily: 'JetBrains Mono', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              ENSEMBLE CONSENSUS SCORE
            </div>
            <div className="consensus-pct">{consensusPct}%</div>
            <div style={{ fontSize: '13px', color: '#CBD5E1', marginTop: '6px' }}>
              Agreement Level:{' '}
              <b style={{ color: isAutoPatch ? '#22C55E' : '#F97316' }}>
                {isAutoPatch ? 'HIGH · Exceeds Safety Threshold' : 'LOW · Divergence Detected'}
              </b>
            </div>
          </div>

          {/* Decision Banner */}
          <div
            style={{
              background: isAutoPatch ? 'rgba(34, 197, 94, 0.1)' : 'rgba(249, 115, 22, 0.12)',
              border: `1px solid ${isAutoPatch ? 'rgba(34, 197, 94, 0.35)' : 'rgba(249, 115, 22, 0.35)'}`,
              borderRadius: '10px',
              padding: '20px 24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '14px',
            }}
          >
            <div>
              <div style={{ fontSize: '11px', color: isAutoPatch ? '#86EFAC' : '#FDBA74', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                GOVERNANCE DECISION
              </div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit', marginTop: '2px' }}>
                {isAutoPatch ? 'AUTO-REMEDIATION ELIGIBLE (C_ens >= 0.85)' : 'HUMAN REVIEW REQUIRED (C_ens < 0.85)'}
              </div>
              <div style={{ fontSize: '12.5px', color: '#94A3B8', marginTop: '4px' }}>
                {isAutoPatch
                  ? 'Consensus exceeds production safety threshold. Remediation Agent has generated verified patch.'
                  : 'Models disagree on severity or attack path. Finding escalated to human security audit queue.'}
              </div>
            </div>

            <button
              className="btn-start-analysis"
              style={{ padding: '10px 20px', fontSize: '13px' }}
              onClick={() => onNavigate(isAutoPatch ? 'remediation' : 'audit')}
            >
              {isAutoPatch ? 'Proceed to Auto-Patch →' : 'Open Human Audit Queue →'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
