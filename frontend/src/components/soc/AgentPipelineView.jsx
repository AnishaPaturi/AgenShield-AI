import React, { useState } from 'react'

export default function AgentPipelineView({ workspace, scanning = false, onNavigate }) {
  const [selectedAgent, setSelectedAgent] = useState('manager')
  const logs = workspace?.execution_logs || []

  // Check which agents have actually completed based on execution logs
  const executedAgents = new Set(logs.map((l) => l.agent))

  const agentNodes = [
    {
      id: 'manager',
      name: 'Manager / Router Agent',
      engine: 'LangGraph Orchestrator',
      executed: executedAgents.has('Orchestrator') || scanning,
      input: 'Raw IaC Template (.tf, .yaml, .json)',
      output: 'Validated Session State & Dispatch',
      desc: 'Orchestrates non-linear execution across scanner nodes, tracks state checkpoints, and handles execution routing.',
    },
    {
      id: 'ast',
      name: 'Hybrid AST Parser Agent',
      engine: 'HCL2 / YAML / JSON Tree-Sitter',
      executed: executedAgents.has('Orchestrator') || executedAgents.has('ASTParser'),
      input: 'Raw template code strings',
      output: 'Normalized AST & Resource Graph',
      desc: 'Parses code into structured AST nodes, pre-evaluates variables, and unfolds loops.',
    },
    {
      id: 'secrets',
      name: 'Secrets Scanner Agent',
      engine: 'Gitleaks + TruffleHog Scanner',
      executed: executedAgents.has('Orchestrator') || executedAgents.has('SecretsScanner'),
      input: 'IaC content strings & environment definitions',
      output: 'Masked Cryptographic Tokens',
      desc: 'Intercepts AWS keys and tokens, redacting them locally before prompt evaluation.',
    },
    {
      id: 'rag',
      name: 'RAG Knowledge Agent',
      engine: 'Qdrant Vector DB',
      executed: executedAgents.has('SecurityAnalystAgent') || executedAgents.has('RAGAgent'),
      input: 'AST resource types & properties',
      output: 'CIS Benchmarks, NIST & SOC 2 Policy Controls',
      desc: 'Executes similarity search against cloud security policies to ground LLM reasoning in verified rules.',
    },
    {
      id: 'analyst',
      name: 'Security Analyst Agent',
      engine: 'Multi-LLM Ensemble',
      executed: executedAgents.has('SecurityAnalystAgent'),
      input: 'Enriched AST nodes & regulatory context',
      output: 'Calibrated vulnerability findings with blast radius scores',
      desc: 'Executes cross-model verification to identify vulnerabilities and assess risk.',
    },
    {
      id: 'attack',
      name: 'Attack-Path Prioritizer',
      engine: 'Graph Dependency Traversal',
      executed: executedAgents.has('FindingPrioritizer'),
      input: 'Vulnerability findings and resource graph',
      output: 'Prioritized attack paths and choke points',
      desc: 'Ranks findings based on graph-theoretical exploitability and blast radius.',
    },
    {
      id: 'remediation',
      name: 'Remediation Agent',
      engine: 'Deterministic Diff Generator',
      executed: executedAgents.has('RemediationAgent'),
      input: 'Vulnerability findings & target security posture',
      output: 'Unified Git Diff patch',
      desc: 'Synthesizes surgical patches targeting exact resource blocks without regressions.',
    },
    {
      id: 'validation',
      name: 'Validation Agent',
      engine: 'Static Linters & Runtime Sandbox',
      executed: executedAgents.has('ValidatorAgent'),
      input: 'Synthesized patch diff buffer',
      output: 'Compiler and linter validation results',
      desc: 'Tests patches against native syntax linters (terraform validate, cfn-lint) and verification checks.',
    },
  ]

  const activeNode = agentNodes.find((n) => n.id === selectedAgent) || agentNodes[0]

  return (
    <div className="pipeline-view">
      <div className="pipeline-hero">
        <h2>Autonomous Agent Execution Pipeline</h2>
        <p>
          Real-time telemetry and state transitions across the AgentShield AI LangGraph workflow.
        </p>
        <div style={{ marginTop: '14px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            className="btn-start-analysis"
            style={{ padding: '8px 18px', fontSize: '12.5px' }}
            onClick={() => onNavigate('new-scan')}
          >
            ⚡ Start New Scan
          </button>
          {workspace && (
            <button
              className="soc-back-home-btn"
              onClick={() => onNavigate('findings')}
            >
              View Findings ({workspace?.report?.findings?.length || 0}) →
            </button>
          )}
        </div>
      </div>

      {!workspace && !scanning ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8', maxWidth: '1080px', width: '100%' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Active Pipeline Execution
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            Upload or paste an IaC template to trigger the autonomous multi-agent pipeline and observe live execution telemetry.
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
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '28px', width: '100%', maxWidth: '1080px' }}>
          {/* Left: Workflow Node Graph */}
          <div className="pipeline-graph-container">
            {agentNodes.map((agent, idx) => (
              <React.Fragment key={agent.id}>
                <div
                  className={`pipeline-agent-box ${agent.executed ? 'completed' : scanning ? 'running' : ''} ${selectedAgent === agent.id ? 'active' : ''}`}
                  onClick={() => setSelectedAgent(agent.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <div>
                    <div className="pipeline-agent-title">{agent.name.toUpperCase()}</div>
                    <div className="pipeline-agent-sub">{agent.engine}</div>
                  </div>
                  <div className="pipeline-status-icon">
                    {agent.executed ? '✓' : scanning ? '⟳' : '○'}
                  </div>
                </div>
                {idx < agentNodes.length - 1 && <div className="pipeline-connector-line"></div>}
              </React.Fragment>
            ))}
          </div>

          {/* Right: Selected Node Details + Execution Trace Logs */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="pipeline-inspector-card">
              <div className="scc-panel-head">
                <div className="scc-panel-title">
                  <span className="flow-node-dot"></span>
                  Agent Node Telemetry
                </div>
                <span style={{ fontSize: '11px', color: activeNode.executed ? '#22C55E' : '#94A3B8', fontFamily: 'JetBrains Mono' }}>
                  {activeNode.executed ? '✓ EXECUTED' : scanning ? 'IN PROGRESS' : 'IDLE'}
                </span>
              </div>

              <div>
                <div className="inspector-section-label">AGENT NAME</div>
                <div className="inspector-section-val" style={{ color: '#FFFFFF', fontWeight: 600 }}>
                  {activeNode.name}
                </div>
              </div>

              <div>
                <div className="inspector-section-label">CORE ENGINE</div>
                <div className="inspector-section-val" style={{ fontFamily: 'JetBrains Mono', color: '#D6A84F' }}>
                  {activeNode.engine}
                </div>
              </div>

              <div>
                <div className="inspector-section-label">INPUT CONTRACT</div>
                <div className="inspector-section-val" style={{ color: '#CBD5E1' }}>
                  {activeNode.input}
                </div>
              </div>

              <div>
                <div className="inspector-section-label">OUTPUT ARTIFACT</div>
                <div className="inspector-section-val" style={{ color: '#CBD5E1' }}>
                  {activeNode.output}
                </div>
              </div>

              <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '12px' }}>
                <div className="inspector-section-label">RESPONSIBILITY &amp; ARCHITECTURE</div>
                <div className="inspector-section-val" style={{ color: '#94A3B8', lineHeight: '1.5' }}>
                  {activeNode.desc}
                </div>
              </div>
            </div>

            {/* Live Execution Logs */}
            {logs.length > 0 && (
              <div className="scc-panel-card" style={{ padding: '16px' }}>
                <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', fontWeight: 700, marginBottom: '8px', textTransform: 'uppercase' }}>
                  AUDIT TRACE LOGS ({logs.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                  {logs.map((l, i) => (
                    <div key={i} style={{ background: '#040609', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '6px', padding: '8px 10px', fontSize: '11.5px', fontFamily: 'JetBrains Mono' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#D6A84F' }}>
                        <span>{l.agent}</span>
                        <span style={{ color: '#64748B' }}>{l.action}</span>
                      </div>
                      <div style={{ color: '#94A3B8', marginTop: '3px' }}>
                        {Object.entries(l)
                          .filter(([k]) => k !== 'agent' && k !== 'action')
                          .map(([k, v]) => `${k}: ${v}`)
                          .join(' · ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
