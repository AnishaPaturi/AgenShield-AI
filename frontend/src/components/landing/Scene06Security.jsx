import { motion } from 'framer-motion'

export default function Scene06Security() {
  const steps = [
    { stage: 'THREAT', detail: 'Public ingress open on Port 5432', color: '#F43F5E' },
    { stage: 'DETECTION', detail: 'Exposed credential + permissive rule', color: '#FB923C' },
    { stage: 'ANALYSIS', detail: 'Lateral traversal to IAM Administrator', color: '#A78BFA' },
    { stage: 'RISK', detail: 'Crown-jewel database breach viable', color: '#F472B6' },
    { stage: 'DECISION', detail: 'Automated quarantine and patch', color: '#34D399' },
  ]

  return (
    <section
      className="cinematic-scene scene-06-security"
      id="security"
      aria-label="Security Intelligence"
    >
      <div className="scene-container">
        <div className="scene-two-col-layout">
          {/* Left Column: Statement & Concept (Enters from LEFT) */}
          <motion.div
            className="scene-col-left"
            initial={{ opacity: 0, x: -70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="scene-heading-clean">
              SECURITY THAT SEES
              <br />
              <span className="highlight-gradient">HOW THREATS PROPAGATE.</span>
            </h2>

            <p className="scene-pure-description">
              AgentShield doesn&apos;t just flag an isolated misconfiguration. It traces the full multi-hop adversary trajectory through your infrastructure to sever the attack path at its root.
            </p>
          </motion.div>

          {/* Right Column: Pure Dramatic Downward Attack Path (No Boxes/Pills) */}
          <motion.div
            className="scene-col-right"
            initial={{ opacity: 0, x: 70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="pure-threat-trajectory">
              <div className="trajectory-spine-line" />

              {steps.map((st) => (
                <div key={st.stage} className="trajectory-step-item">
                  <div
                    className="trajectory-dot"
                    style={{
                      backgroundColor: st.color,
                      boxShadow: `0 0 12px ${st.color}`,
                    }}
                  />
                  <div className="trajectory-meta">
                    <span className="trajectory-stage" style={{ color: st.color }}>
                      {st.stage}
                    </span>
                    <span className="trajectory-sub">{st.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
