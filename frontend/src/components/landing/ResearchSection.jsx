import { motion, useReducedMotion } from 'framer-motion'
import {
  BookOpen,
  FileText,
  Award,
  Layers,
  ArrowUpRight,
  ExternalLink,
  Code2,
  CheckCircle,
  Binary,
} from 'lucide-react'
import GithubIcon from './GithubIcon'

export default function ResearchSection() {
  const prefersReduced = useReducedMotion()

  const researchArtifacts = [
    {
      title: 'Base Research Paper Analysis',
      citation: 'Toprani, D., & Madisetti, V. K. (2025). IEEE Access, Vol. 13, pp. 69175-69181.',
      icon: BookOpen,
      badge: 'IEEE ACCESS 2025',
      summary:
        'Analyzed the foundational 3-agent linear CloudFormation pipeline. Identified key architectural bottlenecks: ~15% single-LLM hallucination rate, lack of auto-patch diff execution, and absence of sandbox validation.',
      advancements: [
        'Expanded from 3 linear agents to 8 stateful LangGraph agents',
        'Added multi-cloud scope: Terraform, K8s, Helm & Azure/GCP',
        'Implemented Platt-calibrated ensemble consensus',
      ],
      linkText: 'Referenced in Repository',
      href: 'https://github.com/AnishaPaturi/AgenShield-AI#readme',
    },
    {
      title: 'AgentShield AI Camera-Ready Publication',
      citation: 'Autonomous Multi-Agent Framework for Multi-Cloud IaC Security (Springer CCIS / IEEE Format)',
      icon: FileText,
      badge: 'PEER-REVIEW SPEC',
      summary:
        'Formal publication draft detailing the mathematical consensus calibration formula, BFS attack-path traversal algorithms, and empirical benchmark evaluations on Terragoat and cfngoat.',
      advancements: [
        'Mathematically bounded hallucination threshold (<3%)',
        'LocalStack containerized dry-run sandbox harness',
        'Topological choke-point mitigation analysis',
      ],
      linkText: 'View Paper Specification',
      href: 'https://github.com/AnishaPaturi/AgenShield-AI/tree/main/docs/paper',
    },
    {
      title: 'Polyglot Literature Survey & Taxonomy',
      citation: 'literature_survey.txt — 4 Paradigms across Static, CSPM, ML & LLM Agentic Architectures',
      icon: Layers,
      badge: 'LITERATURE SURVEY',
      summary:
        'Comprehensive survey establishing the comparative matrix against static scanners (Checkov, KICS), dynamic CSPM (AWS Config), ML smell detectors (GLITCH), and early LLMs (GenKubeSec).',
      advancements: [
        'Shift-Left + Live Drift continuous detection model',
        'Dynamic few-shot prompt adaptation from developer feedback',
        'Zero-leakage local cryptographic secrets redaction',
      ],
      linkText: 'Read Architecture Specs',
      href: 'https://github.com/AnishaPaturi/AgenShield-AI/blob/main/about.md',
    },
  ]

  const engineeringMetrics = [
    { label: 'Automated Test Suite', value: '230+ Unit & Integration Tests', sub: 'Pytest 100% Pass Rate' },
    { label: 'Orchestration Engine', value: 'LangGraph Non-Linear DAG', sub: 'Stateful Checkpointed Graph' },
    { label: 'Open-Source License', value: 'MIT Open Source', sub: 'Reproducible Research' },
    { label: 'Mathematical Calibration', value: 'Platt Temperature Scaling', sub: 'ECE & Brier Score Validation' },
  ]

  return (
    <section className="research-section" id="research" aria-label="Research and Engineering Credibility">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-block text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              PEER-REVIEWED SCIENTIFIC RIGOR
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            RESEARCH &amp;
            <br />
            <span className="heading-gradient">ENGINEERING FOUNDATIONS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            AgentShield AI is not a generic wrapper or conceptual dashboard. It is an empirically
            evaluated multi-agent cybersecurity framework designed as an architectural advancement
            over published IEEE literature.
          </motion.p>
        </div>

        {/* Research Artifact Cards Grid */}
        <div className="research-cards-grid">
          {researchArtifacts.map((artifact, idx) => {
            const Icon = artifact.icon
            return (
              <motion.div
                key={artifact.title}
                className="research-card"
                initial={{ opacity: 0, y: prefersReduced ? 0 : 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: prefersReduced ? 0.1 : 0.7,
                  delay: prefersReduced ? 0 : idx * 0.12,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                {/* Subtle Glass Reflection Sheen */}
                <div className="glass-reflection-sheen" />

                <div className="research-card-header">
                  <div className="research-badge-row">
                    <span className="research-tag">{artifact.badge}</span>
                  </div>
                  <h3 className="research-card-title">{artifact.title}</h3>
                  <div className="research-citation">{artifact.citation}</div>
                </div>

                <p className="research-card-summary">{artifact.summary}</p>

                <div className="research-advancements-block">
                  <span className="advancements-heading">Key Scientific Contributions:</span>
                  <ul className="advancements-list">
                    {artifact.advancements.map((adv) => (
                      <li key={adv} className="advancement-item">
                        <CheckCircle size={14} className="adv-check" />
                        <span>{adv}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="research-card-footer">
                  <a
                    href={artifact.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="research-link"
                  >
                    <span>{artifact.linkText}</span>
                    <ArrowUpRight size={14} className="link-arrow" />
                  </a>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Engineering Rigor Telemetry Strip */}
        <motion.div
          className="engineering-telemetry-strip"
          initial={{ opacity: 0, y: prefersReduced ? 0 : 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3 }}
        >
          <div className="telemetry-inner-grid">
            {engineeringMetrics.map((m) => (
              <div key={m.label} className="telemetry-stat-card">
                <span className="telemetry-stat-label">{m.label}</span>
                <span className="telemetry-stat-val">{m.value}</span>
                <span className="telemetry-stat-sub">{m.sub}</span>
              </div>
            ))}
          </div>

          <div className="github-credibility-bar">
            <div className="github-info-left">
              <GithubIcon size={18} className="gh-icon" />
              <span className="gh-repo-name">AnishaPaturi / AgenShield-AI</span>
              <span className="gh-badge">Python 3.12+ • LangGraph • FastAPI</span>
            </div>
            <a
              href="https://github.com/AnishaPaturi/AgenShield-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="github-inspect-btn"
            >
              <span>Inspect Source Repository</span>
              <ExternalLink size={13} />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
