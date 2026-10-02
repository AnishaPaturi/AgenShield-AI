import { useState } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import {
  ShieldAlert,
  Network,
  Flame,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Database,
  Cloud,
  Lock,
  Layers,
  FileCode,
  Sliders,
} from 'lucide-react'

export default function SecuritySection() {
  const [selectedFindingIndex, setSelectedFindingIndex] = useState(0)
  const prefersReduced = useReducedMotion()

  const findingsScenarios = [
    {
      id: 'rds-path',
      title: 'Perimeter Ingress to Unencrypted RDS PostgreSQL',
      ruleId: 'CKV_AWS_20 + AS-AWS-001',
      severity: 'CRITICAL',
      priorityScore: '96.4 / 100',
      cloud: 'AWS',
      blastRadiusCount: 5,
      chokePoint: 'aws_security_group.ingress (Port 5432)',
      description:
        'A wide-open security group (0.0.0.0/0) on port 5432 exposes an Amazon RDS database storing PII without KMS encryption at rest. Static linters see an open port; AgentShield reveals the complete ingress-to-data exfiltration path.',
      nodes: [
        { id: 'n1', label: 'Internet Ingress', sub: '0.0.0.0/0', type: 'source', status: 'danger' },
        { id: 'n2', label: 'Internet Gateway', sub: 'igw-089a', type: 'network', status: 'danger' },
        { id: 'n3', label: 'Security Group', sub: 'sg-public-db', type: 'choke', status: 'choke' },
        { id: 'n4', label: 'RDS PostgreSQL', sub: 'prod-customers', type: 'target', status: 'target' },
        { id: 'n5', label: 'IAM Backup Role', sub: 'rds-backup-role', type: 'cascade', status: 'cascade' },
      ],
      compliance: ['SOC2 CC6.1', 'NIST 800-53 AC-6', 'PCI-DSS 1.3', 'HIPAA 164.312'],
      staticScannerView: 'Flags "Port 5432 open" as Low/Med alert. No awareness of whether the DB holds production data or connects to IGW.',
      agentShieldView: 'Reconstructs topological dependency path from IGW to unencrypted database, elevates risk to CRITICAL (96.4), and identifies sg-public-db as single choke point.',
    },
    {
      id: 's3-privesc',
      title: 'Public S3 Bucket with IAM AssumeRole Escalation',
      ruleId: 'CKV_AWS_54 + AS-IAM-003',
      severity: 'CRITICAL',
      priorityScore: '92.8 / 100',
      cloud: 'AWS',
      blastRadiusCount: 7,
      chokePoint: 'aws_s3_bucket_policy.lake_policy',
      description:
        'An S3 data lake bucket configured with public read access contains automation scripts with an overly permissive IAM AssumeRole policy allowing full AdministratorAccess.',
      nodes: [
        { id: 'n1', label: 'Public Web', sub: 'Anonymous Actor', type: 'source', status: 'danger' },
        { id: 'n2', label: 'S3 Data Lake', sub: 'corp-analytics', type: 'choke', status: 'choke' },
        { id: 'n3', label: 'Bootstrap Script', sub: 'init_worker.sh', type: 'target', status: 'danger' },
        { id: 'n4', label: 'IAM Instance Profile', sub: 'ec2-worker-role', type: 'cascade', status: 'target' },
        { id: 'n5', label: 'AdministratorAccess', sub: 'Full Cloud Estate', type: 'cascade', status: 'cascade' },
      ],
      compliance: ['SOC2 CC6.3', 'NIST 800-53 IA-2', 'PCI-DSS 7.1', 'CIS AWS 2.1.5'],
      staticScannerView: 'Flags "S3 bucket has public read ACL" as generic warning with equal weight to a dev documentation bucket.',
      agentShieldView: 'Detects that the bucket holds deployment artifacts referencing Admin IAM credentials, assessing blast radius across 7 cloud services.',
    },
    {
      id: 'k8s-daemonset',
      title: 'Kubernetes Privileged DaemonSet with HostPath Volume',
      ruleId: 'K8S_PRIVILEGED + MITRE_T1611',
      severity: 'HIGH',
      priorityScore: '89.1 / 100',
      cloud: 'Kubernetes',
      blastRadiusCount: 4,
      chokePoint: 'daemonset.spec.containers[0].securityContext',
      description:
        'A Kubernetes DaemonSet deployed with privileged: true and a hostPath volume mount (/var/run/docker.sock) grants root container escape capabilities to underlying worker node hosts.',
      nodes: [
        { id: 'n1', label: 'Ingress Controller', sub: 'nginx-ingress', type: 'source', status: 'danger' },
        { id: 'n2', label: 'Worker Pod', sub: 'monitoring-agent', type: 'choke', status: 'choke' },
        { id: 'n3', label: 'HostPath Mount', sub: '/var/run/docker.sock', type: 'target', status: 'target' },
        { id: 'n4', label: 'Node Root Host', sub: 'k8s-worker-pool-01', type: 'cascade', status: 'cascade' },
        { id: 'n5', label: 'Kubelet Credentials', sub: 'ServiceAccount Token', type: 'cascade', status: 'cascade' },
      ],
      compliance: ['CIS K8s 5.2.2', 'NIST 800-53 SC-7', 'OWASP K8s K01', 'PCI-DSS 2.2'],
      staticScannerView: 'Rule warning: "privileged container detected". Misses that hostPath exposes Docker socket allowing container escape.',
      agentShieldView: 'Correlates container privilege with node socket mount, recognizing immediate node takeover vector and generating policy patch.',
    },
  ]

  const current = findingsScenarios[selectedFindingIndex]

  return (
    <section className="security-section" id="security" aria-label="Contextual Security Analysis">
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
              CONTEXTUAL TOPOLOGY INTELLIGENCE
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            SECURITY THAT
            <br />
            <span className="heading-gradient">UNDERSTANDS CONTEXT.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            A misconfiguration in isolation is just noise. AgentShield analyzes infrastructure
            relationships, permissions, attack paths, and blast radius to reveal what an attacker
            can actually reach.
          </motion.p>
        </div>

        {/* 4-Step Visual Security Process: Detection -> Analysis -> Risk identification -> Decision */}
        <div className="security-process-timeline">
          <div className="process-step-item active">
            <span className="step-badge-num">1</span>
            <div className="process-step-text">
              <span className="step-name">DETECTION</span>
              <span className="step-desc">Polyglot IaC AST Parsing</span>
            </div>
          </div>
          <span className="process-step-arrow">→</span>
          <div className="process-step-item active">
            <span className="step-badge-num">2</span>
            <div className="process-step-text">
              <span className="step-name">ANALYSIS</span>
              <span className="step-desc">Hybrid RAG + Multi-LLM</span>
            </div>
          </div>
          <span className="process-step-arrow">→</span>
          <div className="process-step-item active">
            <span className="step-badge-num">3</span>
            <div className="process-step-text">
              <span className="step-name">RISK IDENTIFICATION</span>
              <span className="step-desc">BFS Ingress Attack Paths</span>
            </div>
          </div>
          <span className="process-step-arrow">→</span>
          <div className="process-step-item active">
            <span className="step-badge-num">4</span>
            <div className="process-step-text">
              <span className="step-name">DECISION</span>
              <span className="step-desc">Calibrated Auto-Remediation</span>
            </div>
          </div>
        </div>

        {/* Interactive Scenario Selector Tabs */}
        <div className="security-selector-tabs">
          {findingsScenarios.map((f, idx) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setSelectedFindingIndex(idx)}
              className={`security-tab-pill ${selectedFindingIndex === idx ? 'active' : ''}`}
            >
              <div className="tab-pill-header">
                <span className="tab-pill-severity">{f.severity}</span>
                <span className="tab-pill-cloud">{f.cloud}</span>
              </div>
              <span className="tab-pill-title">{f.title}</span>
            </button>
          ))}
        </div>

        {/* Large Interactive Visual Canvas */}
        <div className="security-interactive-stage">
          {/* Subtle Glass Reflection Sheen */}
          <div className="glass-reflection-sheen" />

          {/* Top Bar: Finding Title & Telemetry */}
          <div className="security-stage-header">
            <div className="stage-title-group">
              <div className="finding-pulse-beacon" />
              <div>
                <h3 className="stage-scenario-title">{current.title}</h3>
                <span className="stage-rule-id">{current.ruleId}</span>
              </div>
            </div>

            <div className="stage-meta-badges">
              <div className="meta-badge-box">
                <span className="badge-k">PRIORITY SCORE</span>
                <span className="badge-v critical">{current.priorityScore}</span>
              </div>
              <div className="meta-badge-box">
                <span className="badge-k">BLAST RADIUS</span>
                <span className="badge-v">{current.blastRadiusCount} Cloud Resources</span>
              </div>
            </div>
          </div>

          {/* Interactive Topology Graph Visualizer */}
          <div className="security-graph-canvas">
            <div className="graph-ambient-glow" />

            {/* Topology Flow Nodes */}
            <div className="topology-nodes-track">
              {current.nodes.map((node, nIdx) => (
                <div key={node.id} className="topology-node-cell">
                  <div
                    className={`topology-node-card status-${node.status} ${
                      node.type === 'choke' ? 'is-choke-point' : ''
                    }`}
                  >
                    {node.type === 'choke' && (
                      <div className="choke-indicator-label">
                        <span>ARCHITECTURAL CHOKE POINT</span>
                      </div>
                    )}
                    <div className="node-icon-header">
                      {node.type === 'source' && <Cloud size={16} />}
                      {node.type === 'network' && <Network size={16} />}
                      {node.type === 'choke' && <ShieldAlert size={16} />}
                      {node.type === 'target' && <Database size={16} />}
                      {node.type === 'cascade' && <Lock size={16} />}
                      <span className="node-type-label">{node.type.toUpperCase()}</span>
                    </div>

                    <div className="node-card-name">{node.label}</div>
                    <div className="node-card-sub">{node.sub}</div>

                    <div className="node-pulse-halo" />
                  </div>

                  {nIdx < current.nodes.length - 1 && (
                    <div className="topology-connector-arm">
                      <div className="connector-laser-line" />
                      <div className="connector-laser-pulse" />
                      <ArrowRight size={14} className="connector-tip" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Blast Radius Halo Expansion Callout */}
            <div className="blast-radius-perimeter-callout">
              <div className="blast-perimeter-border" />
              <div className="blast-perimeter-tag">
                <Flame size={13} className="flame-icon" />
                <span>EXPANDED BLAST RADIUS CONTOUR: {current.blastRadiusCount} DEPENDENT SERVICES COMPROMISED</span>
              </div>
            </div>
          </div>

          {/* Bottom Diagnostic Columns: Isolated Scanner vs AgentShield */}
          <div className="security-comparison-matrix">
            <div className="comparison-col traditional">
              <div className="comparison-col-header">
                <AlertTriangle size={16} className="comp-icon warning" />
                <span>TRADITIONAL ISOLATED SCANNER</span>
              </div>
              <p className="comparison-col-body">{current.staticScannerView}</p>
              <div className="comparison-col-footer">
                <span className="comp-tag bad">High Alert Fatigue • No Topology</span>
              </div>
            </div>

            <div className="comparison-col agentshield">
              <div className="comparison-col-header">
                <CheckCircle2 size={16} className="comp-icon success" />
                <span>AGENTSHIELD CONTEXTUAL INTELLIGENCE</span>
              </div>
              <p className="comparison-col-body">{current.agentShieldView}</p>
              <div className="comparison-col-footer">
                <span className="comp-tag good">Choke Point Severing • Automated Patch</span>
              </div>
            </div>
          </div>

          {/* Regulatory Compliance Controls Crosswalk */}
          <div className="security-compliance-footer">
            <span className="comp-strip-label">MAPPED COMPLIANCE CONTROLS:</span>
            <div className="comp-strip-badges">
              {current.compliance.map((c) => (
                <span key={c} className="compliance-control-pill">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
