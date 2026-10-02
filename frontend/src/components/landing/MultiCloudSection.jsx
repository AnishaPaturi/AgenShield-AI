import { motion, useReducedMotion } from 'framer-motion'
import {
  Cloud,
  FileCode,
  Shield,
  Layers,
  ArrowRight,
  GitBranch,
  Terminal,
  Server,
  Database,
  CheckCircle,
} from 'lucide-react'

export default function MultiCloudSection() {
  const prefersReduced = useReducedMotion()

  const clouds = [
    {
      name: 'Amazon Web Services',
      tag: 'AWS SDK (boto3)',
      services: ['Amazon S3', 'EC2 Security Groups', 'Amazon RDS', 'IAM Roles'],
      emulation: 'LocalStack Containerized Sandbox',
      color: '#FF9900',
    },
    {
      name: 'Microsoft Azure',
      tag: 'Azure Resource Graph',
      services: ['Network Security Groups', 'Azure Storage Accounts', 'Key Vaults'],
      emulation: 'Resource Graph State Sync',
      color: '#0089D6',
    },
    {
      name: 'Google Cloud Platform',
      tag: 'Cloud Asset Inventory',
      services: ['Cloud Storage', 'Compute Firewall Rules', 'IAM Policy Bindings'],
      emulation: 'Asset Feed Normalization',
      color: '#4285F4',
    },
  ]

  const iacFormats = [
    { name: 'Terraform (HCL2)', ext: '.tf', desc: 'Resource blocks, variables, locals & module graphs' },
    { name: 'AWS CloudFormation', ext: '.yaml / .json', desc: 'Intrinsic functions (Ref, Fn::GetAtt) & parameter stacks' },
    { name: 'Kubernetes Manifests', ext: '.yaml', desc: 'Pod security standards, RBAC, DaemonSets & host mounts' },
    { name: 'Helm Charts', ext: 'Chart.yaml', desc: 'Template rendering & variable value overlays' },
  ]

  const integrations = [
    { category: 'Static Scanners', tools: 'Checkov • tfsec • KICS' },
    { category: 'Secrets Engines', tools: 'Gitleaks • TruffleHog • Shannon Entropy' },
    { category: 'Validation Harness', tools: 'terraform validate • cfn-lint • LocalStack' },
    { category: 'Shift-Left Delivery', tools: 'VS Code Extension • Git Pre-Commit • SARIF' },
  ]

  return (
    <section className="multicloud-section" id="integrations" aria-label="Multi-Cloud and Integrations">
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
              MULTI-CLOUD ECOSYSTEM INTEGRATION
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            ARCHITECTED FOR
            <br />
            <span className="heading-gradient">MULTI-CLOUD REALITY.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Enterprises do not run a single template in isolation. AgentShield AI ingests polyglot
            IaC across AWS, Azure, and GCP, reconciling declared infrastructure against live
            cloud drift without modifying live resources.
          </motion.p>
        </div>

        {/* Convergence Visual Story Strip: Cloud environments -> Converge -> AgentShield -> Analysis -> Security Decision */}
        <div className="multicloud-flow-banner">
          <div className="flow-banner-item">
            <span className="banner-step">1</span>
            <div className="flow-banner-text">
              <span className="banner-name">CLOUD ENVIRONMENTS</span>
              <span className="banner-sub">AWS • Azure • GCP</span>
            </div>
          </div>
          <span className="flow-banner-arrow">→</span>
          <div className="flow-banner-item">
            <span className="banner-step">2</span>
            <div className="flow-banner-text">
              <span className="banner-name">CONVERGE</span>
              <span className="banner-sub">Multi-IaC Ingestion</span>
            </div>
          </div>
          <span className="flow-banner-arrow">→</span>
          <div className="flow-banner-item active-hub">
            <span className="banner-step">3</span>
            <div className="flow-banner-text">
              <span className="banner-name">AGENTSHIELD CORE</span>
              <span className="banner-sub">LangGraph State DAG</span>
            </div>
          </div>
          <span className="flow-banner-arrow">→</span>
          <div className="flow-banner-item">
            <span className="banner-step">4</span>
            <div className="flow-banner-text">
              <span className="banner-name">CROSS-CLOUD ANALYSIS</span>
              <span className="banner-sub">Topological Reasoning</span>
            </div>
          </div>
          <span className="flow-banner-arrow">→</span>
          <div className="flow-banner-item">
            <span className="banner-step">5</span>
            <div className="flow-banner-text">
              <span className="banner-name">SECURITY DECISION</span>
              <span className="banner-sub">Sandbox Validated</span>
            </div>
          </div>
        </div>

        {/* Converging Architecture Visualizer */}
        <div className="converging-engine-canvas">
          {/* Left Ingress Streams (Multi-Cloud & Polyglot IaC) */}
          <div className="ingress-streams-column">
            <span className="stream-column-title">HETEROGENEOUS INPUT STREAMS</span>

            <div className="cloud-provider-cards">
              {clouds.map((cloud) => (
                <div key={cloud.name} className="cloud-stream-card">
                  {/* Subtle Glass Reflection Sheen */}
                  <div className="glass-reflection-sheen" />

                  <div className="cloud-card-header">
                    <div className="cloud-color-indicator" style={{ backgroundColor: cloud.color }} />
                    <span className="cloud-name">{cloud.name}</span>
                    <span className="cloud-sdk-tag">{cloud.tag}</span>
                  </div>
                  <div className="cloud-services-pills">
                    {cloud.services.map((s) => (
                      <span key={s} className="service-pill">
                        {s}
                      </span>
                    ))}
                  </div>
                  <div className="cloud-emulation-sub">Sandbox: {cloud.emulation}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Center Convergence Arteries */}
          <div className="convergence-artery-column">
            <div className="laser-artery top" />
            <div className="laser-artery middle" />
            <div className="laser-artery bottom" />

            {/* Central Core Shield Engine */}
            <div className="central-engine-nexus">
              <div className="nexus-glow-ring" />
              <div className="nexus-icon-box">
                <Shield size={32} className="nexus-shield-svg" />
              </div>
              <div className="nexus-label">AGENTSHIELD AI</div>
              <div className="nexus-sub">6-Agent LangGraph State Engine</div>
            </div>

            <div className="laser-artery egress" />
          </div>

          {/* Right Egress Streams (Verified Remediation & Compliance) */}
          <div className="egress-streams-column">
            <span className="stream-column-title">VALIDATED OUTPUTS &amp; CONTROLS</span>

            {/* Supported IaC Formats Card */}
            <div className="egress-format-card">
              <div className="egress-card-header">
                <FileCode size={16} />
                <span>Polyglot IaC Formats</span>
              </div>
              <div className="iac-format-list">
                {iacFormats.map((format) => (
                  <div key={format.name} className="iac-format-item">
                    <span className="iac-ext">{format.ext}</span>
                    <div className="iac-info">
                      <span className="iac-name">{format.name}</span>
                      <span className="iac-desc">{format.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tooling & Framework Grid */}
            <div className="tooling-integration-card">
              <div className="egress-card-header">
                <Layers size={16} />
                <span>Integrated Tooling Adapters</span>
              </div>
              <div className="tooling-pills-grid">
                {integrations.map((item) => (
                  <div key={item.category} className="tooling-pill-row">
                    <span className="tool-category">{item.category}:</span>
                    <span className="tool-names">{item.tools}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
