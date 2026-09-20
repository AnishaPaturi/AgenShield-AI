import React, { useState, useEffect } from 'react'

export default function AgentPipelineView({ scanning = false, onNavigate }) {
  const [activeStep, setActiveStep] = useState(scanning ? 1 : 8)
  const [selectedAgent, setSelectedAgent] = useState('manager')
  const [isSimulating, setIsSimulating] = useState(false)

  // Simulation runner
  const startSimulation = () => {
    setIsSimulating(true)
    setActiveStep(0)
    let current = 0
    const interval = setInterval(() => {
      current += 1
      setActiveStep(current)
      if (current >= 8) {
        clearInterval(interval)
        setIsSimulating(false)
      }
    }, 700)
  }

  useEffect(() => {
    if (scanning) {
      startSimulation()
    }
  }, [scanning])

  const agentDetails = {
    manager: {
      name: 'Manager / Router Agent',
      engine: 'LangGraph StateGraph Engine',
      latency: '12ms',
      status: activeStep >= 1 ? '✓ Completed' : 'Waiting',
      input: 'Raw IaC Template (.tf, .yaml, .json)',
      output: 'Validated Session State & Parallel Execution Dispatch',
      desc: 'Orchestrates non-linear execution across parallel scanner nodes, tracks state checkpoints, and handles fault-tolerant fallbacks.',
    },
    ast: {
      name: 'Hybrid AST Parser Agent',
      engine: 'HCL2 / YAML / JSON Tree-Sitter',
      latency: '180ms',
      status: activeStep >= 2 ? '✓ Completed' : 'Waiting',
      input: 'Raw template code strings',
      output: 'Normalized AST & Resource Dependency Graph (RDG)',
      desc: 'Parses code into structured AST nodes, pre-evaluates variables/locals, and unfolds loops (for_each/count) to eliminate ambiguity.',
    },
    secrets: {
      name: 'Secrets Scanner Agent',
      engine: 'Gitleaks + TruffleHog + Entropy Scanner',
      latency: '95ms',
      status: activeStep >= 2 ? '✓ Completed (0 Leaks)' : 'Waiting',
      input: 'IaC content strings & environment definitions',
      output: 'Zero-Leakage Cryptographically Masked Tokens',
      desc: 'Intercepts AWS access keys, RSA private keys, and API tokens, redacting them locally before any data leaves for LLM evaluation.',
    },
    rag: {
      name: 'RAG Query Agent',
      engine: 'Qdrant Vector DB + MiniLM Embeddings',
      latency: '210ms',
      status: activeStep >= 3 ? '✓ Completed' : 'Waiting',
      input: 'AST resource types & properties',
      output: 'Top-3 CIS Benchmarks, NIST & SOC 2 Policy Controls',
      desc: 'Executes hybrid vector similarity and BM25 search against 50,000+ cloud security policies to ground LLM reasoning in verified rules.',
    },
    analyst: {
      name: 'Security Analyst Agent',
      engine: 'Claude 3.5 Sonnet + OpenAI GPT-4o Ensemble',
      latency: '1.4s',
      status: activeStep >= 4 ? '✓ Completed' : 'Waiting',
      input: 'Enriched AST nodes & regulatory context',
      output: 'Calibrated vulnerability findings with blast radius scores',
      desc: 'Executes cross-model verification to eradicate hallucinations. Findings with C_ens >= 0.85 proceed to auto-patching; others route to human triage.',
    },
    consensus: {
      name: 'Consensus Agent',
      engine: 'Ensemble Consensus Validator',
      latency: '45ms',
      status: activeStep >= 5 ? '✓ 94.7% Agreement' : 'Waiting',
      input: 'Dual LLM vulnerability classifications',
      output: 'Ensemble score C_ens = 0.947 · Auto-patch approved',
      desc: 'Calculates agreement index between Claude and GPT-4o. If models agree on severity and attack path, consensus is confirmed.',
    },
    remediation: {
      name: 'Remediation Agent',
      engine: 'Deterministic Diff Generator',
      latency: '820ms',
      status: activeStep >= 6 ? '✓ Patch Synthesized' : 'Waiting',
      input: 'Vulnerability AST node & target security posture',
      output: 'Unified Git Diff patch with zero syntax regressions',
      desc: 'Writes an executable patch targeting the exact resource block without modifying untouched configurations.',
    },
    validation: {
      name: 'Validation Agent',
      engine: 'LocalStack Runtime Sandbox + Native Linters',
      latency: '1.1s',
      status: activeStep >= 7 ? '✓ PASSED (0 Errors)' : 'Waiting',
      input: 'Synthesized patch diff buffer',
      output: 'Dry-run verified deployment in isolated LocalStack environment',
      desc: 'Tests patches against native syntax linters (terraform validate, cfn-lint) and executes dry-run infrastructure deployments.',
    },
    report: {
      name: 'Report Generator Agent',
      engine: 'SARIF / JSON / PDF Multi-Format Engine',
      latency: '85ms',
      status: activeStep >= 8 ? '✓ Generated' : 'Waiting',
      input: 'Validated findings, patches & compliance metrics',
      output: 'SARIF v2.1.0, JSON, Markdown & Executive PDF',
      desc: 'Exports compliance-ready reports mapped to SOC 2, HIPAA, PCI-DSS, and NIST controls.',
    },
  }

  const current = agentDetails[selectedAgent] || agentDetails.manager

  return (
    <div className="pipeline-view">
      <div className="pipeline-hero">
        <h2>Autonomous 8-Agent LangGraph Workflow</h2>
        <p>
          Real-time visualization of coordinated AI agents analyzing, auditing, synthesizing, and
          sandbox-validating infrastructure code.
        </p>
        <div style={{ marginTop: '14px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            className="btn-start-analysis"
            style={{ padding: '8px 18px', fontSize: '12.5px' }}
            onClick={startSimulation}
            disabled={isSimulating}
          >
            {isSimulating ? '⚡ Simulation Running...' : '▶ Run Live Pipeline Demo'}
          </button>
          <button
            className="soc-back-home-btn"
            onClick={() => onNavigate('remediation')}
          >
            Inspect Remediated Code →
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '28px', width: '100%', maxWidth: '1080px' }}>
        {/* Center: Interactive Workflow Graph */}
        <div className="pipeline-graph-container">
          {/* 1. MANAGER AGENT */}
          <div
            className={`pipeline-agent-box ${activeStep >= 1 ? 'completed' : isSimulating ? 'running' : ''}`}
            onClick={() => setSelectedAgent('manager')}
          >
            <div>
              <div className="pipeline-agent-title">MANAGER AGENT</div>
              <div className="pipeline-agent-sub">LangGraph Orchestrator · 12ms</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 1 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 2. PARALLEL: AST PARSER + SECRETS SCANNER */}
          <div className="pipeline-parallel-row">
            <div
              className={`pipeline-agent-box ${activeStep >= 2 ? 'completed' : activeStep === 1 ? 'running' : ''}`}
              style={{ width: '230px' }}
              onClick={() => setSelectedAgent('ast')}
            >
              <div>
                <div className="pipeline-agent-title">AST PARSER</div>
                <div className="pipeline-agent-sub">HCL2 / Tree-Sitter</div>
              </div>
              <div className="pipeline-status-icon">
                {activeStep >= 2 ? '✓' : '●'}
              </div>
            </div>

            <div
              className={`pipeline-agent-box ${activeStep >= 2 ? 'completed' : activeStep === 1 ? 'running' : ''}`}
              style={{ width: '230px' }}
              onClick={() => setSelectedAgent('secrets')}
            >
              <div>
                <div className="pipeline-agent-title">SECRETS AGENT</div>
                <div className="pipeline-agent-sub">Gitleaks Interceptor</div>
              </div>
              <div className="pipeline-status-icon">
                {activeStep >= 2 ? '✓' : '●'}
              </div>
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 3. RAG ENGINE */}
          <div
            className={`pipeline-agent-box ${activeStep >= 3 ? 'completed' : activeStep === 2 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('rag')}
          >
            <div>
              <div className="pipeline-agent-title">RAG ENGINE</div>
              <div className="pipeline-agent-sub">Qdrant Vector DB · 50k Rules</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 3 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 4. SECURITY ANALYST */}
          <div
            className={`pipeline-agent-box ${activeStep >= 4 ? 'completed' : activeStep === 3 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('analyst')}
          >
            <div>
              <div className="pipeline-agent-title">SECURITY ANALYST</div>
              <div className="pipeline-agent-sub">Claude 3.5 + GPT-4o Ensemble</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 4 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 5. CONSENSUS */}
          <div
            className={`pipeline-agent-box ${activeStep >= 5 ? 'completed' : activeStep === 4 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('consensus')}
          >
            <div>
              <div className="pipeline-agent-title">CONSENSUS AGENT</div>
              <div className="pipeline-agent-sub">Agreement: 94.7% ✓</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 5 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 6. REMEDIATION */}
          <div
            className={`pipeline-agent-box ${activeStep >= 6 ? 'completed' : activeStep === 5 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('remediation')}
          >
            <div>
              <div className="pipeline-agent-title">REMEDIATION AGENT</div>
              <div className="pipeline-agent-sub">Unified Git Diff Synthesizer</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 6 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 7. VALIDATION */}
          <div
            className={`pipeline-agent-box ${activeStep >= 7 ? 'completed' : activeStep === 6 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('validation')}
          >
            <div>
              <div className="pipeline-agent-title">VALIDATION AGENT</div>
              <div className="pipeline-agent-sub">LocalStack Sandbox ✓ PASSED</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 7 ? '✓' : '●'}
            </div>
          </div>

          <div className="pipeline-connector-line"></div>

          {/* 8. REPORT */}
          <div
            className={`pipeline-agent-box ${activeStep >= 8 ? 'completed' : activeStep === 7 ? 'running' : ''}`}
            onClick={() => setSelectedAgent('report')}
          >
            <div>
              <div className="pipeline-agent-title">REPORT GENERATOR</div>
              <div className="pipeline-agent-sub">SARIF / JSON / PDF Multi-Format</div>
            </div>
            <div className="pipeline-status-icon">
              {activeStep >= 8 ? '✓' : '●'}
            </div>
          </div>
        </div>

        {/* Right: Selected Agent Telemetry Inspector */}
        <div className="scc-panel-card" style={{ height: 'fit-content' }}>
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span className="flow-node-dot"></span>
              Agent Telemetry Inspector
            </div>
            <span style={{ fontSize: '11px', color: '#D6A84F', fontFamily: 'JetBrains Mono' }}>
              LIVE NODE
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                ACTIVE NODE
              </div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#FFFFFF', marginTop: '2px', fontFamily: 'Outfit' }}>
                {current.name}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '10px 12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10.5px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>LATENCY</div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', marginTop: '2px' }}>{current.latency}</div>
              </div>
              <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '10px 12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10.5px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>STATUS</div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#22C55E', marginTop: '2px' }}>{current.status}</div>
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                CORE ENGINE
              </div>
              <div style={{ fontSize: '13px', color: '#CBD5E1', marginTop: '2px' }}>{current.engine}</div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                ROLE &amp; FUNCTION
              </div>
              <div style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px', lineHeight: '1.55' }}>
                {current.desc}
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '14px' }}>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                INPUT PAYLOAD
              </div>
              <div style={{ fontSize: '12px', color: '#CBD5E1', fontFamily: 'JetBrains Mono', marginTop: '2px', background: '#040609', padding: '8px', borderRadius: '4px' }}>
                {current.input}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
                OUTPUT PAYLOAD
              </div>
              <div style={{ fontSize: '12px', color: '#86EFAC', fontFamily: 'JetBrains Mono', marginTop: '2px', background: '#040609', padding: '8px', borderRadius: '4px' }}>
                {current.output}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
