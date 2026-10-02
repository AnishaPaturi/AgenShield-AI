import { motion, useReducedMotion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  Layers,
  ArrowRight,
  FileCode2,
  Radar,
  CheckCircle2,
  Cpu,
  Lock,
  Network,
  Sparkles,
  ExternalLink,
} from 'lucide-react'

export default function ArchitecturePreview() {
  const prefersReduced = useReducedMotion()

  const architecturePillars = [
    {
      step: '01',
      title: 'Polyglot AST Normalization',
      category: 'Static Representation',
      icon: FileCode2,
      tag: 'HCL2 / CFN / K8s / Helm',
      desc: 'Normalizes diverse IaC templates into structured Abstract Syntax Trees. Resolves dynamic variables, locals, and module references before semantic evaluation.',
      metric: '4 Polyglot Frameworks',
    },
    {
      step: '02',
      title: 'Dual-LLM Consensus Engine',
      category: 'Semantic Reasoning',
      icon: Radar,
      tag: 'Claude 3.5 + GPT-4o',
      desc: 'Executes parallel reasoning across dual foundational models with Chain-of-Thought prompting and Platt-calibrated logit scaling to suppress hallucinations.',
      metric: '< 3% Hallucination Rate',
    },
    {
      step: '03',
      title: 'LocalStack Runtime Sandbox',
      category: 'Validation Harness',
      icon: CheckCircle2,
      tag: 'Pre-Deployment Emulation',
      desc: 'Pre-validates synthesized code diffs through static linters followed by containerized dry-run deployment inside LocalStack to guarantee zero deployment regressions.',
      metric: '100% Patch Syntax Validity',
    },
  ]

  const pipelineStages = [
    { num: '01', label: 'IaC Ingestion' },
    { num: '02', label: 'Secrets Shield' },
    { num: '03', label: 'LLM Consensus' },
    { num: '04', label: 'Attack Paths' },
    { num: '05', label: 'Diff Synthesis' },
    { num: '06', label: 'Sandbox Gate' },
  ]

  return (
    <section className="preview-section" id="architecture-preview" aria-label="Platform Architecture Overview">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-block text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              SYSTEM ARCHITECTURE
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            AUTONOMOUS 6-AGENT
            <br />
            <span className="heading-gradient">VERIFICATION ENGINE.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Traditional scanners check isolated lines of code against static regex rules.
            AgentShield AI reconstructs resource topology, intercepts credentials, executes
            multi-LLM consensus, and validates generated patches inside a local runtime sandbox.
          </motion.p>
        </div>

        {/* Interactive Architecture Showcase Card */}
        <motion.div
          className="preview-showcase-card"
          initial={{ opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.25 }}
        >
          {/* Top Mini Pipeline Strip */}
          <div className="preview-pipeline-strip" aria-hidden="true">
            <span className="preview-pipeline-label">VERIFICATION PIPELINE FLOW</span>
            <div className="preview-pipeline-nodes">
              {pipelineStages.map((stage, idx) => (
                <div key={stage.num} className="preview-pipeline-node-wrap">
                  <div className="preview-pipeline-node">
                    <span className="node-num">{stage.num}</span>
                    <span className="node-name">{stage.label}</span>
                  </div>
                  {idx < pipelineStages.length - 1 && <span className="preview-pipeline-arrow">→</span>}
                </div>
              ))}
            </div>
          </div>

          {/* Core Pillars 3-Column Grid */}
          <div className="preview-pillars-grid">
            {architecturePillars.map((pillar) => {
              const IconComponent = pillar.icon
              return (
                <div key={pillar.title} className="preview-pillar-item">
                  <div className="preview-pillar-header">
                    <div className="preview-pillar-icon-box">
                      <IconComponent size={18} />
                    </div>
                    <span className="preview-pillar-tag">{pillar.tag}</span>
                  </div>
                  <span className="preview-pillar-step">STAGE {pillar.step} • {pillar.category}</span>
                  <h3 className="preview-pillar-title">{pillar.title}</h3>
                  <p className="preview-pillar-desc">{pillar.desc}</p>
                  <div className="preview-pillar-metric">
                    <Sparkles size={12} className="metric-sparkle" />
                    <span>{pillar.metric}</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Bottom Action Footer */}
          <div className="preview-card-footer">
            <div className="preview-footer-info">
              <span className="preview-badge-status">
                <span className="preview-status-dot" />
                LangGraph Non-Linear DAG • 6 Autonomous Micro-Agents
              </span>
              <p className="preview-footer-note">
                Deep dive into AST parsing, prompt calibration, and runtime dry-runs on our dedicated architecture page.
              </p>
            </div>

            <div className="preview-footer-actions">
              <Link to="/architecture" className="preview-cta-btn preview-cta-primary">
                <span>Explore Platform Architecture</span>
                <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
