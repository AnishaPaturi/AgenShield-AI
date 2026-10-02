import React from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Cpu,
  Layers,
  FileCode,
  Check,
  Zap,
} from 'lucide-react'
import AtmosphericBackground from './AtmosphericBackground'
import CopyButton from '../common/CopyButton.jsx'

export default function SecurityCommandCenter({
  onNavigate,
  workspaces = [],
  currentUser = null,
}) {
  const prefersReduced = useReducedMotion()
  const latestWs = workspaces[0] || null

  const summary = latestWs?.report?.summary || {
    total_vulnerabilities: 0,
    critical_count: 0,
    high_count: 0,
    medium_count: 0,
    low_count: 0,
    risk_score: 0,
    human_review_count: 0,
    auto_patchable_count: 0,
  }

  const recentFindings = latestWs?.report?.findings?.slice(0, 5) || []
  const totalFindings = summary.total_vulnerabilities || 0
  const calcPct = (cnt) => (totalFindings > 0 ? Math.round((cnt / totalFindings) * 100) : 0)

  const postureScore = totalFindings > 0
    ? Math.max(0, Math.min(100, Math.round(100 - (summary.risk_score || 0))))
    : 100

  const autoPatchPct = totalFindings > 0
    ? (((summary.auto_patchable_count || 0) / totalFindings) * 100).toFixed(1)
    : '0.0'

  // Time-of-day greeting
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }
  const operatorName = currentUser?.name || 'Security Operator'

  // Backend Orchestrator agent stages
  const executionLogs = latestWs?.execution_logs || []
  const hasLog = (agentName) =>
    executionLogs.some((l) =>
      (l.agent || l.step || '').toLowerCase().includes(agentName.toLowerCase())
    )

  const isWsCompleted = latestWs?.status === 'completed'

  const agents = [
    {
      id: 'orchestrator',
      name: 'Orchestrator',
      role: 'AST Ingestion & Graph Router',
      telemetry: latestWs ? `${latestWs.filename || 'IaC Template'} Parsed` : 'Standby',
      completed: isWsCompleted || hasLog('orchestrator'),
      active: latestWs?.status === 'scanning' && !hasLog('analyst'),
      tab: 'pipeline',
    },
    {
      id: 'analyst',
      name: 'Security Analyst Agent',
      role: 'Deep AST & Policy Analysis',
      telemetry: totalFindings > 0 ? `${totalFindings} Rules Evaluated` : 'Standby',
      completed: isWsCompleted || hasLog('analyst') || hasLog('SecurityAnalystAgent'),
      active: latestWs?.status === 'scanning' && hasLog('orchestrator') && !hasLog('prioritizer'),
      tab: 'pipeline',
    },
    {
      id: 'prioritizer',
      name: 'Finding Prioritizer',
      role: 'Contextual Blast-Radius Scoring',
      telemetry: totalFindings > 0 ? `${summary.critical_count} Criticals Flagged` : 'Standby',
      completed: isWsCompleted || hasLog('prioritizer') || hasLog('FindingPrioritizer'),
      active: latestWs?.status === 'scanning' && hasLog('analyst') && !hasLog('remediation'),
      tab: 'findings',
    },
    {
      id: 'remediation',
      name: 'Remediation Agent',
      role: 'AI Diff Synthesis & Autofix',
      telemetry: totalFindings > 0 ? `${autoPatchPct}% Auto-Patchable` : 'Standby',
      completed: isWsCompleted || hasLog('remediation') || hasLog('RemediationAgent'),
      active: latestWs?.status === 'scanning' && hasLog('prioritizer') && !hasLog('validator'),
      tab: 'remediation',
    },
    {
      id: 'validator',
      name: 'Validator Agent',
      role: 'OPA / Rego Sandbox Verification',
      telemetry: latestWs?.patches?.some((p) => p.validation_results?.length > 0)
        ? 'Sandbox Verified'
        : hasLog('validator') || hasLog('ValidatorAgent')
        ? 'Linters Executed'
        : 'Standby',
      completed: isWsCompleted || hasLog('validator') || hasLog('ValidatorAgent'),
      active: latestWs?.status === 'scanning' && hasLog('remediation'),
      tab: 'pipeline',
    },
    {
      id: 'audit',
      name: 'Human Audit Queue',
      role: 'HITL Escalation & Governance',
      telemetry: `${summary.human_review_count || 0} Review Gates`,
      completed: isWsCompleted,
      active: latestWs?.status === 'review',
      tab: 'audit',
    },
  ]

  return (
    <div className="scc-view">
      {/* 1. Living Atmospheric Background (RESTRICTED TO HOMEPAGE ONLY) */}
      <AtmosphericBackground />

      {/* 2. Top Header Row with Time-of-Day Greeting & Live Status */}
      <div className="scc-header-row">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '11px',
                fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 600,
                color: 'var(--ok, #34D399)',
                background: 'var(--ok-bg, rgba(52, 211, 153, 0.1))',
                border: '1px solid var(--ok-border, rgba(52, 211, 153, 0.3))',
                borderRadius: '999px',
                padding: '3px 10px',
                letterSpacing: '0.04em',
              }}
            >
              <span
                style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--ok, #34D399)',
                  boxShadow: '0 0 8px var(--ok, #34D399)',
                }}
              />
              SYSTEM OPERATIONAL
            </span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted, #94A3B8)' }}>
              • Active Workspace: <b style={{ color: 'var(--text, #F8FAFC)' }}>{latestWs?.name || 'Default SOC'}</b>
            </span>
          </div>

          <h2 className="scc-title">
            {getGreeting()}, {operatorName}
          </h2>
          <p className="scc-subtitle">
            Autonomous multi-cloud IaC defense monitoring &amp; LangGraph agent telemetry.
          </p>
        </div>

        <button
          className="btn-start-analysis"
          style={{ padding: '11px 22px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}
          onClick={() => onNavigate('new-scan')}
        >
          <Zap size={15} />
          <span>New Security Scan</span>
        </button>
      </div>

      {/* 3. Top 4 Stat Cards with Animated Transitions */}
      <div className="scc-metrics-grid">
        <motion.div
          className="scc-metric-card scans"
          onClick={() => onNavigate('workspaces')}
          style={{ cursor: 'pointer' }}
          whileHover={prefersReduced ? {} : { y: -3 }}
          transition={{ duration: 0.2 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="scc-metric-label">Total Scans Executed</span>
            <Layers size={16} style={{ color: 'var(--secondary, #38BDF8)', opacity: 0.8 }} />
          </div>
          <div className="scc-metric-num">{workspaces.length}</div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted, #94A3B8)' }}>
            {workspaces.length > 0 ? 'SQLite Workspace Persistence' : 'Ready for first scan'}
          </span>
        </motion.div>

        <motion.div
          className="scc-metric-card critical"
          onClick={() => onNavigate('findings')}
          style={{ cursor: 'pointer' }}
          whileHover={prefersReduced ? {} : { y: -3 }}
          transition={{ duration: 0.2 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="scc-metric-label">Critical Findings</span>
            <AlertTriangle size={16} style={{ color: 'var(--crit, #FB7185)', opacity: 0.8 }} />
          </div>
          <div className="scc-metric-num">{summary.critical_count || 0}</div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted, #94A3B8)' }}>
            {summary.high_count || 0} high severity risks
          </span>
        </motion.div>

        <motion.div
          className="scc-metric-card score"
          whileHover={prefersReduced ? {} : { y: -3 }}
          transition={{ duration: 0.2 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="scc-metric-label">Secure Posture Score</span>
            <Shield size={16} style={{ color: 'var(--ok, #10B981)', opacity: 0.9 }} />
          </div>
          <div className="scc-metric-num">{postureScore}%</div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted, #94A3B8)' }}>
            Risk deduction: {summary.risk_score || 0} pts
          </span>
        </motion.div>

        <motion.div
          className="scc-metric-card queue"
          onClick={() => onNavigate('audit')}
          style={{ cursor: 'pointer' }}
          whileHover={prefersReduced ? {} : { y: -3 }}
          transition={{ duration: 0.2 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="scc-metric-label">Review Queue Pending</span>
            <Clock size={16} style={{ color: 'var(--high, #F59E0B)', opacity: 0.9 }} />
          </div>
          <div className="scc-metric-num">{summary.human_review_count || 0}</div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted, #94A3B8)' }}>
            Human-in-the-loop review gates
          </span>
        </motion.div>
      </div>

      {/* 4. Centerpiece Grid: Live Agent Activity + Real Risk Distribution */}
      <div className="scc-mid-grid">
        {/* Left: Signature Centerpiece — 6-Agent LangGraph Execution Visualization */}
        <div className="scc-panel-card">
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span className="flow-node-dot" />
              <span>AGENT ACTIVITY · LangGraph 6-Agent Execution</span>
            </div>
            <button
              className="soc-back-home-btn"
              style={{ fontSize: '11px', padding: '4px 12px' }}
              onClick={() => onNavigate('pipeline')}
            >
              View Full Pipeline →
            </button>
          </div>

          <p style={{ fontSize: '12.5px', color: 'var(--text-muted, #94A3B8)', margin: '0 0 18px' }}>
            Live orchestrator pipeline telemetry mapped to concrete execution logs from{' '}
            <code style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--primary, #E11D48)', fontSize: '11.5px' }}>
              {latestWs?.filename || 'Active Workspace'}
            </code>
            .
          </p>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '14px',
            }}
          >
            {agents.map((agent, idx) => (
              <motion.div
                key={agent.id}
                onClick={() => onNavigate(agent.tab)}
                style={{
                  background: 'var(--surface-2-glass, rgba(20, 26, 45, 0.55))',
                  border: agent.active
                    ? '1.5px solid var(--primary, #E11D48)'
                    : agent.completed
                    ? '1px solid var(--ok-border, rgba(52, 211, 153, 0.35))'
                    : '1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))',
                  borderRadius: '10px',
                  padding: '14px 16px',
                  cursor: 'pointer',
                  boxShadow: agent.active
                    ? '0 0 18px var(--primary-glow, rgba(225, 29, 72, 0.25))'
                    : 'none',
                  transition: 'all 0.25s ease',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                whileHover={prefersReduced ? {} : { y: -2, borderColor: 'var(--primary, #E11D48)' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        fontFamily: 'JetBrains Mono, monospace',
                        fontSize: '10px',
                        color: 'var(--text-muted, #94A3B8)',
                        background: 'rgba(255, 255, 255, 0.06)',
                        padding: '2px 6px',
                        borderRadius: '4px',
                      }}
                    >
                      STAGE {idx + 1}
                    </span>
                    <span
                      style={{
                        fontWeight: 700,
                        fontSize: '13px',
                        color: 'var(--text, #F8FAFC)',
                      }}
                    >
                      {agent.name}
                    </span>
                  </div>

                  {agent.completed ? (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '3px',
                        fontSize: '10.5px',
                        fontFamily: 'JetBrains Mono, monospace',
                        fontWeight: 700,
                        color: 'var(--ok, #34D399)',
                        background: 'var(--ok-bg, rgba(52, 211, 153, 0.12))',
                        padding: '2px 7px',
                        borderRadius: '999px',
                      }}
                    >
                      <Check size={11} /> DONE
                    </span>
                  ) : agent.active ? (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '10.5px',
                        fontFamily: 'JetBrains Mono, monospace',
                        fontWeight: 700,
                        color: 'var(--primary, #E11D48)',
                        background: 'var(--primary-dim, rgba(225, 29, 72, 0.15))',
                        padding: '2px 7px',
                        borderRadius: '999px',
                      }}
                    >
                      <span className="flow-node-dot" /> ACTIVE
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: '10.5px',
                        fontFamily: 'JetBrains Mono, monospace',
                        color: 'var(--muted, #64748B)',
                      }}
                    >
                      STANDBY
                    </span>
                  )}
                </div>

                <div style={{ fontSize: '11.5px', color: 'var(--text-muted, #94A3B8)', marginBottom: '10px' }}>
                  {agent.role}
                </div>

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderTop: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.06))',
                    paddingTop: '8px',
                    fontSize: '11px',
                    fontFamily: 'JetBrains Mono, monospace',
                    color: agent.completed ? 'var(--ok, #10B981)' : 'var(--muted, #64748B)',
                  }}
                >
                  <span>{agent.telemetry}</span>
                  <ArrowRight size={12} style={{ opacity: 0.7 }} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Right: Risk Distribution Panel */}
        <div className="scc-panel-card">
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span>Risk Distribution</span>
            </div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted, #94A3B8)', fontFamily: 'JetBrains Mono, monospace' }}>
              {totalFindings} TOTAL FINDINGS
            </span>
          </div>

          <div className="risk-dist-list">
            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: 'var(--crit, #FB7185)', fontWeight: 600 }}>● CRITICAL</span>
                <span>
                  {summary.critical_count || 0} ({calcPct(summary.critical_count || 0)}%)
                </span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill crit"
                  style={{ width: `${calcPct(summary.critical_count || 0)}%` }}
                />
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: 'var(--high, #F472B6)', fontWeight: 600 }}>● HIGH</span>
                <span>
                  {summary.high_count || 0} ({calcPct(summary.high_count || 0)}%)
                </span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill high"
                  style={{ width: `${calcPct(summary.high_count || 0)}%` }}
                />
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: 'var(--med, #94A3B8)', fontWeight: 600 }}>● MEDIUM</span>
                <span>
                  {summary.medium_count || 0} ({calcPct(summary.medium_count || 0)}%)
                </span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill med"
                  style={{ width: `${calcPct(summary.medium_count || 0)}%` }}
                />
              </div>
            </div>

            <div className="risk-dist-item">
              <div className="risk-dist-meta">
                <span style={{ color: 'var(--low, #64748B)', fontWeight: 600 }}>● LOW</span>
                <span>
                  {summary.low_count || 0} ({calcPct(summary.low_count || 0)}%)
                </span>
              </div>
              <div className="risk-dist-bar-track">
                <div
                  className="risk-dist-bar-fill low"
                  style={{ width: `${calcPct(summary.low_count || 0)}%` }}
                />
              </div>
            </div>
          </div>

          <div
            style={{
              marginTop: '22px',
              padding: '14px 16px',
              background: 'var(--surface-2-glass, rgba(18, 24, 33, 0.6))',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.06))',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: 'var(--text-muted, #94A3B8)',
                marginBottom: '8px',
              }}
            >
              <span>Auto-Patch Eligibility</span>
              <b style={{ color: 'var(--ok, #34D399)' }}>{autoPatchPct}%</b>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: 'var(--text-muted, #94A3B8)',
              }}
            >
              <span>Human Review Escalations</span>
              <b style={{ color: 'var(--high, #F472B6)' }}>{summary.human_review_count || 0} items</b>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Bottom Table: Recent Security Findings */}
      <div className="scc-panel-card">
        <div className="scc-panel-head">
          <div className="scc-panel-title">
            <span>Recent Security Findings</span>
          </div>
          {recentFindings.length > 0 && (
            <button
              className="soc-back-home-btn"
              style={{ fontSize: '11px', padding: '4px 12px' }}
              onClick={() => onNavigate('findings')}
            >
              View All Findings ({totalFindings}) →
            </button>
          )}
        </div>

        {recentFindings.length === 0 ? (
          <div
            style={{
              padding: '40px 16px',
              textAlign: 'center',
              color: 'var(--text-muted, #94A3B8)',
              fontSize: '13.5px',
            }}
          >
            <Shield
              size={36}
              style={{ color: 'var(--primary, #E11D48)', opacity: 0.5, margin: '0 auto 12px' }}
            />
            <p style={{ margin: '0 0 6px', fontWeight: 600, color: 'var(--text, #F8FAFC)' }}>
              No Security Findings In Active Workspace
            </p>
            <p style={{ margin: 0, fontSize: '12px' }}>
              Upload an IaC template under "New Security Scan" to trigger autonomous evaluation.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="scc-findings-table">
              <thead>
                <tr>
                  <th>SEVERITY</th>
                  <th>FINDING TITLE</th>
                  <th>RESOURCE / RULE</th>
                  <th>PRIORITY</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {recentFindings.map((f) => (
                  <tr key={f.finding_id || f.id}>
                    <td>
                      <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--text, #FFFFFF)' }}>{f.title}</td>
                    <td>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11.5px' }}>
                          {f.affected_resource || f.rule_id}
                        </span>
                        {(f.affected_resource || f.rule_id) && (
                          <CopyButton text={f.affected_resource || f.rule_id} size={11} ariaLabel="Copy resource or rule identifier" />
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="priority-score-badge">
                        {f.priority !== undefined && f.priority !== null
                          ? f.priority
                          : typeof f.confidence_score === 'number'
                          ? Math.round(f.confidence_score * 100)
                          : '—'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="scc-row-arrow-btn"
                        onClick={() => onNavigate('findings')}
                        title="Investigate finding"
                      >
                        Investigate →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
