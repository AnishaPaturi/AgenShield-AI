import { motion } from 'framer-motion'
import { Layers, Network, Cpu, ShieldCheck, Database, GitPullRequest } from 'lucide-react'

export default function Scene05Architecture() {
  const blueprintNodes = [
    { id: 'ast', label: 'AST', sub: 'Polyglot Parser', icon: Layers, x: 100, y: 70 },
    { id: 'langgraph', label: 'LANGGRAPH', sub: 'State Machine', icon: Network, x: 340, y: 70 },
    { id: 'rag-llm', label: 'RAG + MULTI-LLM', sub: 'Consensus Reasoning', icon: Cpu, x: 580, y: 70 },
    { id: 'graph', label: 'ATTACK GRAPH', sub: 'Topological BFS', icon: Database, x: 580, y: 220 },
    { id: 'sandbox', label: 'SANDBOX', sub: 'LocalStack Container', icon: ShieldCheck, x: 340, y: 220 },
    { id: 'result', label: 'VERIFIED RESULT', sub: 'Zero-Regression PR', icon: GitPullRequest, x: 100, y: 220 },
  ]

  return (
    <section
      className="cinematic-scene scene-05-architecture"
      id="architecture"
      aria-label="System Architecture"
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
              TECHNICAL BLUEPRINT
              <br />
              <span className="highlight-gradient">SYSTEM SCHEMATIC.</span>
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
              Deterministic stateful architecture engineered for mathematical consensus and verified containment.
            </p>
          </motion.div>
        </div>

        {/* Living Technical Blueprint Existing Directly on the Background (No Outer Card) */}
        <motion.div
          className="pure-blueprint-stage"
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="blueprint-living-canvas">
            <svg className="blueprint-svg-circuit" viewBox="0 0 680 300">
              <defs>
                <linearGradient id="circuitPulse" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#818CF8" stopOpacity="0.8" />
                </linearGradient>
              </defs>

              {/* Thin Blueprint Geometry Wiring */}
              <line x1="170" y1="70" x2="270" y2="70" className="circuit-trace" />
              <line x1="410" y1="70" x2="510" y2="70" className="circuit-trace" />
              <line x1="580" y1="105" x2="580" y2="185" className="circuit-trace" />
              <line x1="510" y1="220" x2="410" y2="220" className="circuit-trace" />
              <line x1="270" y1="220" x2="170" y2="220" className="circuit-trace" />

              {/* Data Signal traversing circuit */}
              <circle r="3" fill="#38BDF8">
                <animateMotion
                  path="M 170 70 L 510 70 L 580 70 L 580 220 L 170 220"
                  dur="4.8s"
                  repeatCount="indefinite"
                />
              </circle>
            </svg>

            {/* Seamless Node Markers floating directly in the scene */}
            <div className="blueprint-floating-nodes">
              {blueprintNodes.map((bn, idx) => {
                const Icon = bn.icon
                return (
                  <div
                    key={bn.id}
                    className="blueprint-floating-node"
                    style={{ left: `${(bn.x / 680) * 100}%`, top: `${(bn.y / 300) * 100}%` }}
                  >
                    <div className="node-marker-header">
                      <Icon size={14} className="node-marker-icon" />
                      <span className="node-coord-tag">0{idx + 1}</span>
                    </div>
                    <span className="node-marker-title">{bn.label}</span>
                    <span className="node-marker-subtitle">{bn.sub}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
