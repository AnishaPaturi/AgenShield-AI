import { useState, useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  FileCode2,
  Lock,
  Search,
  Cpu,
  Network,
  GitPullRequest,
  Activity,
  Shield,
  Zap,
  CheckCircle2,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function AgentsSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)
  const [selectedAgent, setSelectedAgent] = useState(0)

  const agents = [
    {
      id: 'ast-parser',
      number: '01',
      name: 'Hybrid AST Parser Agent',
      shortRole: 'IaC Ingestion & AST Normalization',
      icon: FileCode2,
      color: '#38BDF8',
      engine: 'HCL2 / CFN / K8s / Helm Parser',
      description:
        'Converts disparate multi-cloud templates into normalized Abstract Syntax Trees, resolving dynamic variables and locals.',
      outputPayload: 'ASTNodeGraph(42 resources, 18 dependencies, 0 syntax errors)',
      codeSnippet: `resource "aws_s3_bucket" "prod_assets" {
  bucket = "\${var.env}-vault-\${local.region}"
  acl    = "public-read" # AST Node Flagged
}`,
    },
    {
      id: 'secrets-scanner',
      number: '02',
      name: 'Secrets Scanner Agent',
      shortRole: 'Zero-Leakage Interception',
      icon: Lock,
      color: '#F472B6',
      engine: 'Gitleaks + Shannon Entropy Filter',
      description:
        'Intercepts exposed API keys and high-entropy credentials locally before prompts ever touch cloud LLMs.',
      outputPayload: 'ZeroCredentialLeakageToken(masked: 3 secrets, entropy: 4.82)',
      codeSnippet: `secret_key = "[REDACTED_SHANNON_ENTROPY_4.8]"
api_token  = "[REDACTED_GITLEAKS_AWS_PAT]"`,
    },
    {
      id: 'security-analyst',
      number: '03',
      name: 'Security Analyst Agent',
      shortRole: 'Hybrid RAG Context Retrieval',
      icon: Search,
      color: '#A78BFA',
      engine: 'Qdrant Vector DB + Dense/Sparse Search',
      description:
        'Retrieves relevant CIS Benchmarks, NIST 800-53 controls, and MITRE ATT&CK techniques using semantic search.',
      outputPayload: 'ComplianceMatches(CIS_AWS_2.1.5, NIST_AC_6, SOC2_CC6.1)',
      codeSnippet: `vectors = qdrant.search(collection="cis_nist", limit=5)
# Top Match: CIS Amazon Web Services Benchmark v1.4.0 §2.1.5`,
    },
    {
      id: 'multi-llm-ensemble',
      number: '04',
      name: 'Multi-LLM Ensemble Agent',
      shortRole: 'Consensus Reasoning Engine',
      icon: Cpu,
      color: '#34D399',
      engine: 'Claude 3.5 Sonnet + GPT-4o Parallel Voting',
      description:
        'Orchestrates dual-model parallel evaluation with Chain-of-Thought reasoning and Platt-calibrated logit consensus.',
      outputPayload: 'ConsensusResult(score: 0.96, agreed: true, action: AUTO_PATCH)',
      codeSnippet: `C_ens = sum(w_i * conf_i) + gamma * agreement_factor
# Calibrated Confidence: 0.964 >= 0.85 Threshold`,
    },
    {
      id: 'attack-path-prioritizer',
      number: '05',
      name: 'Attack-Path Prioritizer Agent',
      shortRole: 'Topological BFS Traversal',
      icon: Network,
      color: '#FB923C',
      engine: 'Directed Graph BFS & Blast Engine',
      description:
        'Constructs an exploit dependency graph from ingress gateways to internal databases, identifying critical choke points.',
      outputPayload: 'ExploitRoute(IGW -> SG_5432 -> RDS -> IAM_Admin, Blast: 5)',
      codeSnippet: `[Internet] ──> [IGW: igw-089a] ──> [SG: sg-db : 5432]
  ──> [RDS: prod-postgres] ──> [IAM: AssumeRole Admin]`,
    },
    {
      id: 'sandbox-remediation',
      number: '06',
      name: 'Sandbox Remediation Agent',
      shortRole: 'Validated Patch Generation',
      icon: GitPullRequest,
      color: '#EC4899',
      engine: 'LocalStack Container + PR Generator',
      description:
        'Generates unified patch diffs, validates syntax in a containerized LocalStack environment, and creates pull requests.',
      outputPayload: 'ValidatedPatch(tests: 4/4 PASSED, PR: #42 opened)',
      codeSnippet: `- acl = "public-read"
+ acl = "private"
+ server_side_encryption_configuration { ... }`,
    },
  ]

  // Reversible scroll progress phases:
  // Phase 1 (>= 0.08): Orchestrator core appears
  // Phase 2 (>= 0.22): 6 Agent nodes emerge radially
  // Phase 3 (>= 0.42): Connection buses draw between core and nodes
  // Phase 4 (>= 0.62): Nodes activate with glow
  // Phase 5 (>= 0.80): Data packets travel along buses
  const isCoreVisible = progress >= 0.06 || prefersReduced
  const isNodesEmerging = progress >= 0.18 || prefersReduced
  const isBusDrawing = progress >= 0.36 || prefersReduced
  const isNodesActive = progress >= 0.54 || prefersReduced
  const isPacketsFlowing = progress >= 0.72 || prefersReduced

  const current = agents[selectedAgent]

  return (
    <section
      ref={sectionRef}
      className="agents-section cinematic-scene-stage"
      id="agents"
      aria-label="Multi-Agent LangGraph Network"
    >
      <div className="section-container agents-centered-container">
        {/* Section Header */}
        <div className="section-header-block text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              LANGGRAPH STATEFUL MULTI-AGENT DAG
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            SIX AUTONOMOUS AGENTS.
            <br />
            <span className="heading-gradient">ONE UNIFIED INTELLIGENCE.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Coordinated by a central state machine with formal input/output contracts,
            deterministic transitions, and zero hallucination propagation.
          </motion.p>
        </div>

        {/* The Autonomous Living Network (Centered Orchestrator + 6 Nodes) */}
        <div className="agents-network-stage">
          {/* SVG Connector Buses Canvas */}
          <svg className="agents-svg-canvas" viewBox="0 0 900 480" preserveAspectRatio="xMidYMid meet">
            <defs>
              <linearGradient id="busGrad01" x1="50%" y1="50%" x2="50%" y2="0%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#38BDF8" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="busGrad02" x1="50%" y1="50%" x2="10%" y2="50%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#F472B6" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="busGrad03" x1="50%" y1="50%" x2="90%" y2="50%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#A78BFA" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="busGrad04" x1="50%" y1="50%" x2="20%" y2="90%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#34D399" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="busGrad05" x1="50%" y1="50%" x2="80%" y2="90%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#FB923C" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="busGrad06" x1="50%" y1="50%" x2="50%" y2="100%">
                <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#EC4899" stopOpacity="0.8" />
              </linearGradient>
              <filter id="laserGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Central Orchestrator Core is at (450, 240) */}
            {/* Bus Lines connecting Core to each Node */}
            <g className="bus-lines-group" filter="url(#laserGlow)">
              {/* Bus to Agent 01 (Top: 450, 50) */}
              <line
                x1="450"
                y1="240"
                x2="450"
                y2="60"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad01)"
              />
              {/* Bus to Agent 02 (Middle Left: 150, 200) */}
              <line
                x1="450"
                y1="240"
                x2="150"
                y2="200"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad02)"
              />
              {/* Bus to Agent 03 (Middle Right: 750, 200) */}
              <line
                x1="450"
                y1="240"
                x2="750"
                y2="200"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad03)"
              />
              {/* Bus to Agent 04 (Lower Left: 200, 390) */}
              <line
                x1="450"
                y1="240"
                x2="200"
                y2="390"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad04)"
              />
              {/* Bus to Agent 05 (Lower Right: 700, 390) */}
              <line
                x1="450"
                y1="240"
                x2="700"
                y2="390"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad05)"
              />
              {/* Bus to Agent 06 (Bottom: 450, 420) */}
              <line
                x1="450"
                y1="240"
                x2="450"
                y2="420"
                className={`network-bus-line ${isBusDrawing ? 'bus-drawn' : ''}`}
                stroke="url(#busGrad06)"
              />
            </g>

            {/* Flowing Data Packets along buses */}
            {isPacketsFlowing && (
              <g className="data-packets-group">
                <circle cx="450" cy="150" r="4" fill="#38BDF8" className="packet-dot packet-v-up" />
                <circle cx="300" cy="220" r="4" fill="#F472B6" className="packet-dot packet-diag-left" />
                <circle cx="600" cy="220" r="4" fill="#A78BFA" className="packet-dot packet-diag-right" />
                <circle cx="325" cy="315" r="4" fill="#34D399" className="packet-dot packet-lower-left" />
                <circle cx="575" cy="315" r="4" fill="#FB923C" className="packet-dot packet-lower-right" />
                <circle cx="450" cy="330" r="4" fill="#EC4899" className="packet-dot packet-v-down" />
              </g>
            )}
          </svg>

          {/* Central Orchestrator Core Node (Exact Center) */}
          <div
            className={`network-core-node ${isCoreVisible ? 'core-visible' : 'core-hidden'} ${
              isNodesActive ? 'core-pulsing' : ''
            }`}
          >
            <div className="core-glow-aura" />
            <div className="core-inner-chip">
              <Zap size={22} className="core-icon" />
              <div className="core-label">AGENTSHIELD</div>
              <div className="core-sublabel">ORCHESTRATOR</div>
            </div>
            <div className="core-ring-orbit" />
          </div>

          {/* Six Autonomous Agent Nodes positioned symmetrically */}
          <div className="network-nodes-layer">
            {/* Agent 01: Top Center */}
            <div
              className={`network-agent-pod pod-top ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 0 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(0)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[0].color }}>
                <FileCode2 size={16} style={{ color: agents[0].color }} />
                <span>01</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[0].name}</span>
                <span className="pod-role">{agents[0].shortRole}</span>
              </div>
            </div>

            {/* Agent 02: Middle Left */}
            <div
              className={`network-agent-pod pod-mid-left ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 1 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(1)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[1].color }}>
                <Lock size={16} style={{ color: agents[1].color }} />
                <span>02</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[1].name}</span>
                <span className="pod-role">{agents[1].shortRole}</span>
              </div>
            </div>

            {/* Agent 03: Middle Right */}
            <div
              className={`network-agent-pod pod-mid-right ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 2 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(2)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[2].color }}>
                <Search size={16} style={{ color: agents[2].color }} />
                <span>03</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[2].name}</span>
                <span className="pod-role">{agents[2].shortRole}</span>
              </div>
            </div>

            {/* Agent 04: Lower Left */}
            <div
              className={`network-agent-pod pod-low-left ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 3 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(3)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[3].color }}>
                <Cpu size={16} style={{ color: agents[3].color }} />
                <span>04</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[3].name}</span>
                <span className="pod-role">{agents[3].shortRole}</span>
              </div>
            </div>

            {/* Agent 05: Lower Right */}
            <div
              className={`network-agent-pod pod-low-right ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 4 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(4)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[4].color }}>
                <Network size={16} style={{ color: agents[4].color }} />
                <span>05</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[4].name}</span>
                <span className="pod-role">{agents[4].shortRole}</span>
              </div>
            </div>

            {/* Agent 06: Bottom Center */}
            <div
              className={`network-agent-pod pod-bottom ${isNodesEmerging ? 'pod-emerged' : ''} ${
                selectedAgent === 5 ? 'pod-selected' : ''
              } ${isNodesActive ? 'pod-active' : ''}`}
              onClick={() => setSelectedAgent(5)}
              role="button"
              tabIndex={0}
            >
              <div className="pod-badge" style={{ borderColor: agents[5].color }}>
                <GitPullRequest size={16} style={{ color: agents[5].color }} />
                <span>06</span>
              </div>
              <div className="pod-info">
                <span className="pod-name">{agents[5].name}</span>
                <span className="pod-role">{agents[5].shortRole}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Centered Telemetry HUD Inspector Drawer */}
        <div className="agents-telemetry-hud">
          <div className="hud-header">
            <div className="hud-meta">
              <span className="hud-badge" style={{ color: current.color }}>
                AGENT {current.number} OF 06
              </span>
              <span className="hud-title">{current.name}</span>
              <span className="hud-engine">{current.engine}</span>
            </div>
            <div className="hud-live-tag">
              <Activity size={13} className="hud-live-icon" />
              <span>{isPacketsFlowing ? 'STATE: STREAMING' : isNodesActive ? 'STATE: ACTIVE' : 'STATE: READY'}</span>
            </div>
          </div>

          <div className="hud-body">
            <div className="hud-col-contract">
              <span className="hud-label">OUTPUT CONTRACT</span>
              <div className="hud-payload">{current.outputPayload}</div>
            </div>
            <div className="hud-col-code">
              <span className="hud-label">EXECUTION TRACE</span>
              <pre className="hud-pre">
                <code>{current.codeSnippet}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
