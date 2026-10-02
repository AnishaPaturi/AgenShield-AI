import { useState, useRef, useEffect } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  FileUp,
  Cpu,
  ShieldAlert,
  SlidersHorizontal,
  GitPullRequest,
  CheckCircle2,
  ArrowRight,
  Database,
  Terminal,
  Activity,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function WorkflowSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)
  const [activeStage, setActiveStage] = useState(0)

  const stages = [
    {
      id: 'input',
      stepNum: '01',
      title: 'IaC Ingestion',
      subtitle: 'Multi-Format Input',
      icon: FileUp,
      color: '#38BDF8',
      summary: 'Ingests raw Terraform HCL2, CloudFormation YAML, Kubernetes manifests, or Helm charts.',
      inputArtifact: 'main.tf / template.yaml / k8s.yaml',
      action: 'Normalizes input templates into clean AST structures with dynamic variables pre-evaluated.',
      outputArtifact: 'Normalized_AST_Graph.json',
      sampleSnippet: `POST /api/v1/scan/iac
{
  "format": "terraform",
  "files": ["main.tf", "variables.tf"],
  "environment": "production"
}`,
    },
    {
      id: 'analysis',
      stepNum: '02',
      title: 'Semantic Analysis',
      subtitle: 'Secrets + Hybrid RAG',
      icon: Cpu,
      color: '#A78BFA',
      summary: 'Intercepts high-entropy secrets locally and retrieves CIS / NIST compliance controls.',
      inputArtifact: 'Normalized_AST_Graph.json',
      action: 'Cryptographically masks exposed keys, queries Qdrant vector DB for CIS/NIST compliance guidelines.',
      outputArtifact: 'Sanitized_AST_Plus_RAG_Context.json',
      sampleSnippet: `[SecretsEngine] Intercepted 1 exposed AWS key (entropy 4.8) -> MASKED
[HybridRAG] Retrieved CIS AWS 2.1.5, NIST AC-6, SOC2 CC6.1
[State] Transferred to Parallel LLM Reasoning Bus`,
    },
    {
      id: 'detection',
      stepNum: '03',
      title: 'Vulnerability Detection',
      subtitle: 'Multi-LLM Consensus',
      icon: ShieldAlert,
      color: '#F43F5E',
      summary: 'Claude 3.5 Sonnet and GPT-4o independently evaluate AST nodes against security baselines.',
      inputArtifact: 'Sanitized_AST_Plus_RAG_Context.json',
      action: 'Executes parallel Chain-of-Thought reasoning. Cross-model consensus eliminates false positives.',
      outputArtifact: 'Validated_Vulnerability_Set.json',
      sampleSnippet: `Model A (Claude 3.5): Flagged CKV_AWS_20 (Port 5432 ingress) [Conf: 0.95]
Model B (GPT-4o):     Flagged CKV_AWS_20 (Port 5432 ingress) [Conf: 0.97]
Ensemble Consensus:   C_ens = 0.964 (High Agreement -> Validated)`,
    },
    {
      id: 'prioritization',
      stepNum: '04',
      title: 'Topological Prioritization',
      subtitle: 'BFS Attack Path & Blast Radius',
      icon: SlidersHorizontal,
      color: '#FB923C',
      summary: 'Traces ingress paths to crown-jewel assets and calculates composite risk priority (0–100).',
      inputArtifact: 'Validated_Vulnerability_Set.json',
      action: 'BFS graph traversal finds exploit route from Internet Gateway to RDS database. Scores priority at 96.4.',
      outputArtifact: 'Prioritized_Attack_Graph.json',
      sampleSnippet: `Exploit Route Discovered:
  [Internet 0.0.0.0/0] -> [IGW igw-089a] -> [SG:5432] -> [RDS prod-db]
Composite Priority Score: 96.4 / 100 [CRITICAL TIER]
Choke Point Identified: aws_security_group.public_db`,
    },
    {
      id: 'remediation',
      stepNum: '05',
      title: 'Autonomous Remediation',
      subtitle: 'Syntax-Preserving Patch',
      icon: GitPullRequest,
      color: '#34D399',
      summary: 'Synthesizes targeted code diffs that fix identified choke points without side-effects.',
      inputArtifact: 'Prioritized_Attack_Graph.json',
      action: 'Replaces wide-open 0.0.0.0/0 ingress with private VPC CIDR and enables KMS encryption at rest.',
      outputArtifact: 'remediation_patch.diff',
      sampleSnippet: `--- a/security_groups.tf
+++ b/security_groups.tf
-  cidr_blocks = ["0.0.0.0/0"]
+  cidr_blocks = [aws_vpc.main.cidr_block]`,
    },
    {
      id: 'validation',
      stepNum: '06',
      title: 'Sandbox Validation',
      subtitle: 'LocalStack Emulation & PR',
      icon: CheckCircle2,
      color: '#10B981',
      summary: 'Validates patch syntax in LocalStack sandbox and automatically creates GitHub Pull Request.',
      inputArtifact: 'remediation_patch.diff',
      action: 'Executes terraform validate & dry-run plan in LocalStack container. Verifies 0 regression errors.',
      outputArtifact: 'GitHub PR #42 (MERGE READY)',
      sampleSnippet: `[LocalStack] Initializing containerized sandbox...
[LocalStack] Running: terraform validate -> SUCCESS (0 errors)
[LocalStack] Running: cfn-lint / kics -> 0 CRITICAL FINDINGS
[GitHub] Pull Request #42 generated & signed: "fix(iac): restrict RDS ingress"`,
    },
  ]

  // Map scroll progress (0.0 to 1.0) dynamically to active stage (0 to 5)
  useEffect(() => {
    if (prefersReduced) return
    const calculatedStage = Math.min(5, Math.max(0, Math.floor(progress * 6)))
    setActiveStage(calculatedStage)
  }, [progress, prefersReduced])

  const current = stages[activeStage]
  const Icon = current.icon

  return (
    <section
      ref={sectionRef}
      className="workflow-section cinematic-scene-stage"
      id="workflow"
      aria-label="AgentShield AI Autonomous Workflow"
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
              END-TO-END AUTONOMOUS SECURITY PIPELINE
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            FROM CODE COMMIT
            <br />
            <span className="heading-gradient">TO VALIDATED FIX.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Watch the workflow progress as you scroll. Each phase operates deterministically with
            formal input/output contracts, transforming raw template inputs into validated patches.
          </motion.p>
        </div>

        {/* 6-Stage Progress Stepper Bar */}
        <div className="workflow-stepper-track">
          {stages.map((stage, idx) => {
            const StageIcon = stage.icon
            const isActive = activeStage === idx
            const isCompleted = activeStage > idx

            return (
              <div
                key={stage.id}
                onClick={() => setActiveStage(idx)}
                className={`workflow-step-node ${isActive ? 'step-active' : ''} ${
                  isCompleted ? 'step-passed' : ''
                }`}
                role="button"
                tabIndex={0}
              >
                <div
                  className="step-icon-bubble"
                  style={{
                    borderColor: isActive ? stage.color : undefined,
                    boxShadow: isActive ? `0 0 16px ${stage.color}60` : undefined,
                  }}
                >
                  <StageIcon size={16} style={{ color: isActive ? stage.color : undefined }} />
                </div>
                <div className="step-label-box">
                  <span className="step-num">{stage.stepNum}</span>
                  <span className="step-title">{stage.title}</span>
                </div>
                {idx < stages.length - 1 && (
                  <div
                    className={`step-conduit-line ${isCompleted ? 'conduit-filled' : ''}`}
                    style={{
                      background: isCompleted
                        ? `linear-gradient(90deg, ${stage.color}, ${stages[idx + 1].color})`
                        : undefined,
                    }}
                  />
                )}
              </div>
            )
          })}
        </div>

        {/* Active Stage Deep-Dive Visual Showcase */}
        <div className="workflow-active-showcase">
          <div className="showcase-left-panel">
            <div className="showcase-stage-header">
              <span className="showcase-stage-tag" style={{ color: current.color }}>
                STAGE {current.stepNum} OF 06 • {current.subtitle.toUpperCase()}
              </span>
              <h3 className="showcase-stage-title">{current.title}</h3>
              <p className="showcase-stage-summary">{current.summary}</p>
            </div>

            <div className="showcase-contract-box">
              <div className="contract-row">
                <span className="contract-key">INPUT ARTIFACT:</span>
                <span className="contract-val">{current.inputArtifact}</span>
              </div>
              <div className="contract-row">
                <span className="contract-key">TRANSFORMATION:</span>
                <span className="contract-val">{current.action}</span>
              </div>
              <div className="contract-row">
                <span className="contract-key">OUTPUT ARTIFACT:</span>
                <span className="contract-val highlight">{current.outputArtifact}</span>
              </div>
            </div>
          </div>

          <div className="showcase-right-terminal">
            <div className="terminal-header">
              <div className="terminal-dots">
                <span className="dot red" />
                <span className="dot yellow" />
                <span className="dot green" />
              </div>
              <span className="terminal-title">agentshield_pipeline_log — Stage {current.stepNum}</span>
              <Activity size={13} className="terminal-pulse" />
            </div>
            <pre className="terminal-code">
              <code>{current.sampleSnippet}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  )
}
