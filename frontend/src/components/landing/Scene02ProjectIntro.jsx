import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function Scene02ProjectIntro() {
  const [isExploitActive, setIsExploitActive] = useState(false)

  // Toggle exploit visualization cycle smoothly
  useEffect(() => {
    const timer = setInterval(() => {
      setIsExploitActive((prev) => !prev)
    }, 4200)
    return () => clearInterval(timer)
  }, [])

  return (
    <section
      className="cinematic-scene scene-02-intro"
      id="intro"
      aria-label="Project Introduction"
    >
      <div className="scene-container">
        <div className="scene-two-col-layout">
          {/* Left Column: Statement & Short Concept (Enters from LEFT) */}
          <motion.div
            className="scene-col-left"
            initial={{ opacity: 0, x: -70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="scene-heading-clean">
              FROM STATIC CHECKS
              <br />
              <span className="highlight-gradient">TO CONTEXTUAL SECURITY.</span>
            </h2>

            <p className="scene-pure-description">
              Traditional linters inspect misconfigurations in isolation. AgentShield correlates your entire cloud infrastructure into an exploit topology, proving breach viability before raising an alert.
            </p>
          </motion.div>

          {/* Right Column: Floating IaC Graph (Directly in Scene, No Card Box) */}
          <motion.div
            className="scene-col-right"
            initial={{ opacity: 0, x: 70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="floating-graph-stage">
              <svg className="iac-graph-svg" viewBox="0 0 540 320" fill="none">
                <defs>
                  <linearGradient id="exploitLaser" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#38BDF8" />
                    <stop offset="50%" stopColor="#A78BFA" />
                    <stop offset="100%" stopColor="#F43F5E" />
                  </linearGradient>
                  <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3.5" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                </defs>

                {/* Base Faint Geometry Links */}
                <line x1="80" y1="160" x2="210" y2="90" className="base-graph-link" />
                <line x1="80" y1="160" x2="210" y2="230" className="base-graph-link" />
                <line x1="210" y1="90" x2="350" y2="90" className="base-graph-link" />
                <line x1="210" y1="230" x2="350" y2="230" className="base-graph-link" />
                <line x1="350" y1="90" x2="460" y2="160" className="base-graph-link" />
                <line x1="350" y1="230" x2="460" y2="160" className="base-graph-link" />

                {/* Active Exploit Vector Route (Gateway -> Lambda -> RDS) */}
                <path
                  d="M 80 160 L 210 90 L 350 90 L 460 160"
                  className={`exploit-laser-path ${isExploitActive ? 'active' : ''}`}
                  stroke="url(#exploitLaser)"
                  strokeWidth={isExploitActive ? 3 : 1}
                  filter={isExploitActive ? 'url(#glowFilter)' : 'none'}
                />

                {/* Traveling packet when exploit is active */}
                {isExploitActive && (
                  <circle r="4" fill="#F43F5E" className="exploit-packet-pulse">
                    <animateMotion
                      path="M 80 160 L 210 90 L 350 90 L 460 160"
                      dur="2.4s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}

                {/* Node 1: Gateway */}
                <g className="graph-node-group" transform="translate(80, 160)">
                  <circle r="20" className="node-bg" />
                  <circle r="24" className="node-ring" />
                  <text y="36" className="node-label">GATEWAY</text>
                </g>

                {/* Node 2: Lambda */}
                <g className="graph-node-group" transform="translate(210, 90)">
                  <circle r="20" className={`node-bg ${isExploitActive ? 'compromised' : ''}`} />
                  <circle r="24" className="node-ring" />
                  <text y="36" className="node-label">LAMBDA</text>
                </g>

                {/* Node 3: VPC Peering */}
                <g className="graph-node-group" transform="translate(210, 230)">
                  <circle r="18" className="node-bg" />
                  <circle r="22" className="node-ring" />
                  <text y="36" className="node-label">VPC SUBNET</text>
                </g>

                {/* Node 4: IAM Role */}
                <g className="graph-node-group" transform="translate(350, 90)">
                  <circle r="20" className={`node-bg ${isExploitActive ? 'compromised' : ''}`} />
                  <circle r="24" className="node-ring" />
                  <text y="36" className="node-label">IAM ROLE</text>
                </g>

                {/* Node 5: S3 Assets */}
                <g className="graph-node-group" transform="translate(350, 230)">
                  <circle r="18" className="node-bg" />
                  <circle r="22" className="node-ring" />
                  <text y="36" className="node-label">S3 BUCKET</text>
                </g>

                {/* Node 6: RDS Crown Jewel */}
                <g className="graph-node-group" transform="translate(460, 160)">
                  <circle
                    r="22"
                    className={`node-bg ${isExploitActive ? 'crown-jewel-risk' : ''}`}
                  />
                  <circle r="26" className="node-ring crown-ring" />
                  <text y="40" className="node-label">RDS DATABASE</text>
                </g>
              </svg>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
