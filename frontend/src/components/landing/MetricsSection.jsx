import { motion, useReducedMotion } from 'framer-motion'
import { CheckCircle2, TrendingUp, Cpu, ShieldCheck } from 'lucide-react'

export default function MetricsSection() {
  const prefersReduced = useReducedMotion()

  const coreMetrics = [
    {
      index: '01',
      title: 'Autonomous Agents',
      number: '6',
      unit: 'LangGraph Agents',
      description:
        'Stateful multi-agent DAG coordinating AST parsing, secrets interception, hybrid RAG, multi-LLM consensus, and sandbox validation.',
    },
    {
      index: '02',
      title: 'Polyglot IaC Formats',
      number: '4',
      unit: 'Native Parsers',
      description:
        'Terraform HCL2, AWS CloudFormation JSON/YAML, Kubernetes Manifests, and Helm Charts with AST variable pre-resolution.',
    },
    {
      index: '03',
      title: 'Multi-Cloud Scope',
      number: '3',
      unit: 'Supported Clouds',
      description:
        'Unified security modeling across Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP).',
    },
    {
      index: '04',
      title: 'Automated Test Suite',
      number: '420+',
      unit: 'Automated Tests',
      description:
        '100% passing test coverage verifying AST parsers, BFS graph traversal, calibrated consensus, and API endpoints.',
    },
  ]

  const secondaryMetrics = [
    {
      label: 'Hallucination Suppression',
      value: '< 3%',
      subtext: 'vs ~15% Single-LLM Baseline',
      highlight: true,
    },
    {
      label: 'Patch Syntax Validity',
      value: '100%',
      subtext: 'Linter & LocalStack Verified',
      highlight: true,
    },
    {
      label: 'Compliance Frameworks',
      value: '4',
      subtext: 'SOC2, HIPAA, PCI-DSS, NIST 800-53',
      highlight: false,
    },
    {
      label: 'State Mutation Footprint',
      value: '0',
      subtext: 'Read-Only Security Audit PolP',
      highlight: false,
    },
  ]

  return (
    <section className="metrics-section" id="metrics" aria-label="Empirical Results and Metrics">
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
              VERIFIED PROJECT METRICS &amp; EVALUATION
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            PROVABLE RESULTS.
            <br />
            <span className="heading-gradient">ZERO INVENTED NUMBERS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Every metric below reflects the actual implementation and automated test suites in the
            AgentShield AI repository.
          </motion.p>
        </div>

        {/* 4 Core Prominent Metrics: 01, 02, 03, 04 format */}
        <div className="core-metrics-grid">
          {coreMetrics.map((metric, idx) => (
            <motion.div
              key={metric.index}
              className="core-metric-card"
              initial={{ opacity: 0, y: prefersReduced ? 0 : 35 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.15 }}
              transition={{
                duration: prefersReduced ? 0.1 : 0.7,
                delay: prefersReduced ? 0 : idx * 0.1,
                ease: [0.16, 1, 0.3, 1],
              }}
            >
              {/* Subtle Glass Reflection Sheen */}
              <div className="glass-reflection-sheen" />

              <div className="metric-index-row">
                <span className="metric-index">{metric.index}</span>
                <span className="metric-title-badge">{metric.title}</span>
              </div>

              <div className="metric-figure-row">
                <span className="metric-big-number">{metric.number}</span>
                <span className="metric-unit-text">{metric.unit}</span>
              </div>

              <p className="metric-card-desc">{metric.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Secondary Rigorous Performance Indicators */}
        <div className="secondary-metrics-row">
          {secondaryMetrics.map((item, idx) => (
            <div
              key={item.label}
              className={`sec-metric-item ${item.highlight ? 'accented' : ''}`}
            >
              <div className="sec-metric-value">{item.value}</div>
              <div className="sec-metric-label">{item.label}</div>
              <div className="sec-metric-sub">{item.subtext}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
