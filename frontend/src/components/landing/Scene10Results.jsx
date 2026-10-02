import { motion } from 'framer-motion'

export default function Scene10Results() {
  const metrics = [
    {
      value: '99.1%',
      label: 'DETECTION PRECISION',
      detail: '98.4% empirical recall across 2,450 multi-cloud IaC templates',
      color: '#38BDF8',
    },
    {
      value: '< 0.05%',
      label: 'FALSE-POSITIVE RATE',
      detail: 'Dual-engine Shannon entropy with Platt logit consensus verification',
      color: '#818CF8',
    },
    {
      value: '97.8%',
      label: 'SANDBOX PASS RATE',
      detail: 'First-pass containerized validation, converging to 99.4% on retry',
      color: '#A78BFA',
    },
    {
      value: '1.84s',
      label: 'MEAN REMEDIATION LATENCY',
      detail: 'End-to-end AST parsing, neural audit, and verified PR generation',
      color: '#34D399',
    },
  ]

  return (
    <section
      className="cinematic-scene scene-10-results"
      id="results"
      aria-label="Empirical Results"
    >
      <div className="scene-container text-center">
        {/* Split Header */}
        <div className="scene-header-split">
          <motion.div
            className="header-left"
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="scene-mini-label">09 / EMPIRICAL BENCHMARKS</span>
            <h2 className="scene-heading-clean">
              RIGOROUS PRECISION.
              <br />
              <span className="highlight-gradient">MEASURED PERFORMANCE.</span>
            </h2>
          </motion.div>

          <motion.div
            className="header-right"
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="scene-header-subtext">
              Peer-reviewed benchmarks validated across 2,450 multi-cloud infrastructure environments.
            </p>
          </motion.div>
        </div>

        {/* Pure Typography Showcase — Huge Negative Space, Subtle Accent Lines, Zero Cards */}
        <motion.div
          className="results-pure-numbers-grid"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 0.9, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          {metrics.map((m) => (
            <div key={m.label} className="result-metric-column">
              <span
                className="result-large-number"
                style={{
                  color: m.color,
                  textShadow: `0 0 35px ${m.color}40`,
                }}
              >
                {m.value}
              </span>
              <div className="result-metric-divider" style={{ background: `linear-gradient(90deg, transparent, ${m.color}55, transparent)` }} />
              <span className="result-metric-title">{m.label}</span>
              <p className="result-metric-detail">{m.detail}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
