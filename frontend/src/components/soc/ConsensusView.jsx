import React, { useState } from 'react'

export default function ConsensusView({ onNavigate }) {
  const [demoMode, setDemoMode] = useState('high') // 'high' | 'split'

  const consensusScore = demoMode === 'high' ? '94.2%' : '71.4%'
  const isAutoPatch = demoMode === 'high'

  return (
    <div className="consensus-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Multi-LLM Ensemble Consensus Engine</h2>
          <p className="scc-subtitle">
            Cross-model verification between Claude 3.5 Sonnet and GPT-4o eradicates AI hallucinations
            prior to patch generation.
          </p>
        </div>

        {/* Toggle between High Consensus and Disagreement */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`tab-btn ${demoMode === 'high' ? 'active' : ''}`}
            onClick={() => setDemoMode('high')}
          >
            ✓ High Consensus Demo (94%)
          </button>
          <button
            className={`tab-btn ${demoMode === 'split' ? 'active' : ''}`}
            onClick={() => setDemoMode('split')}
          >
            ⚠ Model Disagreement Demo (71%)
          </button>
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="consensus-models-grid">
        {/* Model 1: Claude 3.5 Sonnet */}
        <div className="model-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="model-name">Claude 3.5 Sonnet</span>
            <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11px', color: '#D6A84F' }}>ANTHROPIC</span>
          </div>
          <div style={{ fontSize: '13px', color: '#CBD5E1' }}>
            Status: <b style={{ color: '#EF4444' }}>Threat Detected</b>
          </div>
          <div style={{ fontSize: '13px', color: '#94A3B8' }}>
            Confidence Assessment:{' '}
            <b style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
              {demoMode === 'high' ? '91%' : '91%'}
            </b>
          </div>
          <div style={{ background: '#040609', padding: '12px', borderRadius: '6px', fontSize: '12px', color: '#94A3B8', fontFamily: 'JetBrains Mono', lineHeight: '1.5' }}>
            "Identified IAM role allows unrestricted sts:AssumeRole across AWS accounts with missing external ID constraint."
          </div>
        </div>

        {/* Model 2: GPT-4o */}
        <div className="model-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="model-name">GPT-4o</span>
            <span style={{ fontFamily: 'JetBrains Mono', fontSize: '11px', color: '#38BDF8' }}>OPENAI</span>
          </div>
          <div style={{ fontSize: '13px', color: '#CBD5E1' }}>
            Status:{' '}
            <b style={{ color: demoMode === 'high' ? '#EF4444' : '#F59E0B' }}>
              {demoMode === 'high' ? 'Threat Detected' : 'Low Confidence'}
            </b>
          </div>
          <div style={{ fontSize: '13px', color: '#94A3B8' }}>
            Confidence Assessment:{' '}
            <b style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>
              {demoMode === 'high' ? '97%' : '63%'}
            </b>
          </div>
          <div style={{ background: '#040609', padding: '12px', borderRadius: '6px', fontSize: '12px', color: '#94A3B8', fontFamily: 'JetBrains Mono', lineHeight: '1.5' }}>
            {demoMode === 'high'
              ? '"Confirmed critical blast radius of 7 downstream assets. Resource is directly accessible via public ALB."'
              : '"Ambiguous resource exposure. Tags suggest staging environment with limited data sensitivity."'}
          </div>
        </div>
      </div>

      {/* Center Consensus Hub */}
      <div className="consensus-hub">
        <div style={{ fontSize: '12px', color: '#94A3B8', fontFamily: 'JetBrains Mono', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          ENSEMBLE CONSENSUS SCORE
        </div>
        <div className="consensus-pct">{consensusScore}</div>
        <div style={{ fontSize: '13px', color: '#CBD5E1', marginTop: '6px' }}>
          Agreement Level:{' '}
          <b style={{ color: isAutoPatch ? '#22C55E' : '#F97316' }}>
            {isAutoPatch ? 'HIGH · 4 of 4 Signals Matched' : 'LOW · Model Divergence Detected'}
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
              : 'Models disagree on severity and resource exposure. Finding escalated to human security audit queue.'}
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
    </div>
  )
}
