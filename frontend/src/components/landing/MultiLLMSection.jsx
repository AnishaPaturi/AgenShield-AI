import { useState, useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Scale,
  Sparkles,
  ArrowDown,
  ShieldCheck,
  TrendingUp,
  Activity,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function MultiLLMSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)

  // Scroll phase:
  // Step 1: Models reasoning (>= 0.15)
  // Step 2: Consensus Agreement (>= 0.40)
  // Step 3: Confidence Score Calibrated (>= 0.65)
  // Step 4: Final Decision Out (>= 0.82)
  const isModelsActive = progress >= 0.12 || prefersReduced
  const isConsensusActive = progress >= 0.38 || prefersReduced
  const isConfidenceActive = progress >= 0.62 || prefersReduced
  const isDecisionActive = progress >= 0.80 || prefersReduced

  const models = [
    {
      id: 'model-claude',
      name: 'Model A: Claude 3.5 Sonnet',
      provider: 'Anthropic',
      role: 'IaC Semantic Reasoning & Chain-of-Thought',
      weight: 'w₁ = 0.50',
      finding: 'Flagged CKV_AWS_20 (Port 5432 Ingress)',
      confidence: '0.962',
      color: '#A78BFA',
    },
    {
      id: 'model-gpt4o',
      name: 'Model B: OpenAI GPT-4o',
      provider: 'OpenAI',
      role: 'Cross-Domain Policy & IAM Matrix Validation',
      weight: 'w₂ = 0.50',
      finding: 'Flagged CKV_AWS_20 (Port 5432 Ingress)',
      confidence: '0.966',
      color: '#34D399',
    },
    {
      id: 'model-deepseek',
      name: 'Model C: DeepSeek-Coder-V2',
      provider: 'DeepSeek / Llama',
      role: 'Syntax Tree & AST Mutation Baseline Arbiter',
      weight: 'Arbiter',
      finding: 'Confirmed Ingress Exploit Route',
      confidence: '0.954',
      color: '#38BDF8',
    },
  ]

  return (
    <section
      ref={sectionRef}
      className="multillm-section cinematic-scene-stage"
      id="multi-llm"
      aria-label="Multi-LLM Ensemble Consensus Engine"
    >
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-block text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              PLATT-CALIBRATED MULTI-MODEL VOTING
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            MULTI-LLM ENSEMBLE.
            <br />
            <span className="heading-gradient">ZERO-HALLUCINATION CONSENSUS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Single LLMs hallucinate security rules ~15% of the time. AgentShield coordinates
            parallel, independent model evaluation. Only findings verified across models with
            calibrated confidence (C ≥ 0.85) proceed to automated remediation.
          </motion.p>

          {/* Stepper Strip */}
          <div className="llm-stepper-strip">
            <span className={`llm-step-badge ${isModelsActive ? 'active' : ''}`}>1. PARALLEL MODELS</span>
            <span className="llm-step-arrow">→</span>
            <span className={`llm-step-badge ${isConsensusActive ? 'active' : ''}`}>2. LOGIT CONSENSUS</span>
            <span className="llm-step-arrow">→</span>
            <span className={`llm-step-badge ${isConfidenceActive ? 'active' : ''}`}>3. CALIBRATED CONFIDENCE</span>
            <span className="llm-step-arrow">→</span>
            <span className={`llm-step-badge ${isDecisionActive ? 'active' : ''}`}>4. FINAL DECISION</span>
          </div>
        </div>

        {/* Visual Multi-LLM Funnel Stage */}
        <div className="multillm-funnel-canvas">
          {/* Row 1: The 3 Models */}
          <div className="llm-models-row">
            {models.map((m, idx) => (
              <div
                key={m.id}
                className={`llm-model-card ${isModelsActive ? 'model-active' : 'model-dormant'}`}
                style={{
                  transition: `all 0.5s ease ${idx * 0.1}s`,
                  borderColor: isModelsActive ? `${m.color}60` : undefined,
                }}
              >
                <div className="model-card-top">
                  <Cpu size={18} style={{ color: m.color }} />
                  <span className="model-weight-tag">{m.weight}</span>
                </div>
                <h4 className="model-name">{m.name}</h4>
                <div className="model-role">{m.role}</div>
                <div className="model-finding-box">
                  <span className="finding-label">EVALUATION:</span>
                  <p className="finding-text">{m.finding}</p>
                </div>
                <div className="model-confidence-bar">
                  <span>Confidence:</span>
                  <strong style={{ color: m.color }}>{m.confidence}</strong>
                </div>
              </div>
            ))}
          </div>

          {/* Conduits from Models to Consensus Core */}
          <div className="llm-funnel-conduits">
            <div className={`funnel-stream left ${isConsensusActive ? 'flowing' : ''}`} />
            <div className={`funnel-stream center ${isConsensusActive ? 'flowing' : ''}`} />
            <div className={`funnel-stream right ${isConsensusActive ? 'flowing' : ''}`} />
          </div>

          {/* Row 2: Consensus Agreement Engine */}
          <div className={`consensus-core-block ${isConsensusActive ? 'consensus-locked' : 'consensus-standby'}`}>
            <div className="consensus-core-header">
              <Scale size={20} className="consensus-icon" />
              <h4>PLATT TEMPERATURE SCALING LOGIT CONSENSUS</h4>
            </div>

            <div className="consensus-equation-box">
              <code>
                C_ens = Σ w_i · C(M_i) + γ · S_agreement · (N_agreed / N_total)
              </code>
            </div>

            <div className="consensus-meta-stats">
              <div className="c-stat">
                <span className="c-stat-k">AGREEMENT FACTOR:</span>
                <span className="c-stat-v">3 / 3 Models (100% Concordance)</span>
              </div>
              <div className="c-stat">
                <span className="c-stat-k">HALLUCINATION RISK:</span>
                <span className="c-stat-v suppressed">&lt; 0.1% Suppressed</span>
              </div>
            </div>
          </div>

          {/* Conduit to Confidence & Decision */}
          <div className="llm-funnel-conduits vertical">
            <div className={`funnel-stream center ${isConfidenceActive ? 'flowing' : ''}`} />
          </div>

          {/* Row 3: Confidence Gauge & Final Decision Gate */}
          <div className={`decision-gate-block ${isDecisionActive ? 'decision-revealed' : 'decision-concealed'}`}>
            <div className="gate-left-gauge">
              <span className="gauge-label">CALIBRATED ENSEMBLE CONFIDENCE</span>
              <div className="gauge-number-box">
                <span className="gauge-big-num">0.964</span>
                <span className="gauge-threshold">THRESHOLD: 0.850</span>
              </div>
              <div className="gauge-progress-track">
                <div
                  className="gauge-progress-fill"
                  style={{ width: isConfidenceActive ? '96.4%' : '0%' }}
                />
              </div>
            </div>

            <div className="gate-right-outcome">
              <div className="outcome-decision-badge">
                <ShieldCheck size={20} className="outcome-decision-icon" />
                <span>FINAL DECISION: AUTONOMOUS PATCH AUTHORIZED</span>
              </div>
              <p className="outcome-decision-desc">
                High confidence agreement confirmed across Claude 3.5 Sonnet and GPT-4o.
                Zero human triage required. Automatic dispatch to sandbox container for validation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
