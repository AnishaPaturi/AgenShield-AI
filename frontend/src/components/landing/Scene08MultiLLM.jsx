import { motion } from 'framer-motion'

export default function Scene08MultiLLM() {
  return (
    <section
      className="cinematic-scene scene-08-multillm"
      id="multillm"
      aria-label="Multi-LLM Consensus"
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
              MULTI-MODEL ENSEMBLE.
              <br />
              <span className="highlight-gradient">PARALLEL CONSENSUS.</span>
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
              Dual analysis streams converge through calibrated agreement, eliminating single-model blind spots.
            </p>
          </motion.div>
        </div>

        {/* Pure Dual Stream Convergence (No Surrounding Glass Container) */}
        <motion.div
          className="pure-consensus-stage"
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="pure-consensus-flow">
            {/* Left Points: CLAUDE & GPT */}
            <div className="pure-llm-sources">
              <div className="pure-llm-point">
                <span className="llm-point-name">CLAUDE</span>
                <span className="llm-point-sub">Anthropic</span>
              </div>
              <div className="pure-llm-point">
                <span className="llm-point-name">GPT</span>
                <span className="llm-point-sub">OpenAI</span>
              </div>
            </div>

            {/* Middle SVG Convergence Streams */}
            <div className="pure-llm-svg-box">
              <svg className="pure-llm-svg" viewBox="0 0 200 160">
                <defs>
                  <linearGradient id="claudeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#FB923C" />
                    <stop offset="100%" stopColor="#A78BFA" />
                  </linearGradient>
                  <linearGradient id="gptGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#34D399" />
                    <stop offset="100%" stopColor="#A78BFA" />
                  </linearGradient>
                </defs>

                <path d="M 0 35 C 90 35, 120 80, 200 80" className="llm-stream-wire" stroke="url(#claudeGrad)" />
                <path d="M 0 125 C 90 125, 120 80, 200 80" className="llm-stream-wire" stroke="url(#gptGrad)" />

                <circle r="3" fill="#FB923C">
                  <animateMotion path="M 0 35 C 90 35, 120 80, 200 80" dur="2.2s" repeatCount="indefinite" />
                </circle>
                <circle r="3" fill="#34D399">
                  <animateMotion path="M 0 125 C 90 125, 120 80, 200 80" dur="2.2s" repeatCount="indefinite" />
                </circle>
              </svg>
            </div>

            {/* Right Stages: CONSENSUS → CONFIDENCE → DECISION */}
            <div className="pure-consensus-stages">
              <div className="pure-stage-step">
                <span className="step-tag-text">CONSENSUS</span>
                <span className="step-tag-sub">Agreement</span>
              </div>

              <span className="pure-step-arrow">→</span>

              <div className="pure-stage-step">
                <span className="step-tag-text">CONFIDENCE</span>
                <span className="step-tag-sub">Calibrated</span>
              </div>

              <span className="pure-step-arrow">→</span>

              <div className="pure-stage-step highlight">
                <span className="step-tag-text success">DECISION</span>
                <span className="step-tag-sub">Deterministic</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
