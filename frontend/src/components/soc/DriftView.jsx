import React, { useState } from 'react'

export default function DriftView({ onToast, onNavigate }) {
  const [isReconciling, setIsReconciling] = useState(false)
  const [driftResolved, setDriftResolved] = useState(false)

  const handleReconcile = () => {
    setIsReconciling(true)
    setTimeout(() => {
      setIsReconciling(false)
      setDriftResolved(true)
      if (onToast) onToast('Drift auto-reconciled! Live cloud state aligned with Git IaC configuration. ✓')
    }, 1200)
  }

  return (
    <div className="drift-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Live Cloud Infrastructure Drift Detection</h2>
          <p className="scc-subtitle">
            Continuous reconciliation between Git-defined IaC templates and runtime AWS/Azure/GCP cloud API state.
          </p>
        </div>
      </div>

      {/* Desired vs Actual Visualizer */}
      <div className="drift-state-comparison">
        {/* Left: IaC State (Git / Terraform) */}
        <div>
          <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
            DESIRED (GIT IAC STATE)
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit', marginTop: '6px' }}>
            S3 BUCKET PRIVATE
          </div>
          <div style={{ fontSize: '12px', color: '#22C55E', fontFamily: 'JetBrains Mono', marginTop: '4px' }}>
            ✓ public_access_block = true
          </div>
          <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '6px' }}>
            Source: <code style={{ color: '#D6A84F' }}>git://terraform/storage.tf</code>
          </div>
        </div>

        {/* Center: Drift Alert Indicator */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <div className="drift-badge-alert">
            {driftResolved ? '✓ DRIFT RECONCILED' : '⚠ DRIFT DETECTED'}
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
            {driftResolved ? 'State synchronized' : 'Detected 14m ago by Agent 07'}
          </div>
        </div>

        {/* Right: Live Cloud (Runtime API) */}
        <div>
          <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', textTransform: 'uppercase' }}>
            ACTUAL (LIVE CLOUD API)
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: driftResolved ? '#22C55E' : '#EF4444', fontFamily: 'Outfit', marginTop: '6px' }}>
            {driftResolved ? 'S3 BUCKET PRIVATE' : 'S3 BUCKET PUBLIC'}
          </div>
          <div style={{ fontSize: '12px', color: driftResolved ? '#22C55E' : '#EF4444', fontFamily: 'JetBrains Mono', marginTop: '4px' }}>
            {driftResolved ? '✓ public_access_block = true' : '✕ public_access_block = false'}
          </div>
          <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '6px' }}>
            Provider: <code style={{ color: '#D6A84F' }}>AWS us-east-1 · arn:aws:s3:::prod-customer-data</code>
          </div>
        </div>
      </div>

      {/* Detailed Diff Comparison Card */}
      <div className="scc-panel-card">
        <div className="scc-panel-head">
          <div className="scc-panel-title">
            <span>Drift Analysis: aws_s3_bucket.prod_customer_data</span>
          </div>
          <span style={{ fontSize: '11px', color: '#D6A84F', fontFamily: 'JetBrains Mono' }}>
            OUT-OF-BAND MODIFICATION DETECTED
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          <div style={{ background: '#040609', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: '#22C55E', fontFamily: 'JetBrains Mono', marginBottom: '8px' }}>
              EXPECTED CONFIGURATION (IAC)
            </div>
            <pre style={{ margin: 0, fontFamily: 'JetBrains Mono', fontSize: '12px', color: '#86EFAC', lineHeight: '1.5' }}>
{`resource "aws_s3_bucket" "prod_customer_data" {
  bucket = "prod-customer-data"
  acl    = "private"

  public_access_block {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
}`}
            </pre>
          </div>

          <div style={{ background: '#040609', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: '#EF4444', fontFamily: 'JetBrains Mono', marginBottom: '8px' }}>
              ACTUAL LIVE STATE (AWS API)
            </div>
            <pre style={{ margin: 0, fontFamily: 'JetBrains Mono', fontSize: '12px', color: '#FCA5A5', lineHeight: '1.5' }}>
{`resource "aws_s3_bucket" "prod_customer_data" {
  bucket = "prod-customer-data"
  acl    = "public-read"  # ⚠️ Out-of-band edit via AWS Console!

  # Missing public_access_block configuration
  # Modified by IAM user 'dev-ops-admin'
}`}
            </pre>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '18px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '16px' }}>
          <button
            className="soc-back-home-btn"
            onClick={() => onNavigate('remediation')}
          >
            🔍 View Remediated Diff
          </button>
          <button
            className="btn-start-analysis"
            style={{ padding: '9px 20px', fontSize: '13px' }}
            onClick={handleReconcile}
            disabled={isReconciling || driftResolved}
          >
            {isReconciling ? 'Reconciling State...' : driftResolved ? '✓ State Reconciled' : '⚡ Auto-Reconcile to Git IaC →'}
          </button>
        </div>
      </div>
    </div>
  )
}
