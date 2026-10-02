import { useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { Shield, Cpu, Network, CheckCircle2, GitPullRequest, ArrowRight, Layers, Lock } from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function ProjectIntro() {
  const containerRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(containerRef)

  const pillars = [
    {
      id: 'pillar-ast',
      title: 'Polyglot IaC AST Parsing',
      badge: 'FOUNDATION',
      icon: Layers,
      description:
        'Normalizes Terraform (HCL2), AWS CloudFormation, Kubernetes YAML, and Helm into unified Abstract Syntax Trees, pre-evaluating dynamic variables and locals.',
    },
    {
      id: 'pillar-graph',
      title: 'Topological Attack Paths',
      badge: 'TOPOLOGY',
      icon: Network,
      description:
        'Traces multi-hop exploit paths from internet-facing ingress points to high-value internal databases and privileged IAM credentials using breadth-first search.',
    },
    {
      id: 'pillar-llm',
      title: 'Multi-LLM Ensemble Voting',
      badge: 'CONSENSUS',
      icon: Cpu,
      description:
        'Cross-verifies findings using Anthropic Claude 3.5 Sonnet and OpenAI GPT-4o with Platt-calibrated logit consensus, driving hallucinations below 3%.',
    },
    {
      id: 'pillar-sandbox',
      title: 'Sandbox-Validated Fixes',
      badge: 'REMEDIATION',
      icon: GitPullRequest,
      description:
        'Executes automated dry-run deployments in LocalStack sandboxes before generating clean GitHub Pull Requests with zero production regression risk.',
    },
  ]

  const stats = [
    { label: 'LangGraph Agents', value: '6 DAG Nodes', icon: Cpu },
    { label: 'Supported Clouds', value: 'AWS • Azure • GCP', icon: Shield },
    { label: 'Automated Tests', value: '420+ Passing', icon: CheckCircle2 },
    { label: 'Hallucination Rate', value: '< 3% Empirical', icon: Lock },
  ]

  return (
    <section
      ref={containerRef}
      className="project-intro-section cinematic-scene-stage"
      id="project-intro"
      aria-label="Project Introduction"
    >
      <div className="section-container">
        {/* Eyebrow and Main Heading */}
        <div className="intro-header text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              THE PARADIGM SHIFT IN CLOUD SECURITY
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading intro-heading"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            SECURITY BEYOND
            <br />
            <span className="heading-gradient">CONFIGURATION CHECKS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading intro-subheading"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Traditional static linters flood security teams with thousands of isolated alerts with
            zero context. <strong>AgentShield AI</strong> operates as an autonomous multi-agent
            intelligence engine that parses infrastructure syntax, models entire attack topologies,
            reaches multi-LLM consensus, and validates remediation prior to deployment.
          </motion.p>
        </div>

        {/* 4 Architectural Pillars Grid */}
        <div className="intro-pillars-grid">
          {pillars.map((pillar, idx) => {
            const IconComponent = pillar.icon
            return (
              <motion.div
                key={pillar.id}
                className="intro-pillar-card"
                initial={{ opacity: 0, y: prefersReduced ? 0 : 25 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.15 }}
                transition={{
                  duration: prefersReduced ? 0.1 : 0.6,
                  delay: prefersReduced ? 0 : idx * 0.12,
                }}
              >
                <div className="pillar-header">
                  <div className="pillar-icon-box">
                    <IconComponent size={22} className="pillar-icon" />
                  </div>
                  <span className="pillar-badge">{pillar.badge}</span>
                </div>
                <h3 className="pillar-title">{pillar.title}</h3>
                <p className="pillar-desc">{pillar.description}</p>
                <div className="pillar-accent-line" />
              </motion.div>
            )
          })}
        </div>

        {/* Live Empirical Metrics Strip */}
        <div className="intro-stats-strip">
          {stats.map((stat, idx) => {
            const StatIcon = stat.icon
            return (
              <div key={idx} className="intro-stat-item">
                <StatIcon size={16} className="stat-item-icon" />
                <div className="stat-text-box">
                  <span className="stat-item-value">{stat.value}</span>
                  <span className="stat-item-label">{stat.label}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
