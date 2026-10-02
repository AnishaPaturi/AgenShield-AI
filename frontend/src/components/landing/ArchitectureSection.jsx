import { useState, useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  Layers,
  Cpu,
  Network,
  Database,
  ShieldCheck,
  GitBranch,
  Terminal,
  Activity,
  ArrowDown,
  ArrowRight,
  Server,
  Lock,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function ArchitectureSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)

  // Architectural phases driven by scroll progress:
  // Phase 1 (>= 0.15): Ingestion mounted
  // Phase 2 (>= 0.35): LangGraph Orchestrator active
  // Phase 3 (>= 0.55): Multi-LLM & Topological Engines connected
  // Phase 4 (>= 0.75): Sandbox & Verification harnessed
  // Phase 5 (>= 0.85): Final decision emerges
  const p1 = progress >= 0.12 || prefersReduced
  const p2 = progress >= 0.32 || prefersReduced
  const p3 = progress >= 0.52 || prefersReduced
  const p4 = progress >= 0.72 || prefersReduced
  const p5 = progress >= 0.84 || prefersReduced

  return (
    <section
      ref={sectionRef}
      className="architecture-section cinematic-scene-stage"
      id="architecture"
      aria-label="AgentShield AI System Architecture"
    >
      <div className="section-container">
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
              SYSTEM ARCHITECTURE SCHEMATIC
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            A STATEFUL MULTI-AGENT
            <br />
            <span className="heading-gradient">DEFENSE MATRIX.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            As you scroll through the architecture, observe how the system dynamically constructs
            from polyglot ingestion through the LangGraph state machine to sandbox-validated decisions.
          </motion.p>

          {/* Architecture Scroll Stage Breadcrumb */}
          <div className="arch-stage-bar">
            <span className={`arch-stage-pill ${p1 ? 'active' : ''}`}>1. INGESTION</span>
            <span className="arch-stage-arrow">→</span>
            <span className={`arch-stage-pill ${p2 ? 'active' : ''}`}>2. ORCHESTRATION</span>
            <span className="arch-stage-arrow">→</span>
            <span className={`arch-stage-pill ${p3 ? 'active' : ''}`}>3. DUAL ENGINES</span>
            <span className="arch-stage-arrow">→</span>
            <span className={`arch-stage-pill ${p4 ? 'active' : ''}`}>4. SANDBOX HARNESS</span>
            <span className="arch-stage-arrow">→</span>
            <span className={`arch-stage-pill ${p5 ? 'active' : ''}`}>5. DECISION EMERGENCE</span>
          </div>
        </div>

        {/* Blueprint Visual Diagram Grid */}
        <div className="architecture-blueprint-canvas">
          {/* Layer 1: Polyglot Ingestion Layer */}
          <div
            className={`blueprint-layer ${p1 ? 'layer-activated' : 'layer-dormant'}`}
            style={{ transition: 'all 0.5s ease' }}
          >
            <div className="layer-header">
              <span className="layer-number">LAYER 01</span>
              <span className="layer-title">Polyglot IaC Ingestion & Normalization</span>
              <span className="layer-status">{p1 ? 'MOUNTED' : 'AWAITING SCROLL'}</span>
            </div>
            <div className="layer-cards-row">
              <div className="blueprint-node">
                <span className="node-badge">HCL2</span>
                <h4>Terraform Parser</h4>
                <p>Unfolds dynamic locals & variable blocks</p>
              </div>
              <div className="blueprint-node">
                <span className="node-badge">CFN</span>
                <h4>CloudFormation</h4>
                <p>Resolves Ref, Fn::GetAtt & intrinsic stacks</p>
              </div>
              <div className="blueprint-node">
                <span className="node-badge">K8S</span>
                <h4>Kubernetes YAML</h4>
                <p>Parses PodSecurity standards & RBAC roles</p>
              </div>
              <div className="blueprint-node">
                <span className="node-badge">HELM</span>
                <h4>Helm Chart Engine</h4>
                <p>Renders templates & dynamic overlay values</p>
              </div>
            </div>
          </div>

          {/* Conduit Connector 1 -> 2 */}
          <div className="blueprint-vertical-conduit">
            <div className={`conduit-stream ${p2 ? 'stream-active' : ''}`} />
          </div>

          {/* Layer 2: LangGraph Orchestrator & State Blackboard */}
          <div
            className={`blueprint-layer core-orchestrator ${p2 ? 'layer-activated' : 'layer-dormant'}`}
            style={{ transition: 'all 0.5s ease 0.1s' }}
          >
            <div className="layer-header">
              <span className="layer-number">LAYER 02</span>
              <span className="layer-title">LangGraph Orchestration Bus & Shared State</span>
              <span className="layer-status">{p2 ? 'DAG ACTIVE' : 'DORMANT'}</span>
            </div>
            <div className="orchestrator-core-box">
              <div className="core-hub-inner">
                <Cpu size={24} className="core-hub-icon" />
                <div className="core-hub-meta">
                  <h4>Stateful Multi-Agent Directed Acyclic Graph</h4>
                  <p>
                    Deterministic state routing: `ast_parsed` → `secrets_checked` → `rag_retrieved`
                    → `consensus_voted` → `path_prioritized` → `sandbox_validated`
                  </p>
                </div>
              </div>
              <div className="core-blackboard-tags">
                <span className="bb-tag">Zero Memory Leaks</span>
                <span className="bb-tag">Audit Trail Persistence</span>
                <span className="bb-tag">State Rollback Safeguards</span>
              </div>
            </div>
          </div>

          {/* Conduit Connector 2 -> 3 */}
          <div className="blueprint-vertical-conduit">
            <div className={`conduit-stream ${p3 ? 'stream-active' : ''}`} />
          </div>

          {/* Layer 3: Dual Reasoning & Topological Engines */}
          <div
            className={`blueprint-layer ${p3 ? 'layer-activated' : 'layer-dormant'}`}
            style={{ transition: 'all 0.5s ease 0.2s' }}
          >
            <div className="layer-header">
              <span className="layer-number">LAYER 03</span>
              <span className="layer-title">Parallel Cognitive & Topological Engines</span>
              <span className="layer-status">{p3 ? 'ENGINES RUNNING' : 'STANDBY'}</span>
            </div>
            <div className="layer-cards-row dual-engines-row">
              <div className="blueprint-node engine-card">
                <div className="engine-card-header">
                  <Database size={18} className="engine-icon" />
                  <h4>Hybrid Vector RAG (Qdrant)</h4>
                </div>
                <p>Dense + Sparse keyword index indexing CIS, NIST 800-53, SOC2, and MITRE controls.</p>
                <span className="engine-metric">&lt;45ms semantic query latency</span>
              </div>

              <div className="blueprint-node engine-card">
                <div className="engine-card-header">
                  <Cpu size={18} className="engine-icon" />
                  <h4>Multi-LLM Ensemble Voting</h4>
                </div>
                <p>Claude 3.5 Sonnet + GPT-4o parallel voting with Platt logit temperature scaling.</p>
                <span className="engine-metric">&lt;3% hallucination rate</span>
              </div>

              <div className="blueprint-node engine-card">
                <div className="engine-card-header">
                  <Network size={18} className="engine-icon" />
                  <h4>BFS Topological Graph Engine</h4>
                </div>
                <p>Traces exploit propagation from Internet Gateways to Crown-Jewel Databases.</p>
                <span className="engine-metric">Automated choke-point isolation</span>
              </div>
            </div>
          </div>

          {/* Conduit Connector 3 -> 4 */}
          <div className="blueprint-vertical-conduit">
            <div className={`conduit-stream ${p4 ? 'stream-active' : ''}`} />
          </div>

          {/* Layer 4 & 5: Sandbox Verification & Autonomous Decision */}
          <div
            className={`blueprint-layer decision-layer ${p4 ? 'layer-activated' : 'layer-dormant'}`}
            style={{ transition: 'all 0.5s ease 0.3s' }}
          >
            <div className="layer-header">
              <span className="layer-number">LAYER 04 & 05</span>
              <span className="layer-title">LocalStack Sandbox & Decision Emergence</span>
              <span className="layer-status">{p5 ? 'DECISION LOCKED' : p4 ? 'SANDBOX ACTIVE' : 'PENDING'}</span>
            </div>

            <div className="decision-flow-grid">
              <div className="decision-step-card">
                <Terminal size={20} className="step-icon" />
                <h4>LocalStack Container</h4>
                <p>Executes terraform validate & dry-run plan in isolated Docker sandbox.</p>
                <div className="step-badge success">100% Syntax Verified</div>
              </div>

              <div className="decision-step-card">
                <GitBranch size={20} className="step-icon" />
                <h4>Automated Pull Request</h4>
                <p>Generates cryptographic signed Git commit with unified remediation diff.</p>
                <div className="step-badge info">Zero Prod Regression</div>
              </div>

              <div className={`decision-outcome-box ${p5 ? 'outcome-visible' : ''}`}>
                <div className="outcome-header">
                  <ShieldCheck size={22} className="outcome-icon" />
                  <h4>Autonomous Decision Gate</h4>
                </div>
                <div className="outcome-metrics-line">
                  <span>Confidence: C = 0.964</span>
                  <span className="sep">•</span>
                  <span>Threshold: 0.850</span>
                </div>
                <div className="outcome-verdict">
                  <span className="verdict-tag approved">AUTO-PATCH AUTHORIZED</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
