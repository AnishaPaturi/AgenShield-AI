import { useState, useEffect } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import {
  FileCode2,
  Lock,
  Radar,
  Network,
  GitCompare,
  CheckCircle2,
  ChevronRight,
  Shield,
  Play,
  RotateCcw,
  Terminal,
  Activity,
  ArrowRight,
  Sparkles,
} from 'lucide-react'

export default function HowItWorks() {
  const [activeStage, setActiveStage] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(true)
  const prefersReduced = useReducedMotion()

  const stages = [
    {
      id: 'ingestion',
      stepNumber: '01',
      title: 'IaC Ingestion & AST Parsing',
      category: 'PARSER',
      agent: 'Hybrid AST Parser Agent',
      shortDesc: 'Polyglot template parsing with dynamic variable pre-resolution.',
      description:
        'Templates in Terraform (HCL2), CloudFormation (JSON/YAML), Kubernetes (YAML), or Helm are parsed into normalized Abstract Syntax Trees. Dynamic parameters, locals, and conditionals are pre-evaluated to eliminate ambiguity before semantic analysis.',
      tag: 'AST RESOLUTION',
      keyMechanism: 'Dynamic AST Pre-Evaluation & Unfolding',
      empiricalTarget: '4 Polyglot IaC Frameworks Supported',
      icon: FileCode2,
      visualType: 'ast',
      metrics: {
        format: 'Terraform HCL2 / CFN / K8s / Helm',
        nodesParsed: '42 Resource Blocks Normalized',
        dynamicVariables: 'Pre-Evaluated & Locals Resolved',
      },
    },
    {
      id: 'secrets',
      stepNumber: '02',
      title: 'Zero-Leakage Secret Interception',
      category: 'CREDENTIALS',
      agent: 'Secrets Scanner Agent',
      shortDesc: 'Cryptographic redaction prior to prompt transmission.',
      description:
        'Integrated Gitleaks and TruffleHog engines scan high-entropy strings and credential patterns. Exposed AWS access keys, private RSA keys, and API tokens are cryptographically redacted locally so zero raw credentials leave the perimeter.',
      tag: 'LOCAL MASKING',
      keyMechanism: 'High-Entropy Regex + Cryptographic Redaction',
      empiricalTarget: '0 Cleartext Credentials Transmitted to LLMs',
      icon: Lock,
      visualType: 'secrets',
      metrics: {
        engine: 'Gitleaks + TruffleHog + Shannon Scanner',
        entropyThreshold: 'Shannon Entropy > 4.5 Intercepted',
        leakStatus: '0 Credentials Sent to External APIs',
      },
    },
    {
      id: 'consensus',
      stepNumber: '03',
      title: 'Multi-LLM Ensemble Consensus',
      category: 'ENSEMBLE',
      agent: 'Security Analyst Agent + RAG Query',
      shortDesc: 'Dual-model parallel voting suppressing hallucinations.',
      description:
        'Anthropic Claude 3.5 Sonnet and OpenAI GPT-4o independently evaluate normalized AST nodes grounded with CIS benchmarks and SOC 2 / NIST controls retrieved via Qdrant vector search. Platt logit consensus scoring calibrates confidence.',
      tag: 'ENSEMBLE VOTING',
      keyMechanism: 'Platt Temperature Scaling Logit Consensus',
      empiricalTarget: '< 3% Hallucination Rate (C_ens >= 0.85)',
      icon: Radar,
      visualType: 'ensemble',
      metrics: {
        models: 'Claude 3.5 Sonnet + GPT-4o Parallel',
        calibratedScore: 'C_ens: 0.96 (High Confidence)',
        routing: 'Auto-Patch Authorization Granted',
      },
    },
    {
      id: 'attack-path',
      stepNumber: '04',
      title: 'Attack-Path & Blast-Radius Analysis',
      category: 'TOPOLOGY',
      agent: 'Attack-Path Prioritizer Engine',
      shortDesc: 'Topological BFS graph traversal from ingress to core assets.',
      description:
        'A topological dependency graph maps connections between perimeter ingress (Internet Gateways, public ALBs, open 0.0.0.0/0 Security Groups) and core databases. Identifies critical choke points whose remediation severs multiple attack vectors.',
      tag: 'GRAPH TOPOLOGY',
      keyMechanism: 'Breadth-First Exploit Route Discovery',
      empiricalTarget: 'Automated Choke Point Severing',
      icon: Network,
      visualType: 'graph',
      metrics: {
        exploitHops: '3 Intermediate Topological Hops',
        blastRadius: '5 Dependent Cloud Services',
        chokePoint: 'aws_security_group.ingress (Port 5432)',
      },
    },
    {
      id: 'remediation',
      stepNumber: '05',
      title: 'Unified Code Diff Synthesis',
      category: 'SYNTHESIS',
      agent: 'Remediation Agent',
      shortDesc: 'Direct resource-level Git diff generation.',
      description:
        'Rather than outputting natural language commentary, the Remediation Agent synthesizes clean, syntactically valid unified diff patches directly modifying declared resource properties.',
      tag: 'DIFF SYNTHESIS',
      keyMechanism: 'Targeted Code Diff Synthesizer',
      empiricalTarget: 'Resource-Level Precision Auto-Patching',
      icon: GitCompare,
      visualType: 'diff',
      metrics: {
        patchFormat: 'Unified Git Diff Patch',
        targetBlock: 'aws_security_group.ingress',
        diffLines: '+3 Additions / -2 Removals',
      },
    },
    {
      id: 'validation',
      stepNumber: '06',
      title: 'Linter & LocalStack Runtime Validation',
      category: 'VALIDATION',
      agent: 'Code & Sandbox Validator Agent',
      shortDesc: 'Pre-deployment verification in an emulated sandbox.',
      description:
        'The generated patch passes through static linters (terraform validate, cfn-lint) followed by a dry-run provisioning deployment inside a containerized LocalStack sandbox. Any syntax or runtime regression triggers automatic rollback.',
      tag: 'RUNTIME INTEGRITY',
      keyMechanism: 'Static Linters + Containerized Dry-Run',
      empiricalTarget: '100% Patch Syntax & Provision Validity',
      icon: CheckCircle2,
      visualType: 'sandbox',
      metrics: {
        syntaxCheck: 'terraform validate [PASS]',
        runtimeSandbox: 'LocalStack Container Dry-Run [OK]',
        finalStatus: '100% Verified for Production Merge',
      },
    },
  ]

  // Auto-play progression if user hasn't paused
  useEffect(() => {
    if (!isAutoPlaying) return
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % stages.length)
    }, 6000)
    return () => clearInterval(interval)
  }, [isAutoPlaying, stages.length])

  const current = stages[activeStage]
  const CurrentIcon = current.icon

  // 10-Step Scroll-Triggered Reveal Sequence
  const getCardVariants = (idx) => ({
    hidden: { opacity: 0, y: prefersReduced ? 0 : 25 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        delay: prefersReduced ? 0 : 0.4 + idx * 0.14,
        duration: prefersReduced ? 0.1 : 0.6,
        ease: [0.16, 1, 0.3, 1],
      },
    },
  })

  return (
    <section className="how-it-works-section" id="how-it-works" aria-label="How AgentShield Works">
      <div className="section-container">
        {/* Section Header with Tightened Composition */}
        <div className="section-header-block text-center pipeline-header-tight">
          {/* Step 1: Eyebrow appears */}
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              AUTONOMOUS VERIFICATION PIPELINE
            </span>
          </motion.div>

          {/* Step 1: Heading appears */}
          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            FROM CODE TO VALIDATED RUNTIME.
            <br />
            <span className="heading-gradient">ONE CONTINUOUS SYSTEM.</span>
          </motion.h2>

          {/* Step 2: Description appears */}
          <motion.p
            className="section-subheading max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.25 }}
          >
            Information flows autonomously through six connected verification stages. Click any
            agent stage to inspect its live control surface and validation telemetry.
          </motion.p>
        </div>

        {/* Ingress / Egress Pipeline Meta Banner */}
        <div className="pipeline-flow-markers">
          <div className="flow-marker start">
            <span className="marker-pip" />
            <span>INGRESS: DECLARED IaC TEMPLATES</span>
          </div>
          <div className="flow-marker-line" />
          <div className="flow-marker end">
            <span className="marker-pip ok" />
            <span>EGRESS: VALIDATED RUNTIME PATCH</span>
          </div>
        </div>

        {/* 1. HORIZONTAL 6-STAGE CENTERED GLOSSY PIPELINE */}
        <div className="glossy-pipeline-track">
          {stages.map((stage, idx) => {
            const isActive = activeStage === idx
            const isCompleted = activeStage > idx
            const StageIcon = stage.icon

            return (
              <div key={stage.id} className="pipeline-stage-cell">
                {/* Steps 3-8: Agent 01-06 appear staggered */}
                <motion.button
                  type="button"
                  variants={getCardVariants(idx)}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-40px' }}
                  onClick={() => {
                    setActiveStage(idx)
                    setIsAutoPlaying(false)
                  }}
                  className={`glossy-pipeline-card ${isActive ? 'is-active' : ''} ${
                    isCompleted ? 'is-completed' : ''
                  }`}
                  aria-selected={isActive}
                  aria-label={`Stage ${stage.stepNumber}: ${stage.title}`}
                >
                  {/* Glass Reflection Sheen */}
                  <div className="glass-reflection-sheen" />

                  {/* Card Header: 01 and tiny status indicator */}
                  <div className="pipeline-card-top">
                    <span className="card-stage-num">{stage.stepNumber}</span>
                    <span
                      className={`card-status-dot ${
                        isActive ? 'active-pulse' : isCompleted ? 'completed-dot' : 'pending-dot'
                      }`}
                    />
                  </div>

                  {/* Card Center: Minimal line icon */}
                  <div className="pipeline-card-icon-wrap">
                    <StageIcon size={20} className="stage-icon-svg" strokeWidth={2.2} />
                  </div>

                  {/* Card Title */}
                  <div className="pipeline-card-title">{stage.title}</div>

                  {/* Card Category Tag */}
                  <div className="pipeline-card-category">{stage.category}</div>

                  {/* Active Card Subtle Red Glow Contour */}
                  {isActive && <div className="card-active-glow" />}
                </motion.button>

                {/* Step 9: Animated Connecting Arrow & Pulse Wire */}
                {idx < stages.length - 1 && (
                  <>
                    <motion.div
                      className="pipeline-connector-line desktop-only-connector"
                      aria-hidden="true"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: prefersReduced ? 0 : 1.3, duration: 0.5 }}
                    >
                      <div className="connector-wire" />
                      <div className={`connector-pulse-particle ${isActive ? 'accelerated' : ''}`} />
                      <div className="connector-arrowhead">▶</div>
                    </motion.div>

                    <div className="pipeline-connector-vertical mobile-only-connector" aria-hidden="true">
                      <div className="connector-wire-vertical" />
                      <div className="connector-pulse-particle-v" />
                      <div className="connector-arrowhead-v">▼</div>
                    </div>
                  </>
                )}
              </div>
            )
          })}
        </div>

        {/* Step 10: ACTIVE STAGE DETAIL PANEL (CONTROL SURFACE) REVEAL */}
        <motion.div
          className="pipeline-control-surface"
          initial={{ opacity: 0, y: prefersReduced ? 0 : 35 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.75, delay: prefersReduced ? 0 : 1.45, ease: [0.16, 1, 0.3, 1] }}
        >
          {/* Soft atmospheric background glow */}
          <div className="control-surface-glow" />

          {/* Translucent Glass Control Surface Frame */}
          <div className="control-surface-panel">
            {/* Control Surface Top Bar */}
            <div className="control-surface-topbar">
              <div className="topbar-left">
                <div className="active-stage-badge">
                  <span className="stage-pulse-beacon" />
                  <span>STAGE {current.stepNumber} / 06</span>
                  <span className="stage-tag-pill">{current.tag}</span>
                </div>
                <h3 className="control-stage-title">{current.title}</h3>
                <div className="control-agent-meta">
                  <Shield size={14} className="control-shield-icon" />
                  <span>{current.agent}</span>
                </div>
              </div>

              {/* Scrubber Controls */}
              <div className="topbar-right-controls">
                <button
                  type="button"
                  className="control-playback-btn"
                  onClick={() => setIsAutoPlaying(!isAutoPlaying)}
                  title={isAutoPlaying ? 'Pause Auto-Progression' : 'Resume Auto-Progression'}
                >
                  {isAutoPlaying ? (
                    <>
                      <span className="playback-pulse-dot" />
                      <span>LIVE SCRUBBING ({activeStage + 1}/6)</span>
                    </>
                  ) : (
                    <>
                      <Play size={12} fill="currentColor" />
                      <span>RESUME AUTO-RUN</span>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  className="control-step-next-btn"
                  onClick={() => {
                    setActiveStage((prev) => (prev + 1) % stages.length)
                    setIsAutoPlaying(false)
                  }}
                >
                  <span>Next Stage</span>
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>

            {/* Split Control Surface Body: Left Info / Right Live Terminal Console */}
            <div className="control-surface-body-grid">
              {/* Left Column: Architectural Specs & Telemetry */}
              <div className="surface-info-col">
                <p className="surface-description-text">{current.description}</p>

                <div className="surface-specs-divider" />

                <div className="surface-mechanism-row">
                  <div className="mechanism-item">
                    <span className="spec-label">KEY MECHANISM</span>
                    <span className="spec-value">{current.keyMechanism}</span>
                  </div>
                  <div className="mechanism-item">
                    <span className="spec-label">EMPIRICAL TARGET</span>
                    <span className="spec-value-accent">{current.empiricalTarget}</span>
                  </div>
                </div>

                {/* Telemetry Card */}
                <div className="surface-telemetry-box">
                  <div className="telemetry-header">
                    <Activity size={13} className="telemetry-icon" />
                    <span>RUNTIME TELEMETRY STREAM</span>
                  </div>
                  <div className="telemetry-rows">
                    {Object.entries(current.metrics).map(([k, v]) => (
                      <div key={k} className="telemetry-row-item">
                        <span className="row-k">{k.replace(/([A-Z])/g, ' $1').toUpperCase()}:</span>
                        <span className="row-v">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Live Validation Console (Integrated Glass Terminal) */}
              <div className="surface-console-col">
                <div className="integrated-glass-terminal">
                  {/* Terminal Header */}
                  <div className="terminal-header-bar">
                    <div className="terminal-traffic-lights">
                      <span className="terminal-dot red" />
                      <span className="terminal-dot yellow" />
                      <span className="terminal-dot green" />
                    </div>
                    <div className="terminal-center-title">
                      <Terminal size={12} className="terminal-icon-mini" />
                      <span>agentshield://engine/stage-{current.stepNumber}-validation.live</span>
                    </div>
                    <div className="terminal-live-badge">
                      <span className="live-blip" />
                      <span>LIVE</span>
                    </div>
                  </div>

                  {/* Morphing Stage Output Canvas */}
                  <div className="terminal-content-canvas">
                    <AnimatePresence mode="wait">
                      <motion.div
                        key={current.id}
                        className="terminal-stage-content"
                        initial={{ opacity: 0, y: prefersReduced ? 0 : 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: prefersReduced ? 0 : -12 }}
                        transition={{ duration: prefersReduced ? 0.05 : 0.35, ease: [0.16, 1, 0.3, 1] }}
                      >
                        {/* STAGE 01: AST PARSER LIVE CONSOLE */}
                        {current.visualType === 'ast' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield parse --format=hcl2 main.tf --resolve-locals
                            </div>
                            <div className="console-output-box">
                              <div className="console-code-tree">
                                <span className="tree-node root">IaCTemplate: "main.tf" [HCL2]</span>
                                <br />
                                ├── <span className="tree-node res">Resource: "aws_security_group.ingress"</span>
                                <br />
                                │   ├── <span className="tree-prop">ingress.cidr_blocks</span> = <span className="tree-val-crit">["0.0.0.0/0"]</span>
                                <br />
                                │   └── <span className="tree-prop">ingress.from_port</span> = <span className="tree-val">5432</span>
                                <br />
                                └── <span className="tree-node res">Resource: "aws_db_instance.postgres"</span>
                                <br />
                                    ├── <span className="tree-prop">storage_encrypted</span> = <span className="tree-val-crit">false</span>
                                <br />
                                    └── <span className="tree-prop">vpc_security_group_ids</span> = <span className="tree-val-ref">&lt;ref: aws_security_group.ingress.id&gt;</span>
                              </div>
                            </div>
                            <div className="console-status-strip ok">
                              <span className="status-symbol">✓</span>
                              <span>DYNAMIC VARIABLES PRE-EVALUATED • AST TREE EXTRACTED</span>
                            </div>
                          </div>
                        )}

                        {/* STAGE 02: SECRETS INTERCEPTION CONSOLE */}
                        {current.visualType === 'secrets' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield scan-secrets --entropy=shannon --mask=local-crypto
                            </div>
                            <div className="console-output-box">
                              <div className="terminal-check-table">
                                <div className="term-check-row">
                                  <span className="term-check-dot crit" />
                                  <span className="term-check-name">Gitleaks Interceptor: AWS Access Key</span>
                                  <span className="term-check-status crit">INTERCEPTED</span>
                                </div>
                                <div className="code-redaction-preview">
                                  <div className="code-diff-unmasked">
                                    <span className="diff-ln">14</span> password = <span className="redact-red">"AKIAIOSFODNN7EXAMPLE_SECRET_982"</span>
                                  </div>
                                  <div className="redact-arrow-label">↓ Local Zero-Knowledge Redaction Applied</div>
                                  <div className="code-diff-masked">
                                    <span className="diff-ln">14</span> password = <span className="redact-green">"[REDACTED_SHANNON_HASH_b7f2a]"</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="console-status-strip ok">
                              <span className="status-symbol">✓</span>
                              <span>0 CLEARTEXT CREDENTIALS SENT TO CLOUD LLM APIS</span>
                            </div>
                          </div>
                        )}

                        {/* STAGE 03: ENSEMBLE CONSENSUS CONSOLE */}
                        {current.visualType === 'ensemble' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield ensemble --models=claude-3.5-sonnet,gpt-4o --calibrate
                            </div>
                            <div className="console-output-box">
                              <div className="ensemble-terminal-grid">
                                <div className="ensemble-model-col">
                                  <div className="col-top">
                                    <span className="m-name">Claude 3.5 Sonnet</span>
                                    <span className="m-conf">Conf: 0.97</span>
                                  </div>
                                  <div className="m-finding-pill crit">CKV_AWS_20: Storage Unencrypted</div>
                                  <div className="m-finding-pill high">AS-AWS-001: 0.0.0.0/0 Ingress</div>
                                </div>
                                <div className="ensemble-model-col">
                                  <div className="col-top">
                                    <span className="m-name">OpenAI GPT-4o</span>
                                    <span className="m-conf">Conf: 0.95</span>
                                  </div>
                                  <div className="m-finding-pill crit">CKV_AWS_20: Encryption Required</div>
                                  <div className="m-finding-pill high">AS-AWS-001: Wide Perimeter Port</div>
                                </div>
                              </div>
                              <div className="concordance-meter-wrap">
                                <div className="meter-label-row">
                                  <span>Platt-Calibrated Agreement (S_agreement):</span>
                                  <span className="meter-score">96.4% Concordance</span>
                                </div>
                                <div className="meter-track">
                                  <div className="meter-fill" style={{ width: '96.4%' }} />
                                </div>
                              </div>
                            </div>
                            <div className="console-status-strip ok">
                              <span className="status-symbol">✓</span>
                              <span>CONCORDANCE VERIFIED (C_ens &ge; 0.85) • PROCEED TO AUTO-PATCH</span>
                            </div>
                          </div>
                        )}

                        {/* STAGE 04: ATTACK PATH & GRAPH CONSOLE */}
                        {current.visualType === 'graph' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield analyze-path --bfs-traverse --choke-points
                            </div>
                            <div className="console-output-box">
                              <div className="attack-path-flow-diagram">
                                <div className="path-step-node">
                                  <span className="step-tag">INGRESS</span>
                                  <span className="step-name">Internet (0.0.0.0/0)</span>
                                </div>
                                <div className="path-step-arrow">➔</div>
                                <div className="path-step-node choke">
                                  <span className="step-tag choke">CHOKE POINT</span>
                                  <span className="step-name">aws_security_group.ingress</span>
                                </div>
                                <div className="path-step-arrow">➔</div>
                                <div className="path-step-node asset">
                                  <span className="step-tag asset">TARGET ASSET</span>
                                  <span className="step-name">aws_db_instance.postgres</span>
                                </div>
                              </div>
                              <div className="choke-mitigation-note">
                                <strong>Choke Point Discovery:</strong> Remediation of Security Group ingress
                                severs multi-hop exploit route before database perimeter breach.
                              </div>
                            </div>
                            <div className="console-status-strip crit">
                              <span className="status-symbol">●</span>
                              <span>CRITICAL ATTACK PATH MAPPED • BLAST RADIUS: 5 SERVICES</span>
                            </div>
                          </div>
                        )}

                        {/* STAGE 05: UNIFIED DIFF CONSOLE */}
                        {current.visualType === 'diff' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield remediate --target=main.tf --format=unified-diff
                            </div>
                            <div className="console-output-box">
                              <div className="console-diff-viewer">
                                <div className="diff-meta-line">--- a/main.tf (Original Declared IaC)</div>
                                <div className="diff-meta-line">+++ b/main.tf (AgentShield Synthesized Patch)</div>
                                <div className="diff-ln-ctx">@@ -15,7 +15,8 @@ resource "aws_security_group" "ingress" &#123;</div>
                                <div className="diff-ln-del">-  cidr_blocks = ["0.0.0.0/0"]</div>
                                <div className="diff-ln-add">+  cidr_blocks = [var.vpc_private_subnet_cidr]</div>
                                <div className="diff-ln-ctx">   from_port   = 5432</div>
                                <div className="diff-ln-ctx">@@ -32,3 +33,4 @@ resource "aws_db_instance" "postgres" &#123;</div>
                                <div className="diff-ln-del">-  storage_encrypted = false</div>
                                <div className="diff-ln-add">+  storage_encrypted = true</div>
                                <div className="diff-ln-add">+  kms_key_id        = aws_kms_key.db_key.arn</div>
                              </div>
                            </div>
                            <div className="console-status-strip ok">
                              <span className="status-symbol">✓</span>
                              <span>RESOURCE-LEVEL DIFF READY FOR SANDBOX VALIDATION</span>
                            </div>
                          </div>
                        )}

                        {/* STAGE 06: LOCALSTACK SANDBOX VALIDATION CONSOLE */}
                        {current.visualType === 'sandbox' && (
                          <div className="terminal-console-view">
                            <div className="console-command-row">
                              <span className="console-prompt">$</span> agentshield validate --harness=localstack --linters=all
                            </div>
                            <div className="console-output-box">
                              <div className="validation-harness-console">
                                <div className="harness-live-header">
                                  <span>VALIDATION HARNESS</span>
                                  <span className="harness-tag">LIVE</span>
                                </div>
                                <div className="harness-item-row">
                                  <span className="h-dot pass">●</span>
                                  <span className="h-cmd">terraform validate</span>
                                  <span className="h-status pass">PASS</span>
                                </div>
                                <div className="harness-item-row">
                                  <span className="h-dot pass">●</span>
                                  <span className="h-cmd">tflint / cfn-lint</span>
                                  <span className="h-status pass">PASS</span>
                                </div>
                                <div className="harness-item-row">
                                  <span className="h-dot pass">●</span>
                                  <span className="h-cmd">LocalStack dry-run</span>
                                  <span className="h-status pass">PASS</span>
                                </div>
                                <div className="harness-divider" />
                                <div className="harness-final-row">
                                  <span className="final-label">PATCH STATUS</span>
                                  <span className="final-val">VERIFIED</span>
                                </div>
                              </div>
                            </div>
                            <div className="console-status-strip ok">
                              <span className="status-symbol">✓</span>
                              <span>100% PATCH SYNTAX VALIDITY • ZERO RUNTIME BREAKAGES</span>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
