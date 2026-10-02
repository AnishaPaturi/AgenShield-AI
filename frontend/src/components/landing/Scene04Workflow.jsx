import { motion } from 'framer-motion'

export default function Scene04Workflow() {
  const steps = [
    { label: 'INPUT', sub: 'IaC Ingestion' },
    { label: 'ANALYSIS', sub: 'AST & Secrets' },
    { label: 'DETECTION', sub: 'Policy Evaluation' },
    { label: 'PRIORITIZATION', sub: 'Attack Graph' },
    { label: 'REMEDIATION', sub: 'Patch Synthesis' },
    { label: 'VALIDATION', sub: 'Sandbox Execution' },
  ]

  return (
    <section
      className="cinematic-scene scene-04-workflow"
      id="workflow"
      aria-label="AgentShield Workflow"
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
              AUTONOMOUS
              <br />
              <span className="highlight-gradient">EXECUTION PIPELINE.</span>
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
              One continuous visual pipeline transforming raw infrastructure code into validated pull requests.
            </p>
          </motion.div>
        </div>

        {/* Elegant Continuous Flowing Beam (No UI Boxes) */}
        <motion.div
          className="pure-pipeline-stage"
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="pipeline-track-container">
            <svg className="pipeline-flowing-svg" viewBox="0 0 960 140" preserveAspectRatio="none">
              <defs>
                <linearGradient id="streamLaserGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.4" />
                  <stop offset="35%" stopColor="#818CF8" stopOpacity="0.9" />
                  <stop offset="70%" stopColor="#A78BFA" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#34D399" stopOpacity="0.8" />
                </linearGradient>
                <filter id="streamGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Faint Guide Line */}
              <line x1="60" y1="50" x2="900" y2="50" className="stream-guide-line" />

              {/* Glowing Laser Path */}
              <line
                x1="60"
                y1="50"
                x2="900"
                y2="50"
                stroke="url(#streamLaserGrad)"
                strokeWidth="2.5"
                filter="url(#streamGlow)"
              />

              {/* Continual Traveling Light Particle */}
              <circle r="4" fill="#38BDF8">
                <animateMotion path="M 60 50 L 900 50" dur="3.6s" repeatCount="indefinite" />
              </circle>
            </svg>

            {/* Seamless Nodes along the Line */}
            <div className="pure-pipeline-nodes">
              {steps.map((st, i) => (
                <div key={st.label} className="pure-pipeline-node">
                  <div className="node-marker-dot">
                    <span className="dot-core" />
                    <span className="dot-ripple" />
                  </div>
                  <div className="node-marker-labels">
                    <span className="marker-title">{st.label}</span>
                    <span className="marker-sub">{st.sub}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
