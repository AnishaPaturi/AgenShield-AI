import { useState, useRef } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import {
  GitPullRequest,
  CheckCircle2,
  Terminal,
  ShieldCheck,
  FileCode2,
  ArrowRight,
  ExternalLink,
  Layers,
  Sparkles,
} from 'lucide-react'
import useScrollProgress from '../../hooks/useScrollProgress'

export default function RemediationSection() {
  const sectionRef = useRef(null)
  const prefersReduced = useReducedMotion()
  const { progress } = useScrollProgress(sectionRef)
  const [activeTab, setActiveTab] = useState(0)

  // Scroll phase calculations:
  // Step 1: Finding revealed (>= 0.12)
  // Step 2: Proposal diff rendered (>= 0.35)
  // Step 3: Sandbox container runs (>= 0.58)
  // Step 4: Validation result 100% pass (>= 0.75)
  // Step 5: Validated PR ready (>= 0.86)
  const isFinding = progress >= 0.1 || prefersReduced
  const isProposal = progress >= 0.32 || prefersReduced
  const isSandbox = progress >= 0.55 || prefersReduced
  const isResult = progress >= 0.72 || prefersReduced
  const isPrReady = progress >= 0.84 || prefersReduced

  const remediations = [
    {
      id: 'rem-sg',
      title: 'PostgreSQL Ingress Remediation',
      finding: 'CKV_AWS_20: Security group allows ingress from 0.0.0.0/0 on Port 5432',
      file: 'modules/database/security_groups.tf',
      oldCode: `resource "aws_security_group" "db_sg" {
  name        = "prod-postgres-sg"
  description = "Production Database Ingress"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Flagged: Wide Open
  }
}`,
      newCode: `resource "aws_security_group" "db_sg" {
  name        = "prod-postgres-sg"
  description = "Production Database Ingress (Restricted)"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block] # Restricted to Internal VPC
  }
}`,
      terminalLogs: `[LocalStack] Spawning containerized sandbox: localstack/localstack:latest
[LocalStack] Initializing backend state in RAM...
[LocalStack] Executing: terraform init -backend=false
[LocalStack] Executing: terraform validate
Success! The configuration is valid (0 errors, 0 warnings).
[LocalStack] Executing: tflint --module
TFLint verification completed: 0 issues found.
[LocalStack] Dry-run plan: 0 resources destroyed, 1 in-place update.
[LocalStack] Regression Assessment: ZERO runtime side-effects detected.`,
      prTitle: 'fix(security): restrict RDS PostgreSQL ingress to VPC CIDR (#42)',
    },
    {
      id: 'rem-s3',
      title: 'S3 Data Lake Encryption & Bucket Policy',
      finding: 'CKV_AWS_19: S3 bucket does not enforce server-side encryption at rest with KMS',
      file: 'modules/storage/s3_datalake.tf',
      oldCode: `resource "aws_s3_bucket" "lake" {
  bucket = "prod-corp-analytics-lake"
  acl    = "public-read" # Flagged: Public ACL
}`,
      newCode: `resource "aws_s3_bucket" "lake" {
  bucket = "prod-corp-analytics-lake"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake_kms" {
  bucket = aws_s3_bucket.lake.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.analytics_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lake_block" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}`,
      terminalLogs: `[LocalStack] Validating S3 Bucket KMS Encryption Configuration...
[LocalStack] Mocking AWS KMS Master Key: arn:aws:kms:us-east-1:000000000000:key/...
[LocalStack] Executing: terraform validate
Success! Configuration syntax valid.
[LocalStack] Executing checkov compliance re-scan...
Passed: CKV_AWS_19 (S3 SSE-KMS Enabled)
Passed: CKV_AWS_53 (Block Public ACLs Enabled)
[LocalStack] 100% Policy Compliance Re-verified.`,
      prTitle: 'fix(s3): enforce KMS encryption & block public access for analytics lake (#43)',
    },
  ]

  const current = remediations[activeTab]

  return (
    <section
      ref={sectionRef}
      className="remediation-section cinematic-scene-stage"
      id="remediation"
      aria-label="Automated Sandbox Remediation Engine"
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
              CONTAINERIZED SANDBOX VERIFICATION
            </span>
          </motion.div>

          <motion.h2
            className="section-main-heading"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            AUTOMATED REMEDIATION.
            <br />
            <span className="heading-gradient">ZERO PRODUCTION REGRESSION.</span>
          </motion.h2>

          <motion.p
            className="section-subheading"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: false, amount: 0.2 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            AI-generated patches that break CI/CD pipelines are worse than vulnerabilities.
            AgentShield tests every patch inside a LocalStack container sandbox before creating
            a cryptographic, merge-ready pull request.
          </motion.p>

          {/* Remediation Process Breadcrumb */}
          <div className="remediation-process-strip">
            <span className={`rem-step-pill ${isFinding ? 'active' : ''}`}>1. FINDING</span>
            <span className="rem-step-arrow">→</span>
            <span className={`rem-step-pill ${isProposal ? 'active' : ''}`}>2. REMEDIATION PROPOSAL</span>
            <span className="rem-step-arrow">→</span>
            <span className={`rem-step-pill ${isSandbox ? 'active' : ''}`}>3. SANDBOX VALIDATION</span>
            <span className="rem-step-arrow">→</span>
            <span className={`rem-step-pill ${isResult ? 'active' : ''}`}>4. VALIDATION RESULT</span>
            <span className="rem-step-arrow">→</span>
            <span className={`rem-step-pill ${isPrReady ? 'active' : ''}`}>5. VALIDATED PR</span>
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="remediation-tabs">
          {remediations.map((rem, idx) => (
            <button
              key={rem.id}
              type="button"
              onClick={() => setActiveTab(idx)}
              className={`rem-tab-btn ${activeTab === idx ? 'active' : ''}`}
            >
              <FileCode2 size={15} />
              <span>{rem.title}</span>
            </button>
          ))}
        </div>

        {/* Main Remediation Visual Studio Canvas */}
        <div className="remediation-studio-canvas">
          {/* Finding Strip */}
          <div className={`remediation-finding-banner ${isFinding ? 'banner-revealed' : ''}`}>
            <span className="finding-flag-badge">SECURITY FINDING</span>
            <span className="finding-file-path">{current.file}</span>
            <span className="finding-detail-text">{current.finding}</span>
          </div>

          {/* Split Code Diff Studio: Vulnerable vs Remediated */}
          <div className={`remediation-diff-grid ${isProposal ? 'diff-revealed' : ''}`}>
            {/* Left: Original Vulnerable Code */}
            <div className="diff-pane original-pane">
              <div className="pane-header">
                <span className="pane-badge red">BEFORE: VULNERABLE</span>
                <span className="pane-filename">{current.file}</span>
              </div>
              <pre className="diff-code-block original">
                <code>{current.oldCode}</code>
              </pre>
            </div>

            {/* Right: AgentShield Synthesized Patch */}
            <div className="diff-pane remediated-pane">
              <div className="pane-header">
                <span className="pane-badge green">AFTER: SYNTHESIZED FIX</span>
                <span className="pane-filename">{current.file}</span>
              </div>
              <pre className="diff-code-block remediated">
                <code>{current.newCode}</code>
              </pre>
            </div>
          </div>

          {/* Sandbox Terminal & Validation Logs (Reveals in Step 3 & 4) */}
          <div className={`sandbox-terminal-drawer ${isSandbox ? 'terminal-open' : ''}`}>
            <div className="sandbox-terminal-bar">
              <div className="terminal-dots">
                <span className="dot red" />
                <span className="dot yellow" />
                <span className="dot green" />
              </div>
              <span className="sandbox-terminal-title">
                <Terminal size={14} className="sandbox-icon" />
                LocalStack Sandbox Container [localstack/localstack:latest]
              </span>
              <span className={`sandbox-status-tag ${isResult ? 'verified' : 'testing'}`}>
                {isResult ? 'VERIFICATION: 100% PASSED' : 'EXECUTING DRY RUN...'}
              </span>
            </div>
            <pre className="sandbox-log-stream">
              <code>{current.terminalLogs}</code>
            </pre>
          </div>

          {/* Validated Pull Request Banner (Reveals in Step 5) */}
          <div className={`validated-pr-footer ${isPrReady ? 'pr-revealed' : ''}`}>
            <div className="pr-footer-left">
              <GitPullRequest size={22} className="pr-git-icon" />
              <div>
                <span className="pr-badge">GITHUB PULL REQUEST READY</span>
                <h4 className="pr-headline">{current.prTitle}</h4>
              </div>
            </div>
            <div className="pr-footer-right">
              <span className="pr-stat-item">
                <CheckCircle2 size={15} className="check-icon" />
                0 Syntax Regressions
              </span>
              <span className="pr-stat-item">
                <ShieldCheck size={15} className="check-icon" />
                KMS Verified
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
