import { useState } from 'react'
import { motion } from 'framer-motion'
import { Cpu, Lock, Search, Network, GitPullRequest, FileCode2, Zap } from 'lucide-react'

export default function Scene03Agents() {
  const [activeAgent, setActiveAgent] = useState(0)

  const agents = [
    { name: 'AST Parser', color: '#38BDF8', icon: FileCode2 },
    { name: 'Secrets Scanner', color: '#F472B6', icon: Lock },
    { name: 'Security Analyst', color: '#A78BFA', icon: Search },
    { name: 'Multi-LLM Ensemble', color: '#34D399', icon: Cpu },
    { name: 'Attack-Path Prioritizer', color: '#FB923C', icon: Network },
    { name: 'Sandbox Remediation', color: '#EC4899', icon: GitPullRequest },
  ]

  // Symmetrical polar positions around center (cx: 360, cy: 220, r: 155)
  const cx = 360
  const cy = 220
  const radius = 155

  const agentCoords = agents.map((_, i) => {
    const angle = ((i * 60 - 90) * Math.PI) / 180
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    }
  })

  return (
    <section
      className="cinematic-scene scene-03-agents"
      id="agents"
      aria-label="Six Autonomous Agents"
    >
      <div className="scene-container text-center">
        {/* Header split entrance */}
        <div className="scene-header-split">
          <motion.div
            className="header-left"
            initial={{ opacity: 0, x: -70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="scene-heading-clean">
              SIX AUTONOMOUS AGENTS.
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
              Coordinated by a central state machine with formal contracts and zero hallucination propagation.
            </p>
          </motion.div>
        </div>

        {/* Central Circular Network — Pure Visual without Cards or Telemetry Pills */}
        <motion.div
          className="pure-agent-network-stage"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <svg className="agents-svg-network" viewBox="0 0 720 440" preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="agentLaserGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Orbit rings */}
            <circle cx={cx} cy={cy} r={radius} className="network-orbit-ring" />
            <circle cx={cx} cy={cy} r={radius * 0.55} className="network-inner-ring" />

            {/* Connection lines from center to each node */}
            {agentCoords.map((pos, idx) => (
              <line
                key={`line-${idx}`}
                x1={cx}
                y1={cy}
                x2={pos.x}
                y2={pos.y}
                className={`agent-bus-line ${activeAgent === idx ? 'bus-active' : ''}`}
                stroke={activeAgent === idx ? agents[idx].color : 'rgba(129, 140, 248, 0.18)'}
                strokeWidth={activeAgent === idx ? 2 : 1}
                filter={activeAgent === idx ? 'url(#agentLaserGlow)' : 'none'}
              />
            ))}

            {/* Flowing packet along lines */}
            {agentCoords.map((pos, idx) => (
              <circle key={`pkt-${idx}`} r="3" fill={agents[idx].color} className="agent-bus-packet">
                <animateMotion
                  path={`M ${cx} ${cy} L ${pos.x} ${pos.y}`}
                  dur={`${2.4 + idx * 0.3}s`}
                  repeatCount="indefinite"
                />
              </circle>
            ))}

            {/* Center Node: AGENTSHIELD ORCHESTRATOR */}
            <g className="network-center-group" transform={`translate(${cx}, ${cy})`}>
              <circle r="48" className="center-node-glow-halo" />
              <circle r="40" className="center-node-core" />
              <Zap size={20} className="center-node-icon" x="-10" y="-20" />
              <text y="4" className="center-node-title">AGENTSHIELD</text>
              <text y="15" className="center-node-sub">ORCHESTRATOR</text>
            </g>

            {/* Six Surrounding Nodes */}
            {agentCoords.map((pos, idx) => {
              const a = agents[idx]
              const isSelected = activeAgent === idx
              const Icon = a.icon

              return (
                <g
                  key={a.name}
                  className={`agent-node-group ${isSelected ? 'selected' : ''}`}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onClick={() => setActiveAgent(idx)}
                  style={{ cursor: 'pointer' }}
                >
                  <circle
                    r="26"
                    className="agent-node-disk"
                    stroke={isSelected ? a.color : 'rgba(148, 163, 184, 0.22)'}
                    strokeWidth={isSelected ? 2 : 1}
                  />
                  <circle r="22" className="agent-node-inner" fill="#060A16" />
                  <foreignObject x="-10" y="-10" width="20" height="20">
                    <Icon size={19} color={isSelected ? a.color : '#94A3B8'} />
                  </foreignObject>
                  <text y="38" className="agent-node-label" fill={isSelected ? '#F8FAFC' : '#CBD5E1'}>
                    {a.name}
                  </text>
                </g>
              )
            })}
          </svg>
        </motion.div>
      </div>
    </section>
  )
}
