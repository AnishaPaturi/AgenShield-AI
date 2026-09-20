import React, { useMemo } from 'react'

export default function ResearchLabView({ workspaces = [] }) {
  const empiricalMetrics = useMemo(() => {
    let totalFindings = 0
    let totalPatches = 0
    let validatedPatches = 0
    let consensusSum = 0
    let consensusCount = 0
    let humanReviewCount = 0

    workspaces.forEach((ws) => {
      const findings = ws.report?.findings || []
      totalFindings += findings.length
      humanReviewCount += ws.report?.summary?.human_review_count || 0

      findings.forEach((f) => {
        if (typeof f.consensus_score === 'number') {
          consensusSum += f.consensus_score
          consensusCount += 1
        }
      })

      const patches = ws.patches || []
      totalPatches += patches.length
      patches.forEach((p) => {
        if (p.validation_results && p.validation_results.every((v) => v.passed)) {
          validatedPatches += 1
        }
      })
    })

    const avgConsensus = consensusCount > 0 ? Math.round((consensusSum / consensusCount) * 100) : 0
    const passRate = totalPatches > 0 ? Math.round((validatedPatches / totalPatches) * 100) : 100
    const autoPatchRate = totalFindings > 0 ? Math.round(((totalFindings - humanReviewCount) / totalFindings) * 100) : 100

    return [
      { label: 'Workspaces Evaluated', val: `${workspaces.length}`, sub: 'Active Scan Sessions', color: '#38BDF8' },
      { label: 'Total Findings Identified', val: `${totalFindings}`, sub: 'Vulnerabilities Triaged', color: '#F97316' },
      { label: 'Ensemble Consensus', val: `${avgConsensus}%`, sub: 'Multi-LLM Calibration', color: '#D6A84F' },
      { label: 'Patch Validation Rate', val: `${passRate}%`, sub: 'Passed Static Linters', color: '#22C55E' },
      { label: 'Auto-Remediation Rate', val: `${autoPatchRate}%`, sub: 'C_ens >= 0.85 Threshold', color: '#22C55E' },
      { label: 'Human Reviews Required', val: `${humanReviewCount}`, sub: 'Escalated to Audit Queue', color: '#EF4444' },
    ]
  }, [workspaces])

  return (
    <div className="research-lab-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">AgentShield AI Empirical Performance &amp; Evaluation</h2>
          <p className="scc-subtitle">
            Empirical runtime performance data and accuracy statistics calculated across active workspace scans.
          </p>
        </div>
      </div>

      {workspaces.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Empirical Scan Data Available
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            No workspace scans have been executed in this session yet. Run security scans on IaC templates to populate real-time empirical performance metrics.
          </p>
        </div>
      ) : (
        <div className="research-gauges-grid">
          {empiricalMetrics.map((m) => (
            <div key={m.label} className="research-gauge-card">
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                {m.label}
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: m.color, fontFamily: 'JetBrains Mono', margin: '6px 0 2px' }}>
                {m.val}
              </div>
              <div style={{ fontSize: '11px', color: '#94A3B8' }}>{m.sub}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
