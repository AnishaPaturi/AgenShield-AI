import { motion, useReducedMotion } from 'framer-motion'
import FeatureCard from './FeatureCard'

export default function FeatureSection() {
  const prefersReduced = useReducedMotion()

  const featuresData = [
    {
      id: 'iac-ast',
      title: 'Polyglot IaC AST Parsing',
      category: 'Static Representation',
      iconKey: 'iac',
      engine: 'HCL2 / CFN / K8s / Helm',
      description:
        'Extracts structured Abstract Syntax Trees across Terraform, CloudFormation, Kubernetes YAML, and Helm charts. Pre-resolves dynamic locals, parameters, and variable references before reasoning begins.',
      mechanism: 'Dynamic AST Pre-Evaluation',
      metric: '4 Polyglot Formats',
      size: 'large',
      direction: 'bottom',
      codeLabel: 'HCL AST Normalization',
      codePreview: `resource "aws_s3_bucket" "lake" {
  bucket = "\${var.prefix}-data-\${local.env}"
  # Pre-resolved AST -> "prod-data-lake"
  acl    = "public-read" # Flagged AS-AWS-001
}`,
      spec: 'Eliminates parsing ambiguity for dynamic IaC',
    },
    {
      id: 'secrets',
      title: 'Zero-Leakage Secret Interception',
      category: 'Credential Safeguard',
      iconKey: 'secrets',
      engine: 'Gitleaks + TruffleHog + Shannon Entropy',
      description:
        'Intercepts exposed API keys, private RSA certificates, AWS secret tokens, and high-entropy strings, cryptographically masking credentials locally before any template payload is evaluated by LLMs.',
      mechanism: 'High-Entropy Regex + Cryptographic Masking',
      metric: '0 Credentials Sent to Cloud LLMs',
      size: 'normal',
      direction: 'left',
      spec: 'Local redaction prior to prompt ingestion',
    },
    {
      id: 'analyst-ensemble',
      title: 'Multi-LLM Ensemble Voting',
      category: 'Semantic Analysis',
      iconKey: 'analyst',
      engine: 'Claude 3.5 Sonnet + OpenAI GPT-4o',
      description:
        'Executes dual-model parallel reasoning with Chain-of-Thought prompting and Platt-calibrated consensus scoring. Suppresses single-model hallucinations and routes ambiguous findings (C < 0.85) to human triage.',
      mechanism: 'Platt Temperature Scaling Logit Consensus',
      metric: '<3% Hallucination Rate',
      size: 'large',
      direction: 'bottom',
      codeLabel: 'Consensus Agreement Engine',
      codePreview: `C_ensemble = Σ w_i * C(M_i) + γ * S_agreement * (N_agreed / N_total)
# Auto-patch threshold: C >= 0.85
# Disagreement or C < 0.85 -> Human Review Queue`,
      spec: 'Mathematical hallucination suppression',
    },
    {
      id: 'attack-path',
      title: 'Attack-Path Intelligence',
      category: 'Contextual Topology',
      iconKey: 'attackpath',
      engine: 'ResourceGraph BFS Exploit Traversal',
      description:
        'Constructs resource topological dependency graphs from IaC references. Analyzes exploit routes from perimeter ingress (Internet Gateways, public ALBs, 0.0.0.0/0 Security Groups) to high-value internal databases and admin roles.',
      mechanism: 'Topological Ingress-to-Asset Route Discovery',
      metric: 'Automated Choke Point Detection',
      size: 'large',
      direction: 'right',
      codeLabel: 'Discovered Attack Path Route',
      codePreview: `[Internet] ──> (IGW: igw-01a)
       └──> (SG: 0.0.0.0/0 : 5432)
              └──> [RDS: prod-postgres-db]
                     └──> (IAM: AssumeRole Admin)`,
      spec: 'Multi-hop exposure graph modeling',
    },
    {
      id: 'blast-radius',
      title: 'Blast-Radius Assessment',
      category: 'Impact Scoring',
      iconKey: 'blastradius',
      engine: 'Cascade Dependency Reachability',
      description:
        'Quantifies downstream blast radius across compute instances, databases, storage buckets, and IAM roles. Distinguishes isolated issues from misconfigurations that jeopardize an entire cloud estate.',
      mechanism: 'Breadth-First Transitive Reachability',
      metric: 'Categorized Asset Impact',
      size: 'normal',
      direction: 'left',
      spec: 'Quantifies downstream cascade exposure',
    },
    {
      id: 'prioritization',
      title: 'Composite Risk Prioritization',
      category: 'Triage Intelligence',
      iconKey: 'prioritize',
      engine: 'Composite Formula Engine',
      description:
        'Calculates unified risk priority scores (0–100) combining base vulnerability severity (50%), topological exposure (30%), and blast radius impact (20%), calibrated by multi-model ensemble confidence.',
      mechanism: 'Priority = (0.5*S + 0.3*E + 0.2*B) * (0.5 + 0.5*C)',
      metric: 'CRITICAL / HIGH / MED / LOW',
      size: 'normal',
      direction: 'bottom',
      spec: 'Actionable ranking eliminating alert fatigue',
    },
    {
      id: 'remediation',
      title: 'Automated Unified Diff Patches',
      category: 'Remediation Synthesis',
      iconKey: 'remediation',
      engine: 'Targeted Code Diff Synthesizer',
      description:
        'Synthesizes clean, executable unified diff patches directly targeting specific IaC resource blocks. Replaces conversational text suggestions with immediately mergeable code.',
      mechanism: 'Unified Git Patch Generation',
      metric: 'Resource-Level Precision',
      size: 'normal',
      direction: 'right',
      spec: 'Ready for Git pull requests and pre-commit hooks',
    },
    {
      id: 'sandbox-validation',
      title: 'LocalStack Sandbox Validation',
      category: 'Runtime Integrity',
      iconKey: 'sandbox',
      engine: 'Linters + LocalStack Dry-Run',
      description:
        'Two-tier validation pipeline: static linters (terraform validate, cfn-lint, kube-linter) followed by containerized runtime dry-run deployment inside LocalStack to verify patch syntax and provision integrity.',
      mechanism: 'Pre-Deployment Emulated Provisioning',
      metric: '100% Patch Syntax Validity',
      size: 'large',
      direction: 'bottom',
      codeLabel: 'Validation Harness Gate',
      codePreview: `1. Syntax Check: terraform validate -> PASS [OK]
2. Linter Check: tflint / cfn-lint    -> PASS [OK]
3. Dry-Run Test: LocalStack Deploy    -> PASS [OK]
Result: Patch authorized for automated merge.`,
      spec: 'Automated rollback on linter or dry-run failure',
    },
  ]

  return (
    <section className="features-section" id="features" aria-label="Key Features">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-block text-center">
          <motion.div
            className="section-eyebrow-wrapper"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <span className="section-eyebrow">
              <span className="eyebrow-accent-dot" />
              CORE ARCHITECTURAL CAPABILITIES
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            SECURITY BEYOND
            <br />
            <span className="heading-gradient">CONFIGURATION CHECKS.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Traditional scanners check isolated lines of code against static regex rules.
            AgentShield AI reconstructs resource topology, intercepts credentials, executes
            multi-LLM consensus, and validates generated patches inside a local runtime sandbox.
          </motion.p>
        </div>

        {/* Asymmetric Bento / Feature Cards Grid */}
        <div className="features-asymmetric-grid">
          {featuresData.map((feature, idx) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              index={idx}
              size={feature.size}
              direction={feature.direction}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
