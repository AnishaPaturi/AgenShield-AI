import { useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  FileCode2,
  KeyRound,
  Network,
  Radar,
  Flame,
  GitCompare,
  Box,
  Layers,
  ChevronRight,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react'

export default function FeatureCard({
  feature,
  index,
  size = 'normal', // 'large', 'wide', or 'normal'
  direction = 'bottom',
}) {
  const [isHovered, setIsHovered] = useState(false)
  const prefersReduced = useReducedMotion()

  const getDirectionVariants = () => {
    if (prefersReduced) return { hidden: { opacity: 0 }, visible: { opacity: 1 } }
    switch (direction) {
      case 'left':
        return {
          hidden: { opacity: 0, x: -35, y: 20 },
          visible: { opacity: 1, x: 0, y: 0 },
        }
      case 'right':
        return {
          hidden: { opacity: 0, x: 35, y: 20 },
          visible: { opacity: 1, x: 0, y: 0 },
        }
      case 'bottom':
      default:
        return {
          hidden: { opacity: 0, y: 40 },
          visible: { opacity: 1, y: 0 },
        }
    }
  }

  const iconMap = {
    iac: FileCode2,
    secrets: KeyRound,
    analyst: Radar,
    attackpath: Network,
    blastradius: Flame,
    prioritize: Layers,
    remediation: GitCompare,
    sandbox: Box,
  }

  const IconComponent = iconMap[feature.iconKey] || ShieldAlert

  return (
    <motion.div
      className={`feature-card-wrapper card-size-${size}`}
      variants={getDirectionVariants()}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-50px' }}
      transition={{
        duration: prefersReduced ? 0.1 : 0.75,
        delay: prefersReduced ? 0 : index * 0.08,
        ease: [0.16, 1, 0.3, 1],
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={`feature-card-inner ${isHovered ? 'hovered' : ''}`}>
        {/* Glass Reflection Sheen */}
        <div className="glass-reflection-sheen" />

        {/* Ambient Top Glow Border */}
        <div className="card-top-highlight" />

        {/* Header: Badge & Icon */}
        <div className="feature-card-header">
          <div className="feature-icon-badge">
            <IconComponent size={20} className="feature-icon" strokeWidth={2.2} />
          </div>
          <span className="feature-engine-pill">{feature.engine}</span>
        </div>

        {/* Typography: Heading & Description */}
        <div className="feature-card-body">
          <div className="feature-category-tag">{feature.category}</div>
          <h3 className="feature-title">{feature.title}</h3>
          <p className="feature-desc">{feature.description}</p>
        </div>

        {/* Technical Details Area (Reveals or expands on hover) */}
        <div className="feature-technical-details">
          <div className="tech-meta-row">
            <span className="tech-label">Key Mechanism</span>
            <span className="tech-value">{feature.mechanism}</span>
          </div>

          {feature.metric && (
            <div className="tech-meta-row">
              <span className="tech-label">Empirical Target</span>
              <span className="tech-value-accent">{feature.metric}</span>
            </div>
          )}

          {/* Code snippet / formula preview for prominent cards */}
          {feature.codePreview && (
            <div className={`feature-code-preview ${isHovered ? 'expanded' : ''}`}>
              <div className="code-preview-header">
                <span className="code-dot red" />
                <span className="code-dot yellow" />
                <span className="code-dot green" />
                <span className="code-preview-title">{feature.codeLabel}</span>
              </div>
              <pre className="code-preview-text">
                <code>{feature.codePreview}</code>
              </pre>
            </div>
          )}
        </div>

        {/* Bottom Interactive Hover Indicator */}
        <div className="feature-card-footer">
          <span className="footer-spec-text">{feature.spec}</span>
          <div className="footer-arrow-wrapper">
            <ChevronRight size={14} className="card-chevron" />
          </div>
        </div>
      </div>
    </motion.div>
  )
}
