import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getCurrentUser } from '../../auth'

export default function Scene11FinalCTA() {
  const user = getCurrentUser()

  return (
    <section
      className="cinematic-scene scene-11-final-cta"
      id="final-cta"
      aria-label="Launch AgentShield"
    >
      <div className="scene-container text-center pure-final-container">
        <motion.div
          className="pure-final-content"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="pure-monumental-heading">
            SECURE EVERY <span className="highlight-gradient">PATH.</span>
          </h2>

          <p className="pure-final-subtext">
            Continuous context-aware security intelligence for modern cloud infrastructure.
          </p>

          <div className="pure-final-cta-wrapper">
            <Link
              to={user ? '/dashboard' : '/sign-up'}
              className="cinematic-primary-cta pure-cta-btn"
              id="final-launch-btn"
            >
              <span>Launch AgentShield</span>
              <ArrowRight size={16} className="cta-icon-arrow" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
