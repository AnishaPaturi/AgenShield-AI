import React, { useState } from 'react'

export default function RemediationView({ onDecide, onToast }) {
  const [patchStatus, setPatchStatus] = useState('PENDING')

  const handleApply = () => {
    setPatchStatus('APPLIED')
    if (onToast) onToast('Patch successfully applied & verified in LocalStack sandbox! ✓')
  }

  const handleReject = () => {
    setPatchStatus('REJECTED')
    if (onToast) onToast('Patch marked as rejected by security engineer.')
  }

  return (
    <div className="remediation-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Code + AI Remediation Workbench</h2>
          <p className="scc-subtitle">
            Executable Git diff patch synthesized by Remediation Agent with dual-stage linter &amp; LocalStack sandbox verification.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className={`status-tag ${patchStatus}`}>{patchStatus}</span>
        </div>
      </div>

      {/* Split Screen: BEFORE vs AFTER */}
      <div className="remediation-split">
        {/* Left: BEFORE (Vulnerable) */}
        <div className="code-pane">
          <div className="code-pane-header">
            <span style={{ color: '#FCA5A5' }}>● BEFORE (Vulnerable Code)</span>
            <span style={{ color: '#64748B' }}>main.tf · Lines 14-22</span>
          </div>
          <pre className="code-pane-body">
{`# Vulnerable S3 Bucket Definition (Unblocked Public ACL)
resource "aws_s3_bucket" "prod_customer_data" {
  bucket = "prod-customer-data-lake-2026"
  acl    = "public-read"  # ⚠️ CRITICAL: World Readable

  tags = {
    Environment = "production"
    Department  = "finance"
  }
}
`}
          </pre>
        </div>

        {/* Right: AFTER (Remediated) */}
        <div className="code-pane">
          <div className="code-pane-header">
            <span style={{ color: '#86EFAC' }}>● AFTER (AgentShield Remediated Patch)</span>
            <span style={{ color: '#D6A84F' }}>Synthesized by Agent 06</span>
          </div>
          <pre className="code-pane-body">
{`# Remediated S3 Bucket with Enforced Zero-Trust Access Block
resource "aws_s3_bucket" "prod_customer_data" {
  bucket = "prod-customer-data-lake-2026"
`}
<span className="diff-line-del">{`-  acl    = "public-read"`}</span>
<span className="diff-line-add">{`+  acl    = "private"`}</span>
{`
  tags = {
    Environment = "production"
    Department  = "finance"
  }
}

`}
<span className="diff-line-add">{`+resource "aws_s3_bucket_public_access_block" "prod_customer_data_block" {`}</span>
<span className="diff-line-add">{`+  bucket = aws_s3_bucket.prod_customer_data.id`}</span>
<span className="diff-line-add">{`+`}</span>
<span className="diff-line-add">{`+  block_public_acls       = true`}</span>
<span className="diff-line-add">{`+  block_public_policy     = true`}</span>
<span className="diff-line-add">{`+  ignore_public_acls      = true`}</span>
<span className="diff-line-add">{`+  restrict_public_buckets = true`}</span>
<span className="diff-line-add">{`+}`}</span>
          </pre>
        </div>
      </div>

      {/* AI Remediation Analysis Checklist */}
      <div className="ai-remediation-checklist">
        <div style={{ fontFamily: 'Outfit', fontSize: '15px', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
          AI Remediation Automated Verification Checklist
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          <div className="check-item">
            <span>✓</span> Syntax validation (HCL2 Tree-Sitter AST clean)
          </div>
          <div className="check-item">
            <span>✓</span> Terraform validation (terraform validate exit 0)
          </div>
          <div className="check-item">
            <span>✓</span> Security policy check (0 new regressions / CVEs)
          </div>
          <div className="check-item">
            <span>✓</span> Sandbox runtime test (LocalStack AWS dry-run passed)
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ fontSize: '12.5px', color: '#94A3B8' }}>
          Patch ID: <code style={{ color: '#D6A84F' }}>patch-s3-prod-001</code> · Model: Claude 3.5 Sonnet + Validator
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            className="soc-back-home-btn"
            style={{ padding: '10px 20px', fontSize: '13px' }}
            onClick={handleReject}
          >
            ✕ Reject Patch
          </button>
          <button
            className="btn-start-analysis"
            style={{ padding: '10px 24px', fontSize: '13.5px' }}
            onClick={handleApply}
          >
            ✓ Apply &amp; Commit Patch →
          </button>
        </div>
      </div>
    </div>
  )
}
