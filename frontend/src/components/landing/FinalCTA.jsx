import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { ArrowRight, Shield, Terminal, CheckCircle2 } from 'lucide-react'
import GithubIcon from './GithubIcon'

export default function FinalCTA() {
  const prefersReduced = useReducedMotion()

  return (
    <section className="final-cta-section" id="cta" aria-label="Final Call to Action">
      {/* Subtle Atmospheric Animated Glow & Grid */}
      <div className="cta-ambient-glow" />
      <div className="cta-cyber-grid" />

      <div className="section-container">
        <div className="final-cta-card">
          <motion.div
            className="cta-eyebrow-wrapper"
            initial={{ opacity: 0, y: prefersReduced ? 0 : 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              DEPLOY WITH CONFIDENCE
            </span>
          </motion.div>

          <motion.h2
            className="final-cta-headline"
            initial={{ opacity: 0, y: prefersReduced ? 0 : 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            SECURE THE PATH
            <br />
            BEFORE IT BECOMES
            <br />
            <span className="heading-gradient">AN ATTACK.</span>
          </motion.h2>

          <motion.p
            className="final-cta-subtext"
            initial={{ opacity: 0, y: prefersReduced ? 0 : 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Explore AgentShield AI and see how autonomous security intelligence can analyze,
            prioritize and validate infrastructure risk across multi-cloud environments.
          </motion.p>

          <motion.div
            className="final-cta-buttons-group"
            initial={{ opacity: 0, y: prefersReduced ? 0 : 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            <Link to="/dashboard" className="cta-primary-btn">
              <Shield size={16} className="btn-shield-icon" />
              <span>Launch AgentShield</span>
              <ArrowRight size={16} className="btn-arrow" />
            </Link>

            <a
              href="https://github.com/AnishaPaturi/AgenShield-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="cta-secondary-btn"
            >
              <GithubIcon size={17} />
              <span>Explore GitHub</span>
            </a>
          </motion.div>

          <div className="cta-verification-footer">
            <div className="verification-item">
              <CheckCircle2 size={14} className="verif-check" />
              <span>Zero Live Cloud Mutation Risk</span>
            </div>
            <div className="verification-divider" />
            <div className="verification-item">
              <CheckCircle2 size={14} className="verif-check" />
              <span>100% Passing Test Harness</span>
            </div>
            <div className="verification-divider" />
            <div className="verification-item">
              <CheckCircle2 size={14} className="verif-check" />
              <span>LocalStack Sandbox Emulation</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
