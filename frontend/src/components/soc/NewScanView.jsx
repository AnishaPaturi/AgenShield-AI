import React, { useRef, useState } from 'react'
import { Shield } from 'lucide-react'

const SAMPLES = {
  aws: {
    name: 'sample-aws-infra.tf',
    content: `resource "aws_s3_bucket" "data_bucket" {
  bucket = "enterprise-app-data-bucket"
}

resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Allow web and SSH traffic"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "app_db" {
  identifier          = "app-database"
  engine              = "postgres"
  storage_encrypted   = false
  publicly_accessible = true
}
`,
  },
  azure: {
    name: 'azure-nsg-insecure.json',
    content: `{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Network/networkSecurityGroups",
      "apiVersion": "2020-11-01",
      "name": "insecure-nsg",
      "location": "eastus",
      "properties": {
        "securityRules": [
          {
            "name": "allow-all-inbound",
            "properties": {
              "protocol": "*",
              "sourceAddressPrefix": "*",
              "destinationPortRange": "*",
              "access": "Allow",
              "direction": "Inbound"
            }
          }
        ]
      }
    }
  ]
}`,
  },
  k8s: {
    name: 'k8s-privileged-pod.yaml',
    content: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: insecure-workload
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: app
        image: nginx:latest
        securityContext:
          privileged: true
          allowPrivilegeEscalation: true
          readOnlyRootFilesystem: false
`,
  },
}

export default function NewScanView({ onScan, scanning, onNavigate }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [cloudTarget, setCloudTarget] = useState('AWS')
  const [scanMode, setScanMode] = useState('full')
  const [errorMsg, setErrorMsg] = useState(null)
  const inputRef = useRef(null)

  const allowedExtensions = ['.tf', '.yaml', '.yml', '.json', '.template', '.tgz']
  const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB limit

  const handlePick = (f) => {
    setErrorMsg(null)
    if (!f) return

    const lowerName = (f.name || '').toLowerCase()
    const hasValidExt = allowedExtensions.some((ext) => lowerName.endsWith(ext))
    if (!hasValidExt) {
      setErrorMsg(`Invalid file type (${f.name}). Supported formats: .tf, .yaml, .yml, .json, .template`)
      return
    }

    if (f.size > MAX_FILE_SIZE) {
      setErrorMsg(`File size (${(f.size / (1024 * 1024)).toFixed(2)} MB) exceeds maximum allowed limit of 5 MB.`)
      return
    }

    setFile(f)
  }

  const handleRemoveFile = (e) => {
    e.stopPropagation()
    setFile(null)
    setErrorMsg(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleLoadSample = (sampleKey, defaultCloud) => {
    setErrorMsg(null)
    const sample = SAMPLES[sampleKey]
    if (!sample) return
    const blob = new Blob([sample.content], { type: 'text/plain' })
    const sampleFile = new File([blob], sample.name, { type: 'text/plain' })
    setFile(sampleFile)
    setCloudTarget(defaultCloud)
  }

  const handleStartScan = () => {
    if (!file) {
      inputRef.current?.click()
      return
    }
    if (onScan) {
      onScan(file, { cloud: cloudTarget, mode: scanMode })
    }
  }

  return (
    <div className="newscan-view">
      {/* Hero */}
      <div className="newscan-hero">
        <h2>Secure your infrastructure before it reaches production.</h2>
        <p>
          Analyze Terraform, CloudFormation, Kubernetes and Helm configurations using autonomous
          AI security agents with runtime LocalStack sandbox verification.
        </p>
      </div>

      {/* Quick Sample Template Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
        <span style={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: '#64748B' }}>TEST TEMPLATES:</span>
        <button
          type="button"
          className="tab-btn"
          style={{ fontSize: '11px', padding: '4px 10px' }}
          onClick={() => handleLoadSample('aws', 'AWS')}
        >
          ☁ AWS Insecure S3 &amp; RDS (.tf)
        </button>
        <button
          type="button"
          className="tab-btn"
          style={{ fontSize: '11px', padding: '4px 10px' }}
          onClick={() => handleLoadSample('azure', 'Azure')}
        >
          ☁ Azure Open NSG (.json)
        </button>
        <button
          type="button"
          className="tab-btn"
          style={{ fontSize: '11px', padding: '4px 10px' }}
          onClick={() => handleLoadSample('k8s', 'AWS')}
        >
          ⎈ K8s Privileged Pod (.yaml)
        </button>
      </div>

      {/* Error Notice */}
      {errorMsg && (
        <div className="auth-feedback-box error" style={{ maxWidth: '600px', margin: '0 auto 16px', textAlign: 'center' }}>
          <span>⚠ {errorMsg}</span>
        </div>
      )}

      {/* Huge Dropzone */}
      <div
        className={`huge-dropzone ${dragging ? 'drag-active' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          if (e.dataTransfer.files.length) handlePick(e.dataTransfer.files[0])
        }}
      >
        <div className="huge-dropzone-icon">⬆</div>
        <div className="huge-dropzone-title">DROP IaC FILES HERE</div>
        <div className="huge-dropzone-sub">or click to browse from your computer (Max 5MB)</div>

        <div className="iac-format-pills">
          <span className="iac-pill">Terraform (.tf)</span>
          <span className="iac-pill">CloudFormation (.yaml / .json)</span>
          <span className="iac-pill">Kubernetes (.yaml)</span>
          <span className="iac-pill">Helm (values.yaml / chart)</span>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".tf,.yaml,.yml,.json,.template,.tgz"
          onChange={(e) => handlePick(e.target.files[0])}
        />
      </div>

      {/* Selected File Notice & Controls */}
      {file && (
        <div
          className="filename"
          style={{
            margin: '12px auto 0',
            maxWidth: '560px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 18px',
            background: 'var(--primary-dim, rgba(225, 29, 72, 0.08))',
            border: '1px solid var(--primary-border, rgba(225, 29, 72, 0.3))',
            borderRadius: '10px',
            boxShadow: '0 4px 16px var(--primary-glow, rgba(225, 29, 72, 0.12))',
          }}
        >
          <div>
            <span style={{ color: 'var(--text-muted, #94A3B8)', fontSize: '11px', textTransform: 'uppercase', display: 'block', letterSpacing: '0.04em' }}>
              Selected Template Ready for Agent Triage:
            </span>
            <span style={{ fontWeight: 600, color: 'var(--text, #FFFFFF)' }}>{file.name}</span>
            <span style={{ color: 'var(--muted, #64748B)', fontSize: '12px', marginLeft: '8px' }}>
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="soc-back-home-btn"
              style={{ padding: '4px 12px', fontSize: '11px' }}
              onClick={(e) => {
                e.stopPropagation()
                inputRef.current?.click()
              }}
            >
              Replace
            </button>
            <button
              type="button"
              className="soc-back-home-btn text-danger"
              style={{ padding: '4px 12px', fontSize: '11px' }}
              onClick={handleRemoveFile}
            >
              Remove
            </button>
          </div>
        </div>
      )}

      {/* Options: Cloud Target & Scan Mode */}
      <div className="newscan-options-card">
        <div>
          <div className="control-section-title">Cloud Target</div>
          <div className="cloud-target-pills">
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'AWS' ? 'active' : ''}`}
              onClick={() => setCloudTarget('AWS')}
            >
              <span>☁</span> AWS
            </button>
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'Azure' ? 'active' : ''}`}
              onClick={() => setCloudTarget('Azure')}
            >
              <span>☁</span> Azure
            </button>
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'GCP' ? 'active' : ''}`}
              onClick={() => setCloudTarget('GCP')}
            >
              <span>☁</span> GCP
            </button>
          </div>
        </div>

        <div>
          <div className="control-section-title">Scan Mode</div>
          <div className="scan-mode-radio-group">
            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="quick"
                checked={scanMode === 'quick'}
                onChange={() => setScanMode('quick')}
              />
              <span className="scan-mode-title">Quick Scan</span>
              <span className="scan-mode-desc">— Static AST syntax & secret scanner validation (Fastest, ~300ms)</span>
            </label>

            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="full"
                checked={scanMode === 'full'}
                onChange={() => setScanMode('full')}
              />
              <span className="scan-mode-title">Full AgentShield Analysis (Recommended)</span>
              <span className="scan-mode-desc">
                — 8 coordinated agents: AST, Secrets, RAG, Dual-LLM Consensus, Diff Synthesis & LocalStack Sandbox
              </span>
            </label>

            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="compliance"
                checked={scanMode === 'compliance'}
                onChange={() => setScanMode('compliance')}
              />
              <span className="scan-mode-title">Compliance Audit</span>
              <span className="scan-mode-desc">— SOC 2, HIPAA, PCI-DSS, and NIST 800-53 benchmark enforcement</span>
            </label>
          </div>
        </div>

        {/* Start Security Analysis CTA */}
        <button
          className="btn-start-analysis"
          onClick={handleStartScan}
          disabled={scanning}
        >
          {scanning ? (
            <>
              <span className="spinner"></span>
              Orchestrating 8 AI Agents...
            </>
          ) : (
            'START SECURITY ANALYSIS →'
          )}
        </button>

        {/* Data Retention & Sandbox Governance Notice (Item 23) */}
        <div style={{
          marginTop: '16px',
          padding: '10px 14px',
          background: 'var(--surface-2-glass, rgba(20, 26, 45, 0.4))',
          border: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.05))',
          borderRadius: '8px',
          fontSize: '11.5px',
          color: 'var(--text-muted, #94A3B8)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          lineHeight: '1.4'
        }}>
          <Shield size={14} color="var(--primary, #E11D48)" style={{ flexShrink: 0 }} />
          <span>
            <strong>Ephemeral Sandbox Guarantee:</strong> Uploaded IaC definitions are parsed and analyzed in ephemeral memory and isolated sandboxes. Templates are never stored externally or used to train public foundation models. Read our <a href="/privacy" style={{ color: 'var(--primary, #E11D48)', textDecoration: 'underline' }}>Privacy Policy</a>.
          </span>
        </div>
      </div>
    </div>
  )
}
