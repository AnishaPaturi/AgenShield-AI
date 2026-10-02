import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getCurrentUser } from '../../auth'

export default function Scene01Opening() {
  const user = getCurrentUser()

  return (
    <section
      className="cinematic-scene scene-01-opening"
      id="opening"
      aria-label="AgentShield AI Opening"
    >
      <div className="scene-container text-center">
        {/* Split entrance composition: Headline from LEFT, Supporting + CTA from RIGHT */}
        <div className="scene-01-pure-composition">
          {/* Main Monumental Headline entering from LEFT */}
          <motion.div
            className="scene-01-headline-block"
            initial={{ opacity: 0, x: -80 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 1.0, ease: [0.16, 1, 0.3, 1] }}
          >
            <h1 className="cinematic-monumental-heading">
              <span className="heading-line">SECURITY</span>
              <span className="heading-line">THAT THINKS</span>
              <span className="heading-line highlight-gradient">IN PATHS.</span>
            </h1>
          </motion.div>

          {/* Minimal supporting line + Single CTA entering from RIGHT */}
          <motion.div
            className="scene-01-support-block"
            initial={{ opacity: 0, x: 80 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 1.0, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="scene-01-subtext">
              Autonomous multi-agent security for Infrastructure-as-Code.
            </p>

            <div className="scene-01-cta-row">
              <Link
                to={user ? '/dashboard' : '/sign-up'}
                className="cinematic-primary-cta"
                id="hero-cta-btn"
              >
                <span>{user ? 'Launch Console' : 'Get Started'}</span>
                <ArrowRight size={15} className="cta-icon-arrow" />
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
