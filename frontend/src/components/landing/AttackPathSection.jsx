import { useState, useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  Network,
  ShieldAlert,
  Flame,
  ArrowRight,
  Database,
  Cloud,
  Lock,
  Key,
  Server,
  Crosshair,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function AttackPathSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)
  const [activeVector, setActiveVector] = useState(0)

  // Scroll phase calculation:
  // Step 1: Resource graph discovered (>= 0.12)
  // Step 2: Vulnerabilities flagged (>= 0.32)
  // Step 3: Attack Path traverses graph (>= 0.52)
  // Step 4: Blast Radius expands (>= 0.72)
  // Step 5: Prioritization calculated (>= 0.86)
  const isResourceVisible = progress >= 0.1 || prefersReduced
  const isVulnFlagged = progress >= 0.3 || prefersReduced
  const isPathTraversed = progress >= 0.5 || prefersReduced
  const isBlastExpanded = progress >= 0.7 || prefersReduced
  const isPrioritized = progress >= 0.84 || prefersReduced

  const vectors = [
    {
      id: 'vector-rds',
      name: 'Ingress to Production RDS Database',
      cve: 'CKV_AWS_20 + AS-AWS-001',
      severity: 'CRITICAL',
      score: '96.4 / 100',
      chokePoint: 'aws_security_group.sg_public_db (Port 5432)',
      hops: [
        { id: 'h1', title: 'Internet Ingress', asset: '0.0.0.0/0', type: 'ingress', icon: Cloud },
        { id: 'h2', title: 'Internet Gateway', asset: 'igw-089a', type: 'network', icon: Network },
        { id: 'h3', title: 'Public Security Group', asset: 'sg-public-db : 5432', type: 'vuln', icon: ShieldAlert },
        { id: 'h4', title: 'Amazon RDS DB', asset: 'prod-customers (PII)', type: 'crown', icon: Database },
        { id: 'h5', title: 'IAM AssumeRole', asset: 'AdministratorAccess', type: 'cascade', icon: Key },
      ],
      blastCount: 7,
      blastServices: ['RDS PostgreSQL', 'S3 Data Lake', 'EC2 Worker Nodes', 'IAM Root Credential', 'KMS Keyring', 'Lambda Triggers', 'CloudWatch Audit Logs'],
    },
    {
      id: 'vector-s3',
      name: 'Public S3 Bucket to Cloud Admin Takeover',
      cve: 'CKV_AWS_54 + AS-IAM-003',
      severity: 'CRITICAL',
      score: '92.8 / 100',
      chokePoint: 'aws_s3_bucket_policy.corp_analytics',
      hops: [
        { id: 'h1', title: 'Public Web Scanner', asset: 'Anonymous Actor', type: 'ingress', icon: Cloud },
        { id: 'h2', title: 'S3 Data Lake Bucket', asset: 'corp-analytics (Public Read)', type: 'vuln', icon: ShieldAlert },
        { id: 'h3', title: 'Embedded Bootstrap', asset: 'deploy_worker.sh', type: 'vuln', icon: Server },
        { id: 'h4', title: 'IAM Instance Profile', asset: 'ec2-cluster-admin-role', type: 'crown', icon: Key },
        { id: 'h5', title: 'Full Cloud Estate', asset: 'Multi-Account Access', type: 'cascade', icon: Lock },
      ],
      blastCount: 9,
      blastServices: ['S3 Analytics Bucket', 'EC2 AutoScale Pool', 'EKS Cluster Control', 'IAM Organization Roles', 'Secrets Manager', 'DynamoDB Billing', 'Route53 Hosted Zones', 'CloudFront CDN', 'SNS Alerts'],
    },
  ]

  const current = vectors[activeVector]

  return (
    <section
      ref={sectionRef}
      className="attack-path-section cinematic-scene-stage"
      id="attack-path"
      aria-label="Attack Path and Blast Radius Intelligence"
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
              TOPOLOGICAL EXPLOIT GRAPH TRAVERSAL
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            TOPOLOGICAL ATTACK PATHS.
            <br />
            <span className="heading-gradient">RADIAL BLAST RADIUS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Scroll to watch the exploit traversal engine trace how an external attacker traverses
            from perimeter gateways through misconfigured security groups directly into internal
            databases and admin roles.
          </motion.p>

          {/* 5-Phase Breadcrumb Bar */}
          <div className="attack-path-progress-bar">
            <span className={`path-step-pill ${isResourceVisible ? 'active' : ''}`}>1. RESOURCE</span>
            <span className="path-step-arrow">→</span>
            <span className={`path-step-pill ${isVulnFlagged ? 'active' : ''}`}>2. VULNERABILITY</span>
            <span className="path-step-arrow">→</span>
            <span className={`path-step-pill ${isPathTraversed ? 'active' : ''}`}>3. ATTACK PATH</span>
            <span className="path-step-arrow">→</span>
            <span className={`path-step-pill ${isBlastExpanded ? 'active' : ''}`}>4. BLAST RADIUS</span>
            <span className="path-step-arrow">→</span>
            <span className={`path-step-pill ${isPrioritized ? 'active' : ''}`}>5. PRIORITIZATION</span>
          </div>
        </div>

        {/* Vector Toggle Buttons */}
        <div className="attack-vector-buttons">
          {vectors.map((vec, idx) => (
            <button
              key={vec.id}
              type="button"
              onClick={() => setActiveVector(idx)}
              className={`vector-toggle-btn ${activeVector === idx ? 'active' : ''}`}
            >
              <Crosshair size={14} className="vector-btn-icon" />
              <span>{vec.name}</span>
            </button>
          ))}
        </div>

        {/* Unique Attack Graph Stage */}
        <div className="attack-path-visual-stage">
          {/* Top Telemetry Header */}
          <div className="attack-stage-meta-strip">
            <div className="meta-left">
              <span className="vector-cve-badge">{current.cve}</span>
              <h3 className="vector-name">{current.name}</h3>
            </div>
            <div className="meta-right">
              <div className="meta-score-box">
                <span className="score-label">COMPOSITE RISK:</span>
                <span className={`score-value ${isPrioritized ? 'revealed' : ''}`}>
                  {isPrioritized ? current.score : 'CALCULATING...'}
                </span>
              </div>
              <div className="meta-choke-box">
                <span className="choke-label">ARCHITECTURAL CHOKE POINT:</span>
                <span className="choke-value">{current.chokePoint}</span>
              </div>
            </div>
          </div>

          {/* Graph Nodes with Laser Conduit */}
          <div className="attack-graph-track">
            {current.hops.map((hop, hIdx) => {
              const HopIcon = hop.icon
              // Node activates based on scroll phase
              const isHopActive =
                isPathTraversed || (hIdx === 0 && isResourceVisible) || (hIdx <= 2 && isVulnFlagged)

              return (
                <div key={hop.id} className="attack-hop-unit">
                  <div
                    className={`attack-hop-node type-${hop.type} ${
                      isHopActive ? 'hop-activated' : 'hop-dormant'
                    }`}
                  >
                    {hop.type === 'vuln' && isVulnFlagged && (
                      <span className="hop-vuln-ping">FLAW DETECTED</span>
                    )}
                    {hop.type === 'crown' && isPathTraversed && (
                      <span className="hop-crown-ping">TARGET ASSET</span>
                    )}

                    <div className="hop-icon-box">
                      <HopIcon size={18} className="hop-icon" />
                    </div>

                    <div className="hop-title">{hop.title}</div>
                    <div className="hop-asset">{hop.asset}</div>
                  </div>

                  {hIdx < current.hops.length - 1 && (
                    <div className="attack-hop-connector">
                      <div
                        className={`attack-laser-track ${
                          isPathTraversed ? 'laser-firing' : ''
                        }`}
                      />
                      <ArrowRight size={14} className="attack-laser-arrow" />
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Blast Radius Section (Reveals during Step 4) */}
          <div
            className={`blast-radius-cascade-panel ${
              isBlastExpanded ? 'blast-revealed' : 'blast-concealed'
            }`}
          >
            <div className="blast-panel-header">
              <Flame size={16} className="blast-panel-flame" />
              <h4>EXPANDED BLAST RADIUS: {current.blastCount} DOWNSTREAM ASSETS THREATENED</h4>
            </div>
            <div className="blast-services-list">
              {current.blastServices.map((srv, sIdx) => (
                <span key={sIdx} className="blast-service-chip">
                  <span className="chip-indicator" />
                  {srv}
                </span>
              ))}
            </div>
            <p className="blast-mitigation-note">
              <strong>Severing the Choke Point:</strong> Remediating <code>{current.chokePoint}</code> eliminates all {current.blastCount} downstream exploit vectors in a single deployment.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
