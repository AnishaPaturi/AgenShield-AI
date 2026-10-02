import { motion, useReducedMotion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  ShieldAlert,
  Network,
  Lock,
  ArrowRight,
  Database,
  Flame,
  CheckCircle2,
  Sliders,
  Sparkles,
} from 'lucide-react'

export default function SecurityPreview() {
  const prefersReduced = useReducedMotion()

  const securityPillars = [
    {
      title: 'Attack-Path Discovery',
      category: 'Contextual Topology',
      icon: Network,
      tag: 'BFS Exploit Route Discovery',
      desc: 'Constructs resource dependency graphs from IaC. Traces exploit paths from perimeter ingress to high-value internal databases and privileged IAM roles.',
      metric: 'Automated Choke Point Detection',
    },
    {
      title: 'Zero-Leakage Safeguards',
      category: 'Credential Protection',
      icon: Lock,
      tag: 'Gitleaks + Shannon Entropy',
      desc: 'Intercepts exposed API keys, private certificates, and AWS tokens, cryptographically masking them locally prior to any model ingestion.',
      metric: '0 Credentials Sent to LLMs',
    },
    {
      title: 'Composite Risk Scoring',
      category: 'Triage Intelligence',
      icon: Sliders,
      tag: 'Mathematical Formula',
      desc: 'Calculates unified risk scores (0–100) combining base severity (50%), topological exposure (30%), and blast radius (20%) calibrated by consensus confidence.',
      metric: 'Priority = (0.5S + 0.3E + 0.2B)',
    },
  ]

  const attackPathNodes = [
    { label: 'Internet Ingress', sub: '0.0.0.0/0', type: 'source' },
    { label: 'Internet Gateway', sub: 'igw-089a', type: 'network' },
    { label: 'Security Group', sub: 'Port 5432 Ingress', type: 'choke' },
    { label: 'RDS PostgreSQL', sub: 'prod-customers', type: 'target' },
    { label: 'IAM Backup Role', sub: 'AdministratorAccess', type: 'cascade' },
  ]

  return (
    <section className="preview-section" id="security-preview" aria-label="Security Intelligence Overview">
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
              CONTEXTUAL TOPOLOGY INTELLIGENCE
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            SECURITY THAT UNDERSTANDS
            <br />
            <span className="heading-gradient">EXPLOIT CONTEXT.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            A misconfiguration in isolation is just noise. AgentShield analyzes infrastructure
            relationships, permissions, attack paths, and blast radius to reveal what an attacker can
            actually reach.
          </motion.p>
        </div>

        {/* Security Showcase Card */}
        <motion.div
          className="preview-showcase-card"
          initial={{ opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.25 }}
        >
          {/* Visual Attack Path Breadcrumb Strip */}
          <div className="preview-attackpath-strip">
            <div className="preview-attackpath-header">
              <span className="preview-pipeline-label">REPRESENTATIVE ATTACK VECTOR GRAPH</span>
              <span className="preview-chokepoint-badge">
                <ShieldAlert size={12} />
                Choke Point: aws_security_group.ingress (Port 5432)
              </span>
            </div>

            <div className="preview-path-nodes">
              {attackPathNodes.map((node, idx) => (
                <div key={node.label} className="preview-path-node-wrap">
                  <div className={`preview-path-node node-${node.type}`}>
                    <span className="path-node-label">{node.label}</span>
                    <span className="path-node-sub">{node.sub}</span>
                  </div>
                  {idx < attackPathNodes.length - 1 && (
                    <div className="preview-path-connector">
                      <span className="connector-line" />
                      <span className="connector-arrow">▶</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Core Security Pillars 3-Column Grid */}
          <div className="preview-pillars-grid">
            {securityPillars.map((pillar) => {
              const IconComponent = pillar.icon
              return (
                <div key={pillar.title} className="preview-pillar-item">
                  <div className="preview-pillar-header">
                    <div className="preview-pillar-icon-box security-icon-box">
                      <IconComponent size={18} />
                    </div>
                    <span className="preview-pillar-tag">{pillar.tag}</span>
                  </div>
                  <span className="preview-pillar-step">{pillar.category}</span>
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
                Live Cloud Drift Detection &amp; Compliance Mappings (CIS, NIST, SOC 2, PCI-DSS)
              </span>
              <p className="preview-footer-note">
                Examine interactive multi-hop attack graphs, blast radius calculations, and cloud drift auditing on our dedicated security page.
              </p>
            </div>

            <div className="preview-footer-actions">
              <Link to="/security" className="preview-cta-btn preview-cta-primary">
                <span>Explore Security Intelligence</span>
                <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
