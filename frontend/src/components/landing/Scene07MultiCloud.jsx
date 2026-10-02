import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'

export default function Scene07MultiCloud() {
  const sources = [
    { name: 'AWS', y: 40, color: '#FF9900' },
    { name: 'AZURE', y: 110, color: '#0089D6' },
    { name: 'GCP', y: 180, color: '#4285F4' },
  ]

  const targets = [
    { name: 'Terraform', y: 30, color: '#844FBA' },
    { name: 'CloudFormation', y: 85, color: '#FF9900' },
    { name: 'Kubernetes', y: 135, color: '#326CE5' },
    { name: 'Helm', y: 190, color: '#0F1689' },
  ]

  return (
    <section
      className="cinematic-scene scene-07-multicloud"
      id="multicloud"
      aria-label="Multi-Cloud Convergence"
    >
      <div className="scene-container text-center">
        {/* Split Header */}
        <div className="scene-header-split">
          <motion.div
            className="header-left"
            initial={{ opacity: 0, x: -70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="scene-heading-clean">
              ANY CLOUD.
              <br />
              <span className="highlight-gradient">ONE UNIFIED INTELLIGENCE.</span>
            </h2>
          </motion.div>

          <motion.div
            className="header-right"
            initial={{ opacity: 0, x: 70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="scene-header-subtext">
              Heterogeneous cloud configurations converge into AgentShield, generating native fixes across all major IaC frameworks.
            </p>
          </motion.div>
        </div>

        {/* Pure Network: Three Points in Space Converging & Radiating Outward (No Cards) */}
        <motion.div
          className="pure-multicloud-stage"
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="space-network-container">
            {/* Left Points: AWS, AZURE, GCP */}
            <div className="space-sources-column">
              {sources.map((s) => (
                <div key={s.name} className="space-point-node source">
                  <span className="point-coord-name" style={{ color: s.color }}>{s.name}</span>
                  <span className="space-point-beacon" style={{ backgroundColor: s.color, boxShadow: `0 0 10px ${s.color}` }} />
                </div>
              ))}
            </div>

            {/* Central SVG Streams with Core */}
            <div className="space-streams-center">
              <svg className="space-svg-bus" viewBox="0 0 360 220" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="inStreamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#818CF8" stopOpacity="0.8" />
                  </linearGradient>
                  <linearGradient id="outStreamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#818CF8" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#34D399" stopOpacity="0.4" />
                  </linearGradient>
                </defs>

                {/* Converging Stream Lines (Left -> Center (180, 110)) */}
                <path d="M 0 40 C 110 40, 120 110, 180 110" className="stream-wire" stroke="url(#inStreamGrad)" />
                <path d="M 0 110 L 180 110" className="stream-wire" stroke="url(#inStreamGrad)" />
                <path d="M 0 180 C 110 180, 120 110, 180 110" className="stream-wire" stroke="url(#inStreamGrad)" />

                {/* Radiating Outward Stream Lines (Center (180, 110) -> Right) */}
                <path d="M 180 110 C 240 110, 250 30, 360 30" className="stream-wire" stroke="url(#outStreamGrad)" />
                <path d="M 180 110 C 240 110, 250 85, 360 85" className="stream-wire" stroke="url(#outStreamGrad)" />
                <path d="M 180 110 C 240 110, 250 135, 360 135" className="stream-wire" stroke="url(#outStreamGrad)" />
                <path d="M 180 110 C 240 110, 250 190, 360 190" className="stream-wire" stroke="url(#outStreamGrad)" />

                {/* Animated Light Stream Runners */}
                <circle r="3" fill="#38BDF8">
                  <animateMotion path="M 0 40 C 110 40, 120 110, 180 110" dur="2.4s" repeatCount="indefinite" />
                </circle>
                <circle r="3" fill="#818CF8">
                  <animateMotion path="M 0 110 L 180 110" dur="2.1s" repeatCount="indefinite" />
                </circle>
                <circle r="3" fill="#34D399">
                  <animateMotion path="M 180 110 C 240 110, 250 30, 360 30" dur="2.6s" repeatCount="indefinite" />
                </circle>
                <circle r="3" fill="#34D399">
                  <animateMotion path="M 180 110 C 240 110, 250 135, 360 135" dur="2.3s" repeatCount="indefinite" />
                </circle>
              </svg>

              {/* Central Core: AGENTSHIELD INTELLIGENCE */}
              <div className="space-core-intelligence">
                <Shield size={18} className="space-core-icon" />
                <span className="space-core-txt">AGENTSHIELD</span>
                <span className="space-core-sub">INTELLIGENCE</span>
              </div>
            </div>

            {/* Right Points: Terraform, CloudFormation, Kubernetes, Helm */}
            <div className="space-targets-column">
              {targets.map((t) => (
                <div key={t.name} className="space-point-node target">
                  <span className="space-point-beacon" style={{ backgroundColor: '#34D399', boxShadow: '0 0 10px #34D399' }} />
                  <span className="point-coord-name">{t.name}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
